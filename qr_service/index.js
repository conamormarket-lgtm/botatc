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

    // Escachar mensajes y re-transmitirlos al CRM Python imitando el SDK de Meta Cloud
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;
        
        for (let m of messages) {
            if (m.key.fromMe || m.key.remoteJid === 'status@broadcast') continue;
            
            try {
                const wa_id = m.key.remoteJid.split('@')[0];
                const msg_id = m.key.id;
                const timestamp = m.messageTimestamp || Math.floor(Date.now() / 1000);
                const pushName = m.pushName || "Usuario";
                
                let msgType = "unknown";
                let textBody = "";
                let mimeType = "";

                const msgTypeKey = Object.keys(m.message || {})[0];
                if (!msgTypeKey) continue;
                
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
                
                if (msgType === "unknown") continue;

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

                console.log(`➡️ Reenviando msj de ${wa_id} al CRM Python...`);
                await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 3000 });
                
            } catch (err) {
                console.log("❌ Error procesando mensaje de Baileys:", err.message);
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
    console.log(`Servicio QR escuchando en puerto ${PORT} (solo vinculación, sin procesamiento de mensajes)`);
    connectToWhatsApp();
});
