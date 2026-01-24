# -*- coding: utf-8 -*-
#
# weechat_monitor.py — Notify Home Assistant via Supervisor API on completed DCC downloads
#
# Hooks WeeChat's xfer system. On completed downloads:
#  - Calls Home Assistant via Supervisor API (automatic authentication)
#  - Logs file name, size, timestamp to dcc_history.log

import weechat
import os
import json
import time
import urllib.request

SCRIPT_NAME = "weechat_monitor"
SCRIPT_AUTHOR = "Stulle"
SCRIPT_VERSION = "0.1.2"
SCRIPT_LICENSE = "MIT"
SCRIPT_DESC = "WeeChat-side of WeeChat_Monitor Integration for Home Assistant via Supervisor API"

# -------------------------
# Configuration
# -------------------------

# Local log file for completed downloads
LOG_FILE = "/config/weechat/dcc_history.log"

# Supervisor API endpoint (automatic authentication via SUPERVISOR_TOKEN)
SUPERVISOR_URL = "http://supervisor/core/api"

# DOMAIN for Home Assistant services
DOMAIN = "weechat"

# Timer interval between updates to Home Assistant (in seconds)
# Set to 60 and use alignment so updates happen at each minute at 0s
UPDATE_INTERVAL_SECONDS = 60  # 60 seconds = 1 minute

# -------------------------
# Global state for error suppression
# -------------------------

api_suppressed = False
api_404_logged = False

# -------------------------

def log(msg):
    """Print to weechat."""
    weechat.prnt("", f"weechat_monitor: {msg}")

def ensure_log_file():
    directory = os.path.dirname(LOG_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write("# timestamp,file,size_bytes,local_filename\n")

def append_log(timestamp, filename, size_bytes, local_filename):
    ensure_log_file()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},{filename},{size_bytes},{local_filename}\n")

def notify_home_assistant(service, payload, suppress_on_404=False):
    """Call Home Assistant via Supervisor API.
    
    Args:
        service: The service name to call
        payload: The data to send
        suppress_on_404: If True, enables suppression mode on 404 errors
    
    Returns:
        True if successful, False otherwise
    """
    global api_suppressed, api_404_logged
    
    # If suppressed, skip silently
    if api_suppressed:
        return False
    
    # Get Supervisor token from environment (automatically available in add-ons)
    supervisor_token = os.environ.get('SUPERVISOR_TOKEN')
    
    if not supervisor_token:
        log("ERROR: SUPERVISOR_TOKEN not found in environment")
        return False
    
    url = f"{SUPERVISOR_URL}/services/{DOMAIN}/{service}"
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {supervisor_token}"
        }
    )
    
    try:
        response = urllib.request.urlopen(req, timeout=10)
        response_data = response.read().decode('utf-8')
        
        # Success - clear suppression if it was active
        if api_suppressed:
            api_suppressed = False
            api_404_logged = False
            log("✓ Connection to HA restored - resuming notifications")
        
        if service == "register_download":
            filename = payload.get("filename", "unknown")
            size_bytes = payload.get("size_bytes", 0)
            log(f"✓ Notified HA register_download: {filename} ({_format_bytes(size_bytes)})")
        
        return True
        
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8', errors='ignore')
        
        if e.code == 404:
            # Handle 404 with suppression logic
            if suppress_on_404:
                if not api_404_logged:
                    log(f"HTTP Error 404: {error_msg}")
                    log("ERROR: Service not found - is weechat_monitor integration loaded in HA?")
                    log("Suppressing further API calls until connection is restored")
                    api_404_logged = True
                api_suppressed = True
            else:
                # For non-suppressing calls, still log once
                if not api_404_logged:
                    log(f"HTTP Error 404: {error_msg}")
                    log("ERROR: Service not found - is weechat_monitor integration loaded in HA?")
        elif e.code == 500:
            log(f"HTTP Error {e.code}: {error_msg}")
            log("ERROR: Home Assistant internal error - check HA logs")
            log("This may be due to database or integration errors")
        else:
            log(f"HTTP Error {e.code}: {error_msg}")
        
        return False
        
    except urllib.error.URLError as e:
        log(f"Connection error: {e.reason}")
        log("Cannot reach Home Assistant - is it running?")
        return False
        
    except Exception as e:
        log(f"Notification error: {type(e).__name__}: {e}")
        return False

def _format_bytes(bytes_val):
    """Format bytes to human readable."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def xfer_ended(data, signal, signal_data):
    """Handle completed transfers."""
    if not signal_data:
        return weechat.WEECHAT_RC_OK

    while weechat.infolist_next(signal_data):
        status = weechat.infolist_integer(signal_data, "status")
        filename = weechat.infolist_string(signal_data, "filename")
        filename_suffix = weechat.infolist_integer(signal_data, "filename_suffix")
        filename_suffix = filename_suffix if filename_suffix is not None else -1
        local_filename = weechat.infolist_string(signal_data, "local_filename")
        
        # Get size - try as integer first, then string
        try:
            size_str = weechat.infolist_string(signal_data, "size")
            size = int(size_str) if size_str else 0
        except:
            size = 0
        
        # status 3 = done, only process successful downloads with valid data
        if status == 3 and filename and size > 0:
            timestamp = int(time.time())
            if filename_suffix > 0:
                log(f"Completed (Duplicate .{filename_suffix}): {filename} ({_format_bytes(size)})")
            else:
                log(f"Completed: {filename} ({_format_bytes(size)})")
            
            # Log locally
            append_log(timestamp, filename, size, local_filename)
            
            # Notify Home Assistant (no suppression flag - respects global suppression)
            payload = {
                "filename": filename,
                "size_bytes": size,
                "timestamp": int(time.time()),
                "filename_suffix": filename_suffix
            }
            notify_home_assistant("register_download", payload, suppress_on_404=False)
        elif status == 3:
            log(f"Skipped completed transfer: {filename} (size={size}, may be invalid)")
    
    return weechat.WEECHAT_RC_OK

def update_counts(data, remaining_calls):
    """Fetch IRC stats and notify Home Assistant."""
    servers = weechat.infolist_get("irc_server", "", "")
    total_servers = 0
    connected_servers = 0
    total_channels = 0
    total_private_chats = 0
    
    if servers:
        while weechat.infolist_next(servers):
            total_servers += 1
            connected = weechat.infolist_integer(servers, "is_connected")
            if not connected is None and connected != 0:
                connected_servers += 1
            
            server_name = weechat.infolist_string(servers, "name")
            channels = weechat.infolist_get("irc_channel", "", f"{server_name}")
            if channels:
                while weechat.infolist_next(channels):
                    type = weechat.infolist_integer(channels, "type")
                    if not type is None:
                        if type == 0:  # type 0 = channel, type 1 = private chat
                            total_channels += 1
                        else:
                            total_private_chats += 1
                weechat.infolist_free(channels)
            
        weechat.infolist_free(servers)
    
    payload = {
        "total_servers": total_servers,
        "connected_servers": connected_servers,
        "total_channels": total_channels,
        "total_private_chats": total_private_chats,
        "alive": True,
        "timestamp": int(time.time()),
    }
    # Enable suppression on 404 from update_counts
    notify_home_assistant("update_counts", payload, suppress_on_404=True)
    
    return weechat.WEECHAT_RC_OK

def send_zero_counts():
    """Send all zero counts to Home Assistant on shutdown."""
    global api_suppressed
    
    # Temporarily disable suppression for shutdown
    was_suppressed = api_suppressed
    api_suppressed = False
    
    payload = {
        "total_servers": 0,
        "connected_servers": 0,
        "total_channels": 0,
        "total_private_chats": 0,
        "alive": False,
        "timestamp": int(time.time()),
    }
    
    log("Sending zero counts to HA on shutdown...")
    success = notify_home_assistant("update_counts", payload, suppress_on_404=False)
    
    if not success and not was_suppressed:
        log("Failed to send shutdown counts to HA")
    
    # Restore suppression state (though we're shutting down anyway)
    api_suppressed = was_suppressed

def shutdown_register():
    """Called when script is unloaded."""
    send_zero_counts()
    return weechat.WEECHAT_RC_OK

def shutdown_callback(data, signal, signal_data):
    """Called when WeeChat is shutting down."""
    send_zero_counts()
    return weechat.WEECHAT_RC_OK

# -------------------------
# Initialize
# -------------------------

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE,
                    SCRIPT_DESC, "shutdown_register", ""):
    
    weechat.hook_signal("xfer_ended", "xfer_ended", "")
    weechat.hook_timer(UPDATE_INTERVAL_SECONDS * 1000, 60, 0, "update_counts", "")
    weechat.hook_signal("quit", "shutdown_callback", "")
    
    # Check if Supervisor token is available
    if os.environ.get('SUPERVISOR_TOKEN'):
        log("Loaded! Using Supervisor API (automatic authentication)")
    else:
        log("WARNING: SUPERVISOR_TOKEN not found - notifications will fail")
        log("This script requires running inside a Home Assistant add-on")