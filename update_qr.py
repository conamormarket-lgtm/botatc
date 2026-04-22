import os
import re

js_path = os.path.join("qr_service", "index.js")
with open(js_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace globals with Map
content = content.replace("let sock;\nlet currentQR = \"\";\nlet isConnected = false;", "const sessions = new Map(); // map: lineId -> {sock, currentQR, isConnected}\n")
content = content.replace("const LINE_ID = \"qr_ventas_1\";", "")

# 2. Update connectToWhatsApp signature and body
content = content.replace("async function connectToWhatsApp() {", "async function connectToWhatsApp(lineId) {")
content = content.replace("await useMultiFileAuthState('auth_info_baileys')", "await useMultiFileAuthState(`auth_info_baileys_${lineId}`)")

# Add session initialization after makeWASocket
content = content.replace("msgRetryCounterCache,\n        retryRequestDelayMs: 2000\n    });", 
"""msgRetryCounterCache,
        retryRequestDelayMs: 2000
    });
    
    let session = { sock, currentQR: "", isConnected: false };
    sessions.set(lineId, session);""")

# Update references inside connectToWhatsApp
content = content.replace("currentQR =", "session.currentQR =")
content = content.replace("isConnected =", "session.isConnected =")
content = content.replace("const authDir = path.join(__dirname, 'auth_info_baileys');", "const authDir = path.join(__dirname, `auth_info_baileys_${lineId}`);")
content = content.replace("setTimeout(connectToWhatsApp, 2000);", "setTimeout(() => connectToWhatsApp(lineId), 2000);")
content = content.replace("setTimeout(connectToWhatsApp, 3000);", "setTimeout(() => connectToWhatsApp(lineId), 3000);")

# Update LINE_ID references inside connectToWhatsApp to lineId
content = content.replace("display_phone_number\": LINE_ID", "display_phone_number\": lineId")
content = content.replace("phone_number_id\": LINE_ID", "phone_number_id\": lineId")

# 3. Update /api/qr/pair
content = re.sub(
    r"app\.post\('/api/qr/pair', async \(req, res\) => \{.*?(let \{ telefono \} = req\.body;)",
    r"app.post('/api/qr/pair', async (req, res) => {\n    let { telefono, lineId = 'qr_ventas_1' } = req.body;",
    content, flags=re.DOTALL
)
content = content.replace("if (!sock)", "const session = sessions.get(lineId);\n        if (!session || !session.sock)")
content = content.replace("if (isConnected)", "if (session.isConnected)")
content = content.replace("while (!currentQR", "while (!session.currentQR")
content = content.replace("await sock.requestPairingCode", "await session.sock.requestPairingCode")


# 4. Update /api/qr/status
content = content.replace(
"""app.get('/api/qr/status', (req, res) => {
    res.json({ connected: isConnected, lineId: LINE_ID });
});""",
"""app.get('/api/qr/status', (req, res) => {
    const lineId = req.query.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    res.json({ connected: session ? session.isConnected : false, lineId });
});"""
)

# 5. Update /api/qr/send-media and /api/qr/send
content = re.sub(r"app\.post\('/api/qr/send-media', async \(req, res\) => \{.*?if \(!isConnected \|\| !sock\) \{",
r"""app.post('/api/qr/send-media', async (req, res) => {
    const lineId = req.body.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    if (!session || !session.isConnected || !session.sock) {""", content, flags=re.DOTALL)

content = re.sub(r"app\.post\('/api/qr/send', async \(req, res\) => \{.*?if \(!isConnected \|\| !sock\) \{",
r"""app.post('/api/qr/send', async (req, res) => {
    const lineId = req.body.lineId || "qr_ventas_1";
    const session = sessions.get(lineId);
    if (!session || !session.isConnected || !session.sock) {""", content, flags=re.DOTALL)

content = content.replace("const sentMsg = await sock.sendMessage", "const sentMsg = await session.sock.sendMessage")

# 6. Update /api/qr/link
content = re.sub(
    r"app\.get\('/api/qr/link', async \(req, res\) => \{.*?if \(isConnected\) \{",
    r"""app.get('/api/qr/link', async (req, res) => {
    const lineId = req.query.lineId || "qr_ventas_1";
    if (!sessions.has(lineId)) {
        connectToWhatsApp(lineId);
        return res.json({ status: 'loading', message: 'Iniciando servicio para ' + lineId + '...' });
    }
    const session = sessions.get(lineId);
    if (session.isConnected) {""", content, flags=re.DOTALL
)

content = content.replace("if (!currentQR)", "if (!session.currentQR)")
content = content.replace("QRCode.toDataURL(currentQR)", "QRCode.toDataURL(session.currentQR)")

# 7. Add /api/qr/logout endpoint
logout_endpoint = """
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
"""
content = content.replace("app.listen(PORT", logout_endpoint + "\napp.listen(PORT")

# 8. Remove the default connectToWhatsApp call at the bottom
content = content.replace("    connectToWhatsApp();\n});", "    // QRs are started on-demand via /api/qr/link\n});")


with open(js_path, "w", encoding="utf-8") as f:
    f.write(content)
print("index.js actualizado para multiples sesiones.")
