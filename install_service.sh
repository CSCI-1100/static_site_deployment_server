# install_service.sh - Install as systemd service (optional)
#! /bin/bash -

SERVICE_NAME="static-deploy"
SERVICE_USER="www-data"
PROJECT_DIR="$(pwd)"

echo "📦 Installing Static Site Deployment as systemd service..."

# Create service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOL
[Unit]
Description=Static Site Deployment Server
After=network.target

[Service]
Type=exec
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
ExecStart=${PROJECT_DIR}/venv/bin/gunicorn static_deploy.wsgi:application \\
    --bind 0.0.0.0:5000 \\
    --workers 3 \\
    --certfile=${PROJECT_DIR}/ssl/server.crt \\
    --keyfile=${PROJECT_DIR}/ssl/server.key
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Change ownership
sudo chown -R ${SERVICE_USER}:${SERVICE_USER} ${PROJECT_DIR}

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "✅ Service installed and started!"
echo "Status: sudo systemctl status ${SERVICE_NAME}"
echo "Logs: sudo journalctl -u ${SERVICE_NAME} -f"
