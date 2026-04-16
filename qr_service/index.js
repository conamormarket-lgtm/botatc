const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');
const fs = require('fs');

const app = express();
app.use(express.json());

const PORT = 3000;
const PYTHON_WEBHOOK = "https://aimunaycrm.com/webhook_qr";
const LINE_ID = "qr_ventas_1"; // ID temporal, luego será dinámico 

let sock;
let currentQR = "";
let isConnected = false;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`🌐 Usando la versión de WhatsApp Web v${version.join('.')} (Última: ${isLatest})`);

    sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: "silent" }), // Evitar spam de logs
        browser: ["Ubuntu", "Chrome", "20.0.04"]
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            currentQR = qr; // Guardamos el texto base del QR para el endpoint
        }

        if (connection === 'close') {
            isConnected = false;
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Se cerró la conexión a WhatsApp. Código:', statusCode, '- Error:', lastDisconnect?.error?.message);
            console.log('Reconectando automáticamente:', shouldReconnect);
            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 3000); // Pequeña pausa de seguridad antes de reconectar
            }
        } else if (connection === 'open') {
            isConnected = true;
            currentQR = "";
            console.log('¡Dispositivo conectado con éxito!');
        }
    });

    // Interceptor de mensajes entrantes
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        console.log(`[DEBUG] Recibido event: type=${type}, cantidad=${messages.length}`);
        if (type !== 'notify') return;

        for (const msg of messages) {
            console.log(`[DEBUG] Analizando mensaje de: ${msg.key.remoteJid} - fromMe: ${msg.key.fromMe} - Tiene Body: ${!!msg.message}`);

            // Ignorar mensajes enviados por nosotros mismos en otro cel
            if (!msg.message || msg.key.fromMe || msg.key.remoteJid === 'status@broadcast') {
                if (!msg.message && !msg.key.fromMe) {
                    console.log("[SILENCED DUMP]", JSON.stringify(msg, null, 2));
                }
                continue;
            }

            const senderNumber = msg.key.remoteJid.replace('@s.whatsapp.net', '');

            // Extraer texto
            let texto = "";
            if (msg.message.conversation) texto = msg.message.conversation;
            else if (msg.message.extendedTextMessage) texto = msg.message.extendedTextMessage.text;

            console.log(`[DEBUG] Texto extraído: "${texto}"`);

            // Preparamos payload sencillo para nuestro Python server
            const payload = {
                lineId: LINE_ID,
                wamid: msg.key.id,
                from: senderNumber,
                timestamp: msg.messageTimestamp,
                type: texto ? "text" : "media",
                body: texto
            };

            // Enviar webhook al servidor Python
            try {
                await axios.post(PYTHON_WEBHOOK, payload, { timeout: 3000 });
                console.log(`[OK] Mensaje reenviado a Python CRM: ${senderNumber}`);
            } catch (err) {
                console.error(`[ERROR] No se pudo enviar webhook a Python: ${err.message}`);
            }
        }
    });
}

// ----------------------------------------
// ENDPOINTS PARA EL PANEL ADMINISTRATIVO
// ----------------------------------------

app.get('/api/qr/status', (req, res) => {
    res.json({ connected: isConnected, lineId: LINE_ID });
});

app.get('/api/qr/link', async (req, res) => {
    if (isConnected) {
        return res.json({ status: 'connected', message: 'Ya hay un dispositivo vinculado.' });
    }
    if (!currentQR) {
        return res.json({ status: 'loading', message: 'Generando QR, intente en 3 segundos.' });
    }

    // Generamos la imagen Base64 para inyectar directo en un <img> en admin.html
    try {
        const qrImage = await QRCode.toDataURL(currentQR);
        res.json({ status: 'qr_ready', base64: qrImage });
    } catch (err) {
        res.status(500).json({ error: 'Fallo generando imagen QR' });
    }
});

// Endpoint por si Python quiere mandar un mensaje de vuelta por esta línea
app.post('/api/qr/send', async (req, res) => {
    if (!isConnected) return res.status(400).json({ error: 'WhatsApp offline' });

    const { to, text } = req.body;
    try {
        const jid = `${to}@s.whatsapp.net`;
        await sock.sendMessage(jid, { text });
        res.json({ success: true });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`Servicio QR de Baileys escuchando en puerto ${PORT} (Loopback 127.0.0.1)`);
    connectToWhatsApp();
});
