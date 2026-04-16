const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');
const fs = require('fs');

const app = express();
app.use(express.json());

const PORT = 3000;
const PYTHON_WEBHOOK = "http://127.0.0.1:5000/webhook_qr";
const LINE_ID = "qr_ventas_1"; // ID temporal, luego será dinámico 

let sock;
let currentQR = "";
let isConnected = false;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true,
        logger: pino({ level: "silent" }), // Evitar spam de logs
        browser: ["CRM Bot", "Chrome", "1.0"]
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            currentQR = qr; // Guardamos el texto base del QR para el endpoint
        }

        if (connection === 'close') {
            isConnected = false;
            const shouldReconnect = lastDisconnect.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Se cerró la conexión a WhatsApp. Reconectando:', shouldReconnect);
            if (shouldReconnect) connectToWhatsApp();
        } else if (connection === 'open') {
            isConnected = true;
            currentQR = "";
            console.log('¡Dispositivo conectado con éxito!');
        }
    });

    // Interceptor de mensajes entrantes
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;
        
        for (const msg of messages) {
            // Ignorar mensajes vacíos, de estado, o enviados por nosotros mismos en otro cel
            if (!msg.message || msg.key.fromMe || msg.key.remoteJid === 'status@broadcast') continue;

            const senderNumber = msg.key.remoteJid.replace('@s.whatsapp.net', '');
            
            // Extraer texto
            let texto = "";
            if (msg.message.conversation) texto = msg.message.conversation;
            else if (msg.message.extendedTextMessage) texto = msg.message.extendedTextMessage.text;
            
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

app.listen(PORT, () => {
    console.log(`Servicio QR de Baileys escuchando en puerto ${PORT}`);
    connectToWhatsApp();
});
