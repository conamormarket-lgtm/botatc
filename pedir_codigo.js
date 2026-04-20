const http = require("http");

// Argumento pasado por terminal (ej: node pedir_codigo.js 51984... )
const telefono = process.argv[2];

if (!telefono) {
    console.log(`
❌ Error: Debes ingresar tu número de teléfono con el código de país.
👉 Ejemplo: node pedir_codigo.js 51984555666
`);
    process.exit(1);
}

console.log(`\nSolicitando código de emparejamiento para: ${telefono}...`);

const data = JSON.stringify({ telefono: telefono });

const options = {
    hostname: '127.0.0.1',
    port: 3000,
    path: '/api/qr/pair',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
    }
};

const req = http.request(options, res => {
    let responseBody = '';
    res.on('data', chunk => { responseBody += chunk; });
    
    res.on('end', () => {
        try {
            const parsed = JSON.parse(responseBody);
            if (res.statusCode >= 400) {
                console.log(`❌ Error del servidor: ${parsed.error || responseBody}`);
                if (parsed.error && parsed.error.includes("Ya estás conectado")) {
                    console.log("\n⚠️ Tienes que borrar la sesión actual. Ejecuta:");
                    console.log("pm2 stop bot-qr");
                    console.log("rm -rf qr_service/auth_info_baileys");
                    console.log("pm2 start bot-qr\n");
                }
            } else {
                console.log(`
===================================================
🔥🔥 TU CÓDIGO DE WHATSAPP ES:  ${parsed.code}  🔥🔥
===================================================

1. Abre WhatsApp en tu celular.
2. Toca los tres puntos (Menú) -> Dispositivos vinculados.
3. Toca "Vincular dispositivo".
4. En la parte de abajo de la cámara, toca "Vincular con el número de teléfono".
5. ¡Ingresa este código!
                `);
            }
        } catch(e) {
            console.log("Error parseando:", responseBody);
        }
    });
});

req.on('error', error => {
    console.log(`❌ Error de red: ${error.message} (¿El pm2 bot-qr está corriendo?)`);
});

req.write(data);
req.end();
