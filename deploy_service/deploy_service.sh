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
    python3 generate_service.py "$SERVICE_NAME" "$VENV_PYTHON"

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

echo "🔍 Checking deployment prerequisites..."
echo ""

# Check if in a venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Not in a virtual environment!"
    echo ""
    echo "📋 Recommended actions:"
    echo "   1. Create a virtual environment:"
    echo "      python3 -m venv $VENV_DIR"
    echo ""
    echo "   2. Activate it:"
    echo "      source $VENV_DIR/bin/activate"
    echo ""
    echo "   3. Install taro:"
    echo "      pip install -e $TARO_DIR"
    echo ""
    echo "   4. Run this script again:"
    echo "      ./deploy_service.sh"
    echo ""
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"

# Check if taro command is available
if ! command -v taro &> /dev/null; then
    echo "❌ taro command not found!"
    echo ""
    echo "📋 Recommended actions:"
    echo "   1. Install taro in your current virtual environment:"
    echo "      pip install -e $TARO_DIR"
    echo ""
    echo "   2. Run this script again:"
    echo "      ./deploy_service.sh"
    echo ""
    exit 1
fi

echo "✅ taro command is available"

# Get the venv python path
VENV_PYTHON="$VIRTUAL_ENV/bin/python"
echo "✅ Using Python: $VENV_PYTHON"
echo ""

# deploy taro_daily service
# Note: taro_web is now deployed via Docker (see docker-compose.prod.yml)
deploy_service taro_daily
