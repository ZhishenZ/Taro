#!/bin/bash
set -e

# Function to deploy a service
deploy_service() {
    local SERVICE_NAME="$1"
    local SERVICE_FILE="${SERVICE_FILE_DIR}/${SERVICE_NAME}.service"
    local SYSTEMD_DIR="/etc/systemd/system"

    if [ -z "$SERVICE_NAME" ]; then
        echo "❌ Usage: deploy_service <service_name>"
        return 1
    fi

    # Generate service file
    echo "🔧 Generating service file..."
    python3 generate_service.py "$SERVICE_NAME"

    # Move service file to systemd directory
    echo "📦 Installing service..."
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

    # Reload systemd to pick up new service
    echo "🔄 Reloading systemd..."
    sudo systemctl daemon-reload

    # Enable and start the service
    echo "🚀 Starting service $SERVICE_NAME..."
    sudo systemctl enable "${SERVICE_NAME}.service"
    sudo systemctl start "${SERVICE_NAME}.service"

    echo "✅ Service $SERVICE_NAME deployed and started."
}

# create and source paths bash script
python3 paths.py
source output/paths.sh

# Ensure virtualenv exists
echo "📦 Checking virtual environment in $VENV_DIR ..."
if [ ! -d "$VENV_DIR" ]; then
    echo "⚡ Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
else
    echo "✅ Virtual environment already exists at $VENV_DIR"
fi

# activate virtualenv
source $VENV_DIR/bin/activate

# install taro python project
pip install -e $TARO_DIR

# depoly
deploy_service taro_daily
deploy_service taro_web
