const express = require('express');
const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion, Browsers, downloadMediaMessage } = require('@whiskeysockets/baileys');
const pino = require('pino');
const QRCode = require('qrcode');
const axios = require('axios');
const NodeCache = require('node-cache');
const fs = require('fs');
const path = require('path');

// Setup qr media cache dir
const mediaPath = path.join(__dirname, 'qr_media_cache');
if (!fs.existsSync(mediaPath)) {
    fs.mkdirSync(mediaPath, { recursive: true });
}

const msgRetryCounterCache = new NodeCache();
const app = express();

// Mapa: msgId -> n├║mero de tel├®fono real (para resolver LIDs en status updates)
// TTL de 1 hora para evitar fugas de memoria
const sentMsgPhoneMap = new NodeCache({ stdTTL: 3600 });
app.use(express.json());
// Servir est├íticos de media local para que Python los consuma a trav├®s de la ruta esperada por qr_client.py
app.use('/media', express.static(mediaPath));
app.use('/api/qr/media', express.static(mediaPath));

const PORT = 3000;


const sessions = new Map(); // map: lineId -> {sock, currentQR, isConnected}

// ── Sistema de alertas: evitar spam (min 30 min entre alertas por línea) ──
const lastAlertTime = new Map();
const ALERT_COOLDOWN_MS = 30 * 60 * 1000; // 30 minutos

async function enviarAlertaQR(lineId, motivo) {
    const now = Date.now();
    const last = lastAlertTime.get(lineId) || 0;
    if (now - last < ALERT_COOLDOWN_MS) {
        console.log(`[ALERTA] Cooldown activo para ${lineId}, omitiendo alerta.`);
        return;
    }
    lastAlertTime.set(lineId, now);

    const mensaje = `⚠️ *ALERTA QR - ${lineId}*\n\n` +
        `Motivo: ${motivo}\n` +
        `Hora: ${new Date().toLocaleString('es-PE', { timeZone: 'America/Lima' })}\n\n` +
        `Acción requerida: Ir al panel admin → Configuración → Líneas QR y escanear el código.`;

    try {
        await axios.post('http://127.0.0.1:8000/api/internal/alerta_qr', {
            lineId,
            motivo,
            mensaje
        }, { timeout: 5000 });
        console.log(`[ALERTA] ✅ Alerta enviada al CRM para ${lineId}: ${motivo}`);
    } catch (e) {
        console.log(`[ALERTA] ⚠️ No se pudo notificar al CRM: ${e.message}`);
    }
}


async function connectToWhatsApp(lineId) {
    const { state, saveCreds } = await useMultiFileAuthState(`auth_info_baileys_${lineId}`);
    const { version, isLatest } = await fetchLatestBaileysVersion();
    console.log(`­ƒîÉ [${lineId}] WhatsApp Web v${version.join('.')} (├Ültima: ${isLatest})`);

    // Crear/obtener el objeto de sesi├│n ANTES de makeWASocket para que los callbacks puedan cerrarlo
    let session = sessions.get(lineId) || { sock: null, currentQR: "", isConnected: false };
    sessions.set(lineId, session);

    const sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: "silent" }),
        browser: Browsers.macOS('Desktop'),
        markOnlineOnConnect: true,
        emitOwnReceipts: true,
        generateHighQualityLinkPreview: true,
        msgRetryCounterCache, // CR├ìTICO para reintentos autom├íticos
        retryRequestDelayMs: 2000 // Darle tiempo al Signal channel
    });
    session.sock = sock; // Guardar referencia en la sesi├│n para que los endpoints puedan usarla

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            session.currentQR = qr;
            console.log('­ƒô▒ Nuevo QR generado ÔÇö listo para escanear.');
        }

        if (connection === 'close') {
            session.isConnected = false;
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            console.log('❌ Conexión cerrada. Código:', statusCode, '-', lastDisconnect?.error?.message);
            
            if (statusCode === DisconnectReason.loggedOut) {
                // 401: Dispositivo desvinculado → limpiar sesión y generar QR fresco
                console.log('🔑 Dispositivo desvinculado. Limpiando sesión para generar nuevo QR...');
                // Alertar al admin
                enviarAlertaQR(lineId, `Dispositivo desvinculado (código 401). El QR de la línea fue removido desde el teléfono.`);
                const authDir = path.join(__dirname, `auth_info_baileys_${lineId}`);
                try { fs.rmSync(authDir, { recursive: true, force: true }); } catch(e) {}
                setTimeout(() => connectToWhatsApp(lineId), 2000);
            } else if (statusCode === 408) {
                // 408: QR no escaneado a tiempo — la línea quedó sin conectar
                console.log('⏰ QR no escaneado (código 408). Reconectando y alertando...');
                enviarAlertaQR(lineId, `QR expiró sin ser escaneado (código 408). La línea no está conectada.`);
                setTimeout(() => connectToWhatsApp(lineId), 3000);
            } else {
                // Otros errores (515 restart, red, etc.) → reconectar sin borrar sesión
                setTimeout(() => connectToWhatsApp(lineId), 3000);
            }
        } else if (connection === 'open') {
            session.isConnected = true;
            session.currentQR = "";
            console.log('Ô£à Dispositivo conectado con ├®xito!');
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
                
                console.log(`ÔÜá´©Å  CIPHERTEXT de ${wa_id} (${pushName}) ÔÇö fromMe: ${isFromSystem} ÔÇö Baileys gestionar├í reintento.`);
                
                if (!isFromSystem) {
                    try {
                        const metaPayload = {
                            "object": "whatsapp_business_account",
                            "entry": [{ "id": "BAILEYS_MOCK", "changes": [{ "value": {
                                "metadata": { "display_phone_number": lineId, "phone_number_id": lineId },
                                "contacts": [{ "profile": { "name": pushName }, "wa_id": wa_id }],
                                "messages": [{
                                    "from": wa_id,
                                    "id": m.key.id,
                                    "timestamp": m.messageTimestamp || Math.floor(Date.now() / 1000),
                                    "type": "text",
                                    "text": { "body": "­ƒô▒ [ÔÅ│ Cifrado. Procesando llaves con el tel├®fono celular...]" }
                                }]
                            }}]}]
                        };
                        const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 4000 });
                        console.log(`Ô£à Placeholder enviado al CRM: ${resp.status}`);
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

                let isAgentMsg = false;
                // CR├ìTICO: Diferenciar eco del bot vs mensaje enviado por operador desde el celular
                if (isFromMe) {
                    if (sentMsgPhoneMap.has(msg_id)) {
                        // Este ID fue enviado por el bot via API ÔåÆ ignorar para evitar eco
                        console.log(`[DEBUG] Eco del bot (fromMe=true, ID conocido) ignorado.`);
                        continue;
                    }
                    // El operador escribi├│ desde el celular ÔåÆ lo pasaremos al CRM como agent_message
                    console.log(`[DEBUG] Mensaje del operador desde el celular (fromMe=true, ID desconocido). Se procesar├í multimedia y se enviar├í al CRM.`);
                    isAgentMsg = true;
                }
                
                let msgType = "unknown";
                let textBody = "";
                let mimeType = "";
                let mediaUrl = "";

                const msgTypeKey = Object.keys(m.message || {})[0];
                if (!msgTypeKey) continue;
                
                if (msgTypeKey === 'conversation' || msgTypeKey === 'extendedTextMessage') {
                    msgType = 'text';
                    textBody = m.message.conversation || m.message.extendedTextMessage?.text || "";
                } else if (['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage', 'stickerMessage'].includes(msgTypeKey)) {
                    // Mapeo unificado para manejo de multimedia entrante
                    const isVid = msgTypeKey === 'videoMessage';
                    const isAud = msgTypeKey === 'audioMessage';
                    const isDoc = msgTypeKey === 'documentMessage';
                    const isSticker = msgTypeKey === 'stickerMessage';
                    
                    msgType = isVid ? 'video' : isAud ? 'audio' : isDoc ? 'document' : isSticker ? 'sticker' : 'image';
                    textBody = m.message[msgTypeKey]?.caption || m.message[msgTypeKey]?.fileName || "";
                    mimeType = m.message[msgTypeKey]?.mimetype || "application/octet-stream";
                    
                    try {
                        const buffer = await downloadMediaMessage(
                            m,
                            'buffer',
                            { },
                            { 
                                logger: pino({ level: 'silent' }),
                                reuploadRequest: sock.updateMediaMessage
                            }
                        );
                        
                        // Guardar en la cach├® local
                        const extension = mimeType.split('/')[1]?.split(';')[0] || 'bin';
                        const fileName = `qr_media_${msg_id}.${extension}`;
                        fs.writeFileSync(path.join(mediaPath, fileName), buffer);
                        
                        // En lugar de una Pseudo-URL, devolvemos solo el nombre de archivo (que empieza por qr_)
                        // para que el CRM backend (FastAPI) lo descargue mediante qr_client.py
                        mediaUrl = fileName;
                        console.log(`[DEBUG] Media descargada localmente: ${fileName}`);
                        
                    } catch (e) {
                        console.log("ÔØî Error descargando media de Baileys:", e.message);
                    }
                }
                
                if (msgType === "unknown") {
                    console.log(`[DEBUG] Tipo desconocido '${msgTypeKey}', saltando.`);
                    continue;
                }

                // Payload base de mapeo hacia Cloud API
                const metaMessage = {
                    "from": wa_id,
                    "id": msg_id,
                    "timestamp": timestamp,
                    "type": msgType
                };
                
                if (isAgentMsg) {
                    metaMessage["agent_message"] = true;
                }
                
                if (msgType === 'text') {
                    metaMessage[msgType] = { "body": textBody };
                } else {
                    metaMessage[msgType] = { "mime_type": mimeType };
                    if (mediaUrl) metaMessage[msgType]["id"] = mediaUrl; // Truco local
                    if (textBody) {
                        if (msgType === 'document') {
                            metaMessage[msgType]["filename"] = textBody;
                        } else {
                            metaMessage[msgType]["caption"] = textBody;
                        }
                    }
                }

                // Construimos payload fingiendo ser Meta
                const metaPayload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "BAILEYS_MOCK",
                        "changes": [{
                            "value": {
                                "metadata": { "display_phone_number": lineId, "phone_number_id": lineId },
                                "contacts": [{ "profile": { "name": pushName }, "wa_id": wa_id }],
                                "messages": [metaMessage]
                            }
                        }]
                    }]
                };

                console.log(`Ô×í´©Å Reenviando msj de ${wa_id} (${msgType}: '${textBody}') al CRM Python...`);
                const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 5000 });
                console.log(`[DEBUG] Respuesta Python: ${resp.status} - ${JSON.stringify(resp.data)}`);
                
            } catch (err) {
                console.log("ÔØî Error procesando mensaje de Baileys:", err.message);
                if (err.response) {
                    console.log("[DEBUG] Respuesta de error Python:", err.response.status, err.response.data);
                }
            }
        }
    });

    // Escuchar mensajes que inicialmente llegaron cifrados (CIPHERTEXT, messageStubType=2)
    // y que Baileys descifra asincr├│nicamente despu├®s
    sock.ev.on('messages.update', async (updates) => {
        console.log(`[DEBUG] messages.update: ${updates.length} actualizaciones`);
        for (let { key, update } of updates) {
            
            // Procesamiento de Recibos de Entrega y Lectura para mensajes propios
            if (key.fromMe && update.status) {
                let metaStatus = '';
                if (update.status === 4) metaStatus = 'delivered';
                else if (update.status === 5 || update.status === 6) metaStatus = 'read';
                // status 3 = 'sent' lo ignoramos (ya lo manejamos al enviar)
                
                if (metaStatus) {
                    // CR├ìTICO: Intentar resolver el n├║mero real desde el mapa, porque
                    // Baileys puede reportar el LID (152286...) en lugar del n├║mero de tel├®fono
                    let wa_id = sentMsgPhoneMap.get(key.id);
                    if (!wa_id) {
                        // Fallback: resolver desde el JID del evento
                        const real_jid = resolveRealJid(key, update);
                        if (real_jid) wa_id = real_jid.split('@')[0].split(':')[0];
                    }
                    
                    if (!wa_id) {
                        console.log(`[STATUS WARN] No se pudo resolver wa_id para msg_id=${key.id}, status=${metaStatus}`);
                        continue;
                    }
                    
                    console.log(`[STATUS] ${metaStatus} para ${key.id} -> resuelto a ${wa_id}`);
                    
                    const metaPayload = {
                        "object": "whatsapp_business_account",
                        "entry": [{
                            "id": "BAILEYS_MOCK",
                            "changes": [{
                                "value": {
                                    "metadata": { "display_phone_number": lineId, "phone_number_id": lineId },
                                    "statuses": [{
                                        "id": key.id,
                                        "status": metaStatus,
                                        "recipient_id": wa_id
                                    }]
                                }
                            }]
                        }]
                    };
                    try {
                        await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 3000 });
                        console.log(`[STATUS] Ô£à Estado '${metaStatus}' de msg_id=${key.id} reenviado (wa_id=${wa_id})`);
                    } catch (e) {
                        console.log(`[STATUS ERROR] HTTP al reenviar estado: ${e.message}`);
                    }
                }
                continue;
            }

            if (!update.message) continue;
            if (key.fromMe || key.remoteJid === 'status@broadcast') continue;

            console.log(`[DEBUG] Mensaje descifrado v├¡a update: jid=${key.remoteJid}`);

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
                                "metadata": { "display_phone_number": lineId, "phone_number_id": lineId },
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

                console.log(`Ô×í´©Å [update] Reenviando msj descifrado de ${wa_id} (${msgType}) al CRM...`);
                const resp = await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 5000 });
                console.log(`[DEBUG] Respuesta Python: ${resp.status}`);

            } catch (err) {
                console.log('ÔØî Error en messages.update:', err.message);
            }
        }
    });
    sock.ev.on('message-receipt.update', async (events) => {
        console.log(`[DEBUG] message-receipt.update: ${events.length} recibos`);
        for (let ev of events) {
            if (!ev.key.fromMe) continue;
            
            let metaStatus = '';
            // Si hay timestamp de lectura, es le├¡do. Si solo hay de recepci├│n, es entregado.
            if (ev.receipt?.readTimestamp) metaStatus = 'read';
            else if (ev.receipt?.receiptTimestamp) metaStatus = 'delivered';
            
            if (!metaStatus) continue;
            
            // CR├ìTICO: Resolver el n├║mero real desde el mapa msgId->phone (mismo fix que messages.update)
            // porque Baileys puede usar el LID (152286...) en lugar del n├║mero de tel├®fono real
            let wa_id = sentMsgPhoneMap.get(ev.key.id);
            if (!wa_id) {
                const real_jid = resolveRealJid(ev.key, ev);
                if (real_jid) wa_id = real_jid.split('@')[0].split(':')[0];
            }
            if (!wa_id) {
                console.log(`[RECEIPT WARN] No se pudo resolver wa_id para msg_id=${ev.key.id}`);
                continue;
            }
            console.log(`[RECEIPT] ${metaStatus} para ${ev.key.id} -> resuelto a ${wa_id}`);
            
            if (metaStatus) {
                const metaPayload = {
                    "object": "whatsapp_business_account",
                    "entry": [{
                        "id": "BAILEYS_MOCK",
                        "changes": [{
                            "value": {
                                "metadata": { "display_phone_number": lineId, "phone_number_id": lineId },
                                "statuses": [{
                                    "id": ev.key.id,
                                    "status": metaStatus,
                                    "recipient_id": wa_id
                                }]
                            }
                        }]
                    }]
                };
                setTimeout(async () => {
                    try {
                        await axios.post('http://127.0.0.1:8000/webhook', metaPayload, { timeout: 3000 });
                        console.log(`[STATUS] Receipt '${metaStatus}' msg_id=${ev.key.id} reenviado (Delayed)`);
                    } catch (e) {
                        console.log(`[STATUS ERROR] HTTP reenviando receipt al webhook: ${e.message}`);
                    }
                }, 1500);
            }
        }
    });

}

// --- Helper: Resoluci├│n de LID a JID real ---
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
    let { telefono, lineId = 'qr_ventas_1' } = req.body;
    if (!telefono) return res.status(400).json({error: "Falta telefono (ej: 51984...)"});
    telefono = telefono.replace(/[^0-9]/g, '');
    
    try {
        const session = sessions.get(lineId);
        if (!session || !session.sock) return res.status(500).json({error: "M├│dulo Baileys no iniciado a├║n."});
        if (session.isConnected) return res.status(400).json({error: "Ya est├ís conectado. Desvincula primero."});
        
        // CR├ìTICO: Meta exige que el WebSocket est├® 100% abierto antes de pedir el Pairing Code (sino da Error 428)
        let attempts = 0;
        while (!session.currentQR && attempts < 10) {
            await new Promise(r => setTimeout(r, 1000));
            attempts++;
        }
        
        let code = await session.sock.requestPairingCode(telefono);
        console.log(`\n\n======================================\n­ƒöÑ C├ôDIGO DE EMPAREJAMIENTO: ${code}\n======================================\n\n`);
        return res.json({ message: "├ëxito", code: code });
    } catch (e) {
        console.error("Error pidiendo c├│digo:", e);
        return res.status(500).json({ error: e.message });
    }
});

// Estado de conexi├│n de la l├¡nea QR
app.get('/api/qr/status', (req, res) => {
    const lineId = req.query.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    res.json({ connected: session ? session.isConnected : false, lineId });
});



// Endpoint principal para env├¡o de media
app.post('/api/qr/send-media', async (req, res) => {
    const lineId = req.body.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    if (!session || !session.isConnected || !session.sock) {
        return res.status(503).json({ error: "El servicio QR no est├í conectado" });
    }
    try {
        const { to, type, url, caption } = req.body;
        if (!to || !type) return res.status(400).json({ error: "Faltan par├ímetros 'to' o 'type'" });

        // Limpiar el n├║mero saliente
        const cleanNumber = to.split(':')[0].replace(/[^0-9]/g, '');
        const isLid = cleanNumber.length >= 14;
        const jid = isLid ? `${cleanNumber}@lid` : `${cleanNumber}@s.whatsapp.net`;

        let mediaPayload = {};
        if (url) {
            // Si es URL directamente, Baileys normalmente la procesar├í sola si es { url: "http..." }
            mediaPayload = { [type]: { url: url } }; 
        }

        if (caption && type !== 'audio' && type !== 'sticker') {
            mediaPayload.caption = caption;
        }

        // Forzar ptt en audios si quieres notas de voz (depende de tu necesidad, usaremos ptt: true)
        if (type === 'audio') {
            mediaPayload.ptt = true;
        }

        const sentMsg = await session.sock.sendMessage(jid, mediaPayload);
        console.log(`[SEND_MEDIA] Ô£ë´©Å Ô£à ${type} mandado a ${jid}`);
        
        // Guardar mapeo msgId -> n├║mero real para resolver LIDs despu├®s
        if (sentMsg?.key?.id) {
            const realPhone = cleanNumber;
            sentMsgPhoneMap.set(sentMsg.key.id, realPhone);
            console.log(`[MAP] ${sentMsg.key.id} -> ${realPhone}`);
        }
        
        return res.json({ status: "ok", message: "Sent", id: sentMsg?.key?.id });
    } catch (err) {
        console.error(`[SEND_MEDIA] ÔØî ERROR: ${err.message}`);
        return res.status(500).json({ error: err.message });
    }
});

app.post('/api/qr/send', async (req, res) => {
    const lineId = req.body.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    if (!session || !session.isConnected || !session.sock) {
        return res.status(500).json({ error: "No conectado a WhatsApp" });
    }
    try {
        const { to, text } = req.body;
        if (!to || !text) return res.status(400).json({ error: "Faltan datos 'to' y 'text'" });
        
        // Limpiar el n├║mero: descartar sufijos de dispositivo y eliminar lo que no sea d├¡gito
        const cleanNumber = to.split(':')[0].replace(/[^0-9]/g, '');
        // LIDs de Meta tienen 15 d├¡gitos. N├║meros telef├│nicos reales tienen 10-13.
        const isLid = cleanNumber.length >= 14;
        const jid = isLid ? `${cleanNumber}@lid` : `${cleanNumber}@s.whatsapp.net`;
        
        console.log(`[SEND] Intentando enviar a JID: ${jid}`);
        console.log(`[SEND] Texto: "${text}"`);
        
        const sentMsg = await session.sock.sendMessage(jid, { text: text });
        console.log(`[SEND] Ô£à Enviado con ├®xito. msg_id: ${sentMsg?.key?.id}`);
        
        // Guardar mapeo msgId -> n├║mero real para resolver LIDs despu├®s
        if (sentMsg?.key?.id) {
            const realPhone = cleanNumber;
            sentMsgPhoneMap.set(sentMsg.key.id, realPhone);
            console.log(`[MAP] ${sentMsg.key.id} -> ${realPhone}`);
        }
        
        return res.json({ status: "ok", message: "Sent", id: sentMsg?.key?.id });
    } catch (err) {
        console.error(`[SEND] ÔØî ERROR al enviar: ${err.message}`);
        return res.status(500).json({ error: err.message });
    }
});

// Generaci├│n / obtenci├│n del c├│digo QR para escanear desde el panel
app.get('/api/qr/link', async (req, res) => {
    const lineId = req.query.lineId || "qr_ventas_1";
    
    // Si no hay sesi├│n para este lineId, iniciarla
    if (!sessions.has(lineId)) {
        console.log(`[QR] Iniciando nueva sesi├│n para lineId=${lineId}`);
        connectToWhatsApp(lineId).catch(err => console.error(`[QR] Error iniciando ${lineId}:`, err.message));
        return res.json({ status: 'loading', message: `Iniciando sesi├│n para ${lineId}, intente en 5 segundos.` });
    }
    
    const session = sessions.get(lineId);
    
    if (session.isConnected) {
        return res.json({ status: 'connected', lineId, message: 'Ya hay un dispositivo vinculado.' });
    }
    if (!session.currentQR) {
        return res.json({ status: 'loading', message: 'Generando QR, intente en 3 segundos.' });
    }
    try {
        const qrImage = await QRCode.toDataURL(session.currentQR);
        res.json({ status: 'qr_ready', lineId, base64: qrImage });
    } catch (err) {
        res.status(500).json({ error: 'Fallo generando imagen QR' });
    }
});


app.delete('/api/qr/logout', (req, res) => {
    const lineId = req.query.lineId || "qr_ventas_1";
    if (sessions.has(lineId)) {
        const session = sessions.get(lineId);
        try { session.sock.logout(); } catch(e){}
        sessions.delete(lineId);
    }
    try { fs.rmSync(path.join(__dirname, `auth_info_baileys_${lineId}`), { recursive: true, force: true }); } catch(e){}
    res.json({ ok: true });
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`Ô£à Servicio QR v2 escuchando en puerto ${PORT} ÔÇö Interceptor de mensajes ACTIVO`);
    
    // Auto-reconectar todas las l├¡neas que tengan credenciales guardadas
    try {
        const entries = fs.readdirSync(__dirname);
        const authDirs = entries.filter(e => e.startsWith('auth_info_baileys_') && fs.statSync(path.join(__dirname, e)).isDirectory());
        if (authDirs.length > 0) {
            console.log(`[AUTO-RECONNECT] Encontradas ${authDirs.length} sesiones guardadas. Reconectando...`);
            for (const dir of authDirs) {
                const lineId = dir.replace('auth_info_baileys_', '');
                console.log(`[AUTO-RECONNECT] Iniciando sesi├│n para lineId=${lineId}`);
                connectToWhatsApp(lineId).catch(err => console.error(`[AUTO-RECONNECT] Error en ${lineId}:`, err.message));
            }
        } else {
            console.log('[AUTO-RECONNECT] No hay sesiones guardadas. Esperando vinculaci├│n desde el panel.');
        }
    } catch(e) {
        console.error('[AUTO-RECONNECT] Error escaneando sesiones:', e.message);
    }
});

// Capturar errores no manejados para que un mensaje malo no mate el servidor
process.on('unhandledRejection', (reason, promise) => {
    console.error('[ERROR] Promesa rechazada no manejada:', reason?.message || reason);
});
process.on('uncaughtException', (err) => {
    console.error('[ERROR] Excepci├│n no capturada (el servidor sigue vivo):', err.message);
});
