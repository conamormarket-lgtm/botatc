> **BrainSync Context Pumper** 🧠
> Dynamically loaded for active file: `qr_service\index.js` (Domain: **Generic Logic**)

### 📐 Generic Logic Conventions & Fixes
- **[convention] Fixed null crash in DisconnectReason — prevents null/undefined runtime crashes — confirmed 3x**: - const express = require('express');
+ const express = require('express');
- const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
+ const { makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
- const pino = require('pino');
+ const pino = require('pino');
- const QRCode = require('qrcode');
+ const QRCode = require('qrcode');
- const axios = require('axios');
+ 
- const fs = require('fs');
+ const app = express();
- 
+ app.use(express.json());
- const app = express();
+ 
- app.use(express.json());
+ const PORT = 3000;
- 
+ const LINE_ID = "qr_ventas_1";
- const PORT = 3000;
+ 
- const PYTHON_WEBHOOK = "https://aimunaycrm.com/webhook_qr";
+ let sock;
- const LINE_ID = "qr_ventas_1"; // ID temporal, luego será dinámico 
+ let currentQR = "";
- 
+ let isConnected = false;
- let sock;
+ 
- let currentQR = "";
+ async function connectToWhatsApp() {
- let isConnected = false;
+     const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
- 
+     const { version, isLatest } = await fetchLatestBaileysVersion();
- // Store en memoria: necesario para que WA pueda re-entregar mensajes @lid cifrados
+     console.log(`🌐 WhatsApp Web v${version.join('.')} (Última: ${isLatest})`);
- const messageStore = {};
+ 
- 
+     sock = makeWASocket({
- async function connectToWhatsApp() {
+         version,
-     const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
+         auth: state,
-     const { version, isLatest } = await fetchLatestBaileysVersion();
+         logger: pino({ level: "silent" }),
-     console.log(`🌐 Usando la versión de WhatsApp Web v${version.join('.')} (Última: ${isLatest})`);
+         browser: ["Ubuntu", "Chrome", "20.0.04"]
- 
+     });
-     sock = makeWASocket({
+ 
-         version,
+     sock.ev.on('creds.update', saveCreds);
-         a
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [express, makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion]
- **[convention] Fixed null crash in Guardar — confirmed 3x**: -             // Guardar en store para que getMessage pueda responder re-entregas
+             // Guardar en store para que getMessage pueda responder re-entregas cifradas (@lid)
-             console.log(`[DEBUG] Analizando mensaje de: ${msg.key.remoteJid} - fromMe: ${msg.key.fromMe} - Tiene Body: ${!!msg.message}`);
+ 
- 
+             // Ignorar: mensajes propios (respuestas del bot), broadcasts de estado, o eventos sin cuerpo
-             // Temporalmente dejando pasar los fromMe para confirmar que el webhook sirve a pesar de los bloqueos locales
+             if (msg.key.fromMe || msg.key.remoteJid === 'status@broadcast' || !msg.message) continue;
-             if (!msg.message || msg.key.remoteJid === 'status@broadcast') {
+ 
-                 if (!msg.message && !msg.key.fromMe) {
+             // Extraer texto
-                     console.log("[SILENCED DUMP]", JSON.stringify(msg, null, 2));
+             let texto = "";
-                 }
+             if (msg.message.conversation) texto = msg.message.conversation;
-                 continue;
+             else if (msg.message.extendedTextMessage) texto = msg.message.extendedTextMessage.text;
-             }
+ 
- 
+             // Ignorar eventos internos sin texto real (stubs, protocolMessages, etc.)
-             // Extraer texto
+             if (!texto || texto.trim().length === 0) continue;
-             let texto = "";
+ 
-             if (msg.message.conversation) texto = msg.message.conversation;
+             // Resolver número real: WhatsApp oculta el teléfono en @lid, pero lo expone en senderPn
-             else if (msg.message.extendedTextMessage) texto = msg.message.extendedTextMessage.text;
+             let rawSender = msg.key.senderPn || msg.key.remoteJid;
- 
+             const senderNumber = rawSender.replace(/@(s\.whatsapp\.net|lid|g\.us)/, '');
-             // Bloque anti-mensajes-vacíos: descartamos audios/fotos temporales que no extrayeron texto
+
… [diff truncated]

📌 IDE AST Context: Modified symbols likely include [express, makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion]
