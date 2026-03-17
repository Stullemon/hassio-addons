#!/usr/bin/with-contenv bashio
set -e

echo "[INFO] Starting WeeChat addon..."

# Get configuration
RELAY_PORT=$(python3 -c "import json; print(json.load(open('/data/options.json')).get('relay_port', 9001))")
RELAY_PASS=$(python3 -c "import json; print(json.load(open('/data/options.json')).get('relay_password', 'superstrongpassword'))")
AUTO_ACCEPT=$(python3 -c "import json; print(str(json.load(open('/data/options.json')).get('auto_accept_dcc', False)).lower())")
ENABLE_MONITOR=$(python3 -c "import json; print(str(json.load(open('/data/options.json')).get('enable_monitor_script', False)).lower())")

echo "[INFO] Configuration loaded: port=$RELAY_PORT"

# Setup directories
DOWNLOADS_DIR="/share/weechat_downloads"
mkdir -p "$DOWNLOADS_DIR"
chmod -R 755 "$DOWNLOADS_DIR" 2>/dev/null || true

export WEECHAT_HOME="/config/weechat"
mkdir -p "$WEECHAT_HOME"
mkdir -p "$WEECHAT_HOME/python"

echo "[INFO] WeeChat home: $WEECHAT_HOME"

# Install weechat_monitor.py script automatically
echo "[INFO] Installing weechat_monitor.py script..."
if [ -f "/app/weechat_monitor.py" ]; then
    cp /app/weechat_monitor.py "$WEECHAT_HOME/python/"
    chmod 644 "$WEECHAT_HOME/python/weechat_monitor.py"
    echo "[SUCCESS] weechat_monitor.py installed to weechat's python directory"
else
    echo "[WARNING] weechat_monitor.py not found in /app/"
fi

# Ensure SUPERVISOR_TOKEN is available (it should be set by Home Assistant)
if [ -z "$SUPERVISOR_TOKEN" ]; then
    echo "[ERROR] SUPERVISOR_TOKEN not set - weechat_monitor integration will not work!"
    echo "[ERROR] This addon must run as a Home Assistant app"
    exit 1
# else
#     echo "[INFO] Supervisor token available: ${SUPERVISOR_TOKEN:0:10}... ✓"
#     echo "[INFO] Token length: ${#SUPERVISOR_TOKEN} characters"
fi

# set auto accept DCC files if configured
AUTO_ACCEPT_VALUE="off"
if [ "$AUTO_ACCEPT" = "true" ]; then
    AUTO_ACCEPT_VALUE="on"
fi

echo "[INFO] Starting WeeChat with relay configuration..."

# Export SUPERVISOR_TOKEN so it's available to WeeChat daemon
export SUPERVISOR_TOKEN

# Start WeeChat with commands to enable FIFO
env SUPERVISOR_TOKEN="$SUPERVISOR_TOKEN" weechat-headless \
    --dir "$WEECHAT_HOME" \
    --daemon \
    --run-command "/set fifo.file.enabled on;/save"

echo "[INFO] Waiting for WeeChat to initialize..."
sleep 10

# Check if weechat is running
if ! pgrep -f "weechat-headless" > /dev/null; then
    echo "[ERROR] WeeChat process is not running!"
    if [ -f "$WEECHAT_HOME/weechat.log" ]; then
        echo "[ERROR] WeeChat log:"
        tail -50 "$WEECHAT_HOME/weechat.log"
    fi
    exit 1
else
    WEECHAT_PID=$(pgrep -f "weechat-headless")
    echo "[INFO] WeeChat started with PID: $WEECHAT_PID"
fi

echo "[SUCCESS] WeeChat is running"

# Setting up settings via FIFO
FIFO_FILES=("$WEECHAT_HOME"/weechat_fifo_*)
FIFO="${FIFO_FILES[0]}"
if [ -p "$FIFO" ]; then
    echo "[INFO] Setting up user relay port and DCC via FIFO ($FIFO)..."
    {
        echo "*/set relay.network.password ${RELAY_PASS}"
        echo "*/set relay.network.allow_empty_password off"
        echo "*/relay del weechat"
        echo "*/relay add weechat ${RELAY_PORT}"
        echo "*/set xfer.file.download_path ${DOWNLOADS_DIR}"
        echo "*/set xfer.file.auto_accept_files ${AUTO_ACCEPT_VALUE}"
        echo "*/set xfer.file.use_nick_in_filename off"
        if [ "$ENABLE_MONITOR" = "true" ]; then
            echo "*/python load weechat_monitor.py"
        fi
        echo "*/save"
    } > "$FIFO"

    if [ "$ENABLE_MONITOR" = "true" ]; then
        echo "[INFO] Enabled weechat_monitor.py script for Home Assistant monitoring"
    else
        echo "[INFO] weechat_monitor.py script not enabled per configuration"
    fi

    # Give WeeChat a moment to process FIFO commands
    sleep 2
    
    # Verify relay - check for both IPv4 and IPv6
    echo "[INFO] Verifying relay..."
    for i in {1..10}; do
        # Check for port in both IPv4 (:PORT) and IPv6 (:::PORT) format
        if netstat -tlnp 2>/dev/null | grep -E "(:${RELAY_PORT}[^0-9]|:::${RELAY_PORT})"; then
            echo "[SUCCESS] ✓✓✓ Relay is listening on port $RELAY_PORT! ✓✓✓"
            
            # Show relay info in log
            if [ -f "$WEECHAT_HOME/weechat.log" ]; then
                echo "[INFO] Recent relay messages from log:"
                grep -i "relay" "$WEECHAT_HOME/weechat.log" | tail -10 || echo "[INFO] No relay messages in log yet"
            fi
            break
        fi
        
        if [ $i -eq 10 ]; then
            echo "[ERROR] Relay NOT listening after 20 seconds"
            echo "[ERROR] All ports:"
            netstat -tlnp 2>/dev/null
            echo "[ERROR] WeeChat log:"
            tail -50 "$WEECHAT_HOME/weechat.log"
            echo "[ERROR] Checking FIFO status..."
            ls -la "$WEECHAT_HOME"/weechat_fifo_* 2>/dev/null || echo "[ERROR] No FIFO found"
        else
            echo "[INFO] Attempt $i/10: waiting..."
            sleep 2
        fi
    done
else
    echo "[WARNING] FIFO pipe not found at $FIFO, cannot set up initial session"
    ls -la "$WEECHAT_HOME"/weechat_fifo_*
fi

# Monitor WeeChat process
echo "[INFO] WeeChat running, starting process monitor..."
echo "[INFO] Home Assistant integration ready!"
echo "[INFO] Download notifications will be sent to Home Assistant"

while true; do
    if ! pgrep -f "weechat-headless" >/dev/null; then
        echo "[ERROR] WeeChat process died!"
        exit 1
    fi
    sleep 3
done