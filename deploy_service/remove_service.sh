#!/bin/bash
set -e

# Function to remove a service
remove_service() {
    local SERVICE_NAME="$1"
    local SYSTEMD_DIR="/etc/systemd/system"

    if [ -z "$SERVICE_NAME" ]; then
        echo "❌ Usage: remove_service <service_name>"
        return 1
    fi

    echo "🛑 Stopping service $SERVICE_NAME..."
    sudo systemctl stop "${SERVICE_NAME}.service" || true
    sudo systemctl disable "${SERVICE_NAME}.service" || true

    echo "🗑 Removing service file..."
    sudo rm -f "$SYSTEMD_DIR/${SERVICE_NAME}.service"

    echo "🔄 Reloading systemd..."
    sudo systemctl daemon-reload

    echo "✅ Service $SERVICE_NAME removed."
}

remove_service taro_daily
deploy_service taro_web
