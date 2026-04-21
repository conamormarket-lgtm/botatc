const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion, Browsers } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');
const NodeCache = require('node-cache');

const msgRetryCounterCache = new NodeCache();
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
        browser: Browsers.macOS('Desktop'),
        markOnlineOnConnect: true,
        generateHighQualityLinkPreview: true,
        msgRetryCounterCache, // CRÍTICO para reintentos automáticos
        retryRequestDelayMs: 2000 // Darle tiempo al Signal channel
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
            console.log('❌ Conexión cerrada. Código:', statusCode, '-', lastDisconnect?.error?.message);
            
            if (statusCode === DisconnectReason.loggedOut) {
                // 401: Dispositivo desvinculado → limpiar sesión y generar QR fresco
                console.log('🔄 Dispositivo desvinculado. Limpiando sesión para generar nuevo QR...');
                const fs = require('fs');
                const path = require('path');
                const authDir = path.join(__dirname, 'auth_info_baileys');
                try { fs.rmSync(authDir, { recursive: true, force: true }); } catch(e) {}
                setTimeout(connectToWhatsApp, 2000);
            } else {
                // Otros errores (515 restart, red, etc.) → reconectar sin borrar sesión
                setTimeout(connectToWhatsApp, 3000);
            }
        } else if (connection === 'open') {
            isConnected = true;
            currentQR = "";
            console.log('✅ Dispositivo conectado con éxito!');
        }
    });

    // DEBUG: Escuchar TODOS los eventos
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log(`[DEBUG] messages.upsert disparado. type='${type}', cantidad=${messages.length}`);

        if (type !== 'notify' && type !== 'append') return;
        
        for (let m of messages) {
            console.log(`[DEBUG] Mensaje: fromMe=${m.key.fromMe}, jid=${m.key.remoteJid}`);
            
            // Ignorar broadcasts
            if (m.key.remoteJid === 'status@broadcast') continue;

            // 1. Manejo exclusivo del CIPHERTEXT (mensaje no desencriptable por llaves perdidas)
            if (m.messageStubType === 2) {
                const real_jid_ciph = resolveRealJid(m.key, m);
                const wa_id = real_jid_ciph.split('@')[0].split(':')[0];
                const pushName = m.pushName || "Cliente";
                
                // Solo mandar placeholder si no es nuestro
                const isFromSystem = m.key.fromMe;
                
                console.log(`⚠️  CIPHERTEXT de ${wa_id} (${pushName}) — fromMe: ${isFromSystem} — Baileys gestionará reintento.`);
                
                if (!isFromSystem) {
                    try {
                        const metaPayload = {
                            "object": "whatsapp_business_account",
                            "entry": [{ "id": "BAILEYS_MOCK", "changes": [{ "value": {
                                "metadata": { "display_phone_number": LINE_ID, "phone_number_id": LINE_ID },
                                "contacts": [{ "profile": { "name": pushName }, "wa_id": wa_id }],
                                "messages": [{
                                    "from": wa_id,
                                    "id": m.key.id,
                                    "timestamp": m.messageTimestamp || Math.floor(Date.now() / 1000),
                                    "type": "text",
                                    "text": { "body": "📱 [⏳ Cifrado. Procesando llaves con el teléfono celular...]" }
                                }]
                            }}]}]
                        };
                        const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 4000 });
                        console.log(`✅ Placeholder enviado al CRM: ${resp.status}`);
                    } catch (err) { }
                }
                continue; 
            }
            
            // 2. Procesamiento de mensajes desencriptados
            try {
                const real_jid = resolveRealJid(m.key, m);
                const wa_id = real_jid.split('@')[0].split(':')[0];
                const msg_id = m.key.id;
                const timestamp = m.messageTimestamp || Math.floor(Date.now() / 1000);
                const pushName = m.pushName || "Usuario";
                const isFromMe = m.key.fromMe;

                // CRÍTICO: Ignorar mensajes enviados por nosotros para evitar el eco duplicado
                if (isFromMe) {
                    console.log(`[DEBUG] Mensaje propio (fromMe=true) ignorado para evitar eco.`);
                    continue;
                }
                
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

    // Escuchar mensajes que inicialmente llegaron cifrados (CIPHERTEXT, messageStubType=2)
    // y que Baileys descifra asincrónicamente después
    sock.ev.on('messages.update', async (updates) => {
        console.log(`[DEBUG] messages.update: ${updates.length} actualizaciones`);
        for (let { key, update } of updates) {
            if (!update.message) continue;
            if (key.fromMe || key.remoteJid === 'status@broadcast') continue;

            console.log(`[DEBUG] Mensaje descifrado vía update: jid=${key.remoteJid}`);

            // Removed buggy store

            try {
                const real_jid = resolveRealJid(key, update);
                const wa_id = real_jid.split('@')[0].split(':')[0];
                const msgTypeKey = Object.keys(update.message || {})[0];

                let msgType = 'unknown';
                let textBody = '';

                if (msgTypeKey === 'conversation' || msgTypeKey === 'extendedTextMessage') {
                    msgType = 'text';
                    textBody = update.message.conversation || update.message.extendedTextMessage?.text || '';
                } else if (msgTypeKey === 'imageMessage') {
                    msgType = 'image';
                    textBody = update.message.imageMessage?.caption || '';
                } else if (msgTypeKey === 'videoMessage') {
                    msgType = 'video';
                    textBody = update.message.videoMessage?.caption || '';
                } else if (msgTypeKey === 'audioMessage') {
                    msgType = 'audio';
                } else if (msgTypeKey === 'documentMessage') {
                    msgType = 'document';
                    textBody = update.message.documentMessage?.fileName || '';
                }

                if (msgType === 'unknown') {
                    console.log(`[DEBUG] update tipo desconocido: ${msgTypeKey}`);
                    continue;
                }

                const metaPayload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "BAILEYS_MOCK",
                        "changes": [{
                            "value": {
                                "metadata": { "display_phone_number": LINE_ID, "phone_number_id": LINE_ID },
                                "contacts": [{ "profile": { "name": "" }, "wa_id": wa_id }],
                                "messages": [{
                                    "from": wa_id,
                                    "id": key.id,
                                    "timestamp": Math.floor(Date.now() / 1000),
                                    "type": msgType,
                                    [msgType]: (msgType === 'text') ? { "body": textBody } : { "caption": textBody }
                                }]
                            }
                        }]
                    }]
                };

                console.log(`➡️ [update] Reenviando msj descifrado de ${wa_id} (${msgType}) al CRM...`);
                const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 5000 });
                console.log(`[DEBUG] Respuesta Python: ${resp.status}`);

            } catch (err) {
                console.log('❌ Error en messages.update:', err.message);
            }
        }
    });

}

// --- Helper: Resolución de LID a JID real ---
function resolveRealJid(key, msg) {
    let jid = key.remoteJid;
    if (key.remoteJidAlt && String(key.remoteJidAlt).includes('@s.whatsapp.net')) jid = key.remoteJidAlt;
    else if (key.participantAlt && String(key.participantAlt).includes('@s.whatsapp.net')) jid = key.participantAlt;
    else if (key.senderPn && String(key.senderPn).includes('@s.whatsapp.net')) jid = key.senderPn;
    else if (msg && msg.participant && String(msg.participant).includes('@s.whatsapp.net')) jid = msg.participant;
    else if (msg && msg.key && msg.key.participant && String(msg.key.participant).includes('@s.whatsapp.net')) jid = msg.key.participant;
    return jid;
}

// -----------------------------------------------------

// ----------------------------------------
// ENDPOINTS PARA EL PANEL ADMINISTRATIVO
// ----------------------------------------

app.post('/api/qr/pair', async (req, res) => {
    let { telefono } = req.body;
    if (!telefono) return res.status(400).json({error: "Falta telefono (ej: 51984...)"});
    telefono = telefono.replace(/[^0-9]/g, '');
    
    try {
        if (!sock) return res.status(500).json({error: "Módulo Baileys no iniciado aún."});
        if (isConnected) return res.status(400).json({error: "Ya estás conectado. Desvincula primero."});
        
        // CRÍTICO: Meta exige que el WebSocket esté 100% abierto antes de pedir el Pairing Code (sino da Error 428)
        let attempts = 0;
        while (!currentQR && attempts < 10) {
            await new Promise(r => setTimeout(r, 1000));
            attempts++;
        }
        
        let code = await sock.requestPairingCode(telefono);
        console.log(`\n\n======================================\n🔥 CÓDIGO DE EMPAREJAMIENTO: ${code}\n======================================\n\n`);
        return res.json({ message: "Éxito", code: code });
    } catch (e) {
        console.error("Error pidiendo código:", e);
        return res.status(500).json({ error: e.message });
    }
});

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
        
        // Limpiar el número: descartar sufijos de dispositivo y eliminar lo que no sea dígito
        const cleanNumber = to.split(':')[0].replace(/[^0-9]/g, '');
        // LIDs de Meta tienen 15 dígitos. Números telefónicos reales tienen 10-13.
        const isLid = cleanNumber.length >= 14;
        const jid = isLid ? `${cleanNumber}@lid` : `${cleanNumber}@s.whatsapp.net`;
        
        console.log(`[SEND] Intentando enviar a JID: ${jid}`);
        console.log(`[SEND] Texto: "${text}"`);
        
        const sentMsg = await sock.sendMessage(jid, { text: text });
        console.log(`[SEND] ✅ Enviado con éxito. msg_id: ${sentMsg?.key?.id}`);
        
        return res.json({ status: "ok", message: "Sent", id: sentMsg?.key?.id });
    } catch (err) {
        console.error(`[SEND] ❌ ERROR al enviar: ${err.message}`);
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
