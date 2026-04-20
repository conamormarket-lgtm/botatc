const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');

const app = express();
app.use(express.json());

const PORT = 3000;
const LINE_ID = "qr_ventas_1";

let sock;
let currentQR = "";
let isConnected = false;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`🌐 WhatsApp Web v${version.join('.')} (Última: ${isLatest})`);

    sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: "silent" }),
        browser: ["Ubuntu", "Chrome", "20.0.04"]
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            currentQR = qr;
            console.log('📱 Nuevo QR generado — listo para escanear.');
        }

        if (connection === 'close') {
            isConnected = false;
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Conexión cerrada. Código:', statusCode, '-', lastDisconnect?.error?.message);
            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 3000);
            }
        } else if (connection === 'open') {
            isConnected = true;
            currentQR = "";
            console.log('✅ Dispositivo conectado con éxito!');
        }
    });

    // DEBUG: Escuchar TODOS los eventos para ver qué llega
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log(`[DEBUG] messages.upsert disparado. type='${type}', cantidad=${messages.length}`);

        // Aceptar 'notify' (mensajes nuevos en vivo) Y 'append' (mensajes al reconectar)
        if (type !== 'notify' && type !== 'append') {
            console.log(`[DEBUG] Tipo '${type}' descartado.`);
            return;
        }
        
        for (let m of messages) {
            console.log(`[DEBUG] Mensaje: fromMe=${m.key.fromMe}, jid=${m.key.remoteJid}`);
            if (m.key.fromMe || m.key.remoteJid === 'status@broadcast') {
                console.log('[DEBUG] Saltando (fromMe o broadcast)');
                continue;
            }
            
            try {
                const wa_id = m.key.remoteJid.split('@')[0];
                const msg_id = m.key.id;
                const timestamp = m.messageTimestamp || Math.floor(Date.now() / 1000);
                const pushName = m.pushName || "Usuario";
                
                let msgType = "unknown";
                let textBody = "";
                let mimeType = "";

                const msgTypeKey = Object.keys(m.message || {})[0];
                console.log(`[DEBUG] msgTypeKey='${msgTypeKey}' de ${wa_id}`);
                if (!msgTypeKey) {
                    console.log('[DEBUG] Sin tipo de mensaje, saltando.');
                    continue;
                }
                
                if (msgTypeKey === 'conversation' || msgTypeKey === 'extendedTextMessage') {
                    msgType = 'text';
                    textBody = m.message.conversation || m.message.extendedTextMessage?.text || "";
                } else if (msgTypeKey === 'imageMessage') {
                    msgType = 'image';
                    textBody = m.message.imageMessage?.caption || "";
                    mimeType = m.message.imageMessage?.mimetype || "image/jpeg";
                } else if (msgTypeKey === 'videoMessage') {
                    msgType = 'video';
                    textBody = m.message.videoMessage?.caption || "";
                    mimeType = m.message.videoMessage?.mimetype || "video/mp4";
                } else if (msgTypeKey === 'audioMessage') {
                    msgType = 'audio';
                    mimeType = m.message.audioMessage?.mimetype || "audio/ogg";
                } else if (msgTypeKey === 'documentMessage') {
                    msgType = 'document';
                    textBody = m.message.documentMessage?.fileName || "";
                }
                
                if (msgType === "unknown") {
                    console.log(`[DEBUG] Tipo desconocido '${msgTypeKey}', saltando.`);
                    continue;
                }

                // Construimos payload fingiendo ser Meta
                const metaPayload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "BAILEYS_MOCK",
                        "changes": [{
                            "value": {
                                "metadata": { "display_phone_number": LINE_ID, "phone_number_id": LINE_ID },
                                "contacts": [{ "profile": { "name": pushName }, "wa_id": wa_id }],
                                "messages": [{
                                    "from": wa_id,
                                    "id": msg_id,
                                    "timestamp": timestamp,
                                    "type": msgType,
                                    [msgType]: (msgType === 'text') ? { "body": textBody } : { "caption": textBody, "mime_type": mimeType }
                                }]
                            }
                        }]
                    }]
                };

                console.log(`➡️ Reenviando msj de ${wa_id} (${msgType}: '${textBody}') al CRM Python...`);
                const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 5000 });
                console.log(`[DEBUG] Respuesta Python: ${resp.status} - ${JSON.stringify(resp.data)}`);
                
            } catch (err) {
                console.log("❌ Error procesando mensaje de Baileys:", err.message);
                if (err.response) {
                    console.log("[DEBUG] Respuesta de error Python:", err.response.status, err.response.data);
                }
            }
        }
    });

}

// ----------------------------------------
// ENDPOINTS PARA EL PANEL ADMINISTRATIVO
// ----------------------------------------

// Estado de conexión de la línea QR
app.get('/api/qr/status', (req, res) => {
    res.json({ connected: isConnected, lineId: LINE_ID });
});

app.post('/api/qr/send', async (req, res) => {
    if (!isConnected || !sock) {
        return res.status(500).json({ error: "No conectado a WhatsApp" });
    }
    try {
        const { to, text } = req.body;
        if (!to || !text) return res.status(400).json({ error: "Faltan datos 'to' y 'text'" });
        
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        const sentMsg = await sock.sendMessage(jid, { text: text });
        
        return res.json({ status: "ok", message: "Sent", id: sentMsg?.key?.id });
    } catch (err) {
        return res.status(500).json({ error: err.message });
    }
});

// Generación / obtención del código QR para escanear desde el panel
app.get('/api/qr/link', async (req, res) => {
    if (isConnected) {
        return res.json({ status: 'connected', message: 'Ya hay un dispositivo vinculado.' });
    }
    if (!currentQR) {
        return res.json({ status: 'loading', message: 'Generando QR, intente en 3 segundos.' });
    }
    try {
        const qrImage = await QRCode.toDataURL(currentQR);
        res.json({ status: 'qr_ready', base64: qrImage });
    } catch (err) {
        res.status(500).json({ error: 'Fallo generando imagen QR' });
    }
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`✅ Servicio QR v2 escuchando en puerto ${PORT} — Interceptor de mensajes ACTIVO`);
    connectToWhatsApp();
});
