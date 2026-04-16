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

// Store en memoria: necesario para que WA pueda re-entregar mensajes @lid cifrados
const messageStore = {};

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`🌐 Usando la versión de WhatsApp Web v${version.join('.')} (Última: ${isLatest})`);

    sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: "silent" }),
        browser: ["Ubuntu", "Chrome", "20.0.04"],
        // CRÍTICO: sin getMessage, WA reporta "Message absent from node" para cuentas @lid / Business
        getMessage: async (key) => {
            if (messageStore[key.id]) return messageStore[key.id];
            return undefined;
        }
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
            // Guardar en store para que getMessage pueda responder re-entregas cifradas (@lid)
            if (msg.message) messageStore[msg.key.id] = msg.message;

            // Ignorar: mensajes propios (respuestas del bot), broadcasts de estado, o eventos sin cuerpo
            if (msg.key.fromMe || msg.key.remoteJid === 'status@broadcast' || !msg.message) continue;

            // Extraer texto
            let texto = "";
            if (msg.message.conversation) texto = msg.message.conversation;
            else if (msg.message.extendedTextMessage) texto = msg.message.extendedTextMessage.text;

            // Ignorar eventos internos sin texto real (stubs, protocolMessages, etc.)
            if (!texto || texto.trim().length === 0) continue;

            // Resolver número real: WhatsApp oculta el teléfono en @lid, pero lo expone en senderPn
            // rawSender es senderPn (número real) cuando el remoteJid es un @lid
            let rawSender = msg.key.senderPn || msg.key.remoteJid;
            const realPhone = rawSender.replace(/@(s\.whatsapp\.net|lid|g\.us)/, '');
            // senderNumber es el @lid limpio (se usa como clave de sesión)
            const senderNumber = msg.key.remoteJid.replace(/@(s\.whatsapp\.net|lid|g\.us)/, '');

            console.log(`[QR IN] ${realPhone} (lid: ${senderNumber}): "${texto}"`);

            // Preparamos payload para nuestro Python server
            // - from: ID de sesión (puede ser @lid o número real)
            // - real_phone: número telefónico real para poder responder
            const payload = {
                lineId: LINE_ID,
                wamid: msg.key.id,
                from: senderNumber,
                real_phone: realPhone,
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
        // Los LIDs son números muy largos (>15 dígitos). Los teléfonos reales tienen <15 dígitos.
        // Baileys requiere el sufijo correcto para cada tipo.
        const isLid = to && to.length > 15;
        const jid = isLid ? `${to}@lid` : `${to}@s.whatsapp.net`;
        console.log(`[QR SEND] Enviando a ${jid}: "${text}"`);
        await sock.sendMessage(jid, { text });
        res.json({ success: true });
    } catch (e) {
        console.error(`[QR SEND ERROR] ${e.message}`);
        res.status(500).json({ error: e.message });
    }
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`Servicio QR de Baileys escuchando en puerto ${PORT} (Loopback 127.0.0.1)`);
    connectToWhatsApp();
});
