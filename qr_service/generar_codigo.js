const { makeWASocket, useMultiFileAuthState, Browsers, fetchLatestBaileysVersion, delay, DisconnectReason } = require('@whiskeysockets/baileys');
const pino = require('pino');

const targetNumber = process.argv[2];

if (!targetNumber) {
    console.log("❌ Error: Debes poner tu número. Ejemplo: node generar_codigo.js 51984000000");
    process.exit(1);
}

const telefono = targetNumber.replace(/[^0-9]/g, '');

const fs = require('fs');
if (fs.existsSync('auth_info_baileys')) {
    console.log(`🧹 Limpiando sesión de raíz (Solo se ejecuta 1 vez)...`);
    fs.rmSync('auth_info_baileys', { recursive: true, force: true });
}

async function startPairing() {

    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    const { version } = await fetchLatestBaileysVersion();
    
    console.log(`🔌 Conectando al servidor de WhatsApp (v${version.join('.')})...`);

    const sock = makeWASocket({
        version,
        auth: state,
        logger: pino({ level: 'silent' }),
        browser: Browsers.ubuntu('Chrome'), // Disfraz obligatorio para móviles
        printQRInTerminal: false,
    });

    sock.ev.on('creds.update', saveCreds);

    let hasRequestedCode = false;

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr && !sock.authState.creds.registered && !hasRequestedCode) {
            hasRequestedCode = true;
            console.log("🚦 Servidor listo. Solicitando código ahora mismo...");
            try {
                // Pequeña pausa para no tropezar con el handshake
                await delay(2000); 
                const code = await sock.requestPairingCode(telefono);
                console.log(`\n======================================================`);
                console.log(`🔥🔥 TU CÓDIGO DE WHATSAPP ES:   ${code}   🔥🔥`);
                console.log(`======================================================\n`);
                console.log(`👉 Entra a WhatsApp > Dispositivos Vinculados > Vincular con número`);
                console.log(`⏳ Tienes 15 SEGUNDOS para ingresarlo antes de que caduque.`);
            } catch (err) {
                console.error("❌ Fallo crítico de Meta:", err?.output?.payload?.message || err.message);
                process.exit(1);
            }
        }

        if (connection === 'open') {
            console.log('✅ ¡EMPAREJAMIENTO EXITOSO! 🎉');
            console.log('Ya puedes presionar Ctrl+C para salir y luego encender el pm2 bot.');
            process.exit(0);
        }

        if (connection === 'close') {
            const code = lastDisconnect?.error?.output?.statusCode;
            console.log(`❌ Conexión cerrada (${code}).`);
            
            // Si es 515, Meta nos pide que nos reconectemos INMEDIATAMENTE para concretar el Logging In
            if (code === DisconnectReason.restartRequired) {
                console.log("🔄 Meta solicita reinicio (515). Reconectando velozmente para salvar sincronización...");
                startPairing();
            }
        }
    });
}

startPairing();
