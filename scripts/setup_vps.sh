#!/bin/bash
# =========================================================================
# SCRIPT DE DESPLIEGUE AUTOMÁTICO EN HOSTINGER VPS (Ubuntu 22.04 / 24.04)
# =========================================================================
set -e

echo "🚀 Iniciando instalación y configuración del servidor VPS para el Bot CRM..."

# 1. Actualizar sistema e instalar dependencias base
echo "📦 Instalando dependencias del sistema operativo (Python, Nginx, Certbot)..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl ufw

# 2. Configurar Firewall
echo "🛡️ Configurando el Firewall (UFW) para permitir HTTP y HTTPS..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
# No activamos ufwa automaticamente por si te bloquea fuera, pero las reglas quedan puestas

# 3. Entorno virtual de Python
echo "🐍 Creando Entorno Virtual e Instalando librerías..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Creación del Servicio Daemon (Para que funcione 24/7 de fondo)
echo "⚙️ Configurando demonio de systemd para uvicorn..."
SERVICE_FILE="/etc/systemd/system/bot-crm.service"
CURRENT_DIR=$(pwd)
CURRENT_USER=$USER

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Servidor Backend Bot CRM conAmor
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable bot-crm.service
sudo systemctl start bot-crm.service

# 5. Reverse Proxy NGINX
echo "🌐 Configurando Nginx..."
read -p "Introduce el nombre de tu dominio o subdominio (Ej: bot.tudominio.com): " DOMAIN_NAME

NGINX_CONF="/etc/nginx/sites-available/bot-crm"
sudo bash -c "cat > $NGINX_CONF" <<EOL
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Para websockets y SSE (Server Sent Events)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOL

sudo ln -sf /etc/nginx/sites-available/bot-crm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# 6. Certificado SSL
echo "🔒 Obteniendo certificado SSL de Let's Encrypt para $DOMAIN_NAME..."
sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos -m admin@$DOMAIN_NAME || echo "⚠️ Warning: No se pudo obtener SSL automáticamente. Verifica que el dominio ya apunte a la IP de este VPS en Hostinger DNS."

echo "✅ ============================================="
echo "✅ ¡DESPLIEGUE COMPLETADO Y SERVIDOR ACTIVO!"
echo "✅ Tu bot ahora corre limpiamente en 127.0.0.1:8000 (Daemon)"
echo "✅ Tu Nginx expone esto a Internet en https://$DOMAIN_NAME"
echo "✅ ============================================="
echo "⚠️ NO OLVIDES LLEVARTE TUS ARCHIVOS .env AL VPS Y REINICIAR EL SERVICIO CON:"
echo "sudo systemctl restart bot-crm.service"
