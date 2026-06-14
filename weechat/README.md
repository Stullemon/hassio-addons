# WeeChat App for Home Assistant

![Project Status](https://img.shields.io/badge/status-beta-orange)
![License](https://img.shields.io/badge/license-MIT-green)

A headless [WeeChat](https://weechat.org/) IRC client app for Home Assistant with relay support and file transfer capabilities. Run your IRC client continuously and interact with it remotely via the WeeChat relay protocol.

Current WeeChat version: **v4.9.2** (App version 0.1.4)

## Features

- **Headless WeeChat IRC Client**: Runs persistently in the background as a Home Assistant service
- **Relay Protocol**: Connect to WeeChat remotely using any relay-compatible client (WeeChat-Android, Glowingbear, etc.)
- **DCC File Transfers**: Automatic file download support with Home Assistant integration
- **Home Assistant Integration**: Downloads logged to `/config/weechat/dcc_history.log`
- **Multi-Architecture Support**: Works on aarch64, amd64, and armv7 architectures
- **Host Networking**: Direct network access for IRC and relay protocols
- **Home Assistant Supervisor Integration**: Automatic authentication via Supervisor API for notifications

## Installation

1. Navigate to **Settings → Apps → Install app**
2. Click the three-dot menu (⋯) in the top right corner
3. Select **Repositories**
4. Add this URL: `https://github.com/Stullemon/hassio-addons`
5. Click **Create**
6. Refresh the page (Ctrl+F5 or Cmd+Shift+R)
7. Search for "WeeChat" in the App Store
8. Click **Install**

## Configuration

Configure the app through the **Configuration** tab in the app details:

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `relay_port` | integer | `9001` | Port for the WeeChat relay server (0-65535). Make sure this port is not in use. |
| `relay_password` | string | `superstrongpassword` | Password for relay authentication. **Change this before enabling remote access!** |
| `auto_accept_dcc` | boolean | `false` | Automatically accept incoming DCC file transfers without prompting |
| `enable_monitor_script` | boolean | `false` | Enable the weechat_monitor script to send irc server/channel/chat counters and download notifications to Home Assistant |

⚠️ **Important**: weechat_monitor script requires installation of [WeeChat Monitor custom component](https://github.com/Stullemon/hassio-weechat-integration).

### Example Configuration

```yaml
relay_port: 9001
relay_password: my_secure_password_here
auto_accept_dcc: true
enable_monitor_script: true
```

## Usage

### Starting WeeChat

1. Go to **Settings → Apps**
2. Find **WeeChat** in the list
3. Click **Start**
4. Check the **Logs** tab to monitor startup

### Connecting via Relay

WeeChat relay listens on the configured port (default `9001`). You can connect using:

- **WeeChat Relay clients**: WeeChat-Android, Glowingbear, etc.
- **Manual connection**: `weechat-relay <hostname>:<port>`

Use the configured `relay_password` to authenticate.

### File Downloads

- **Download Path**: `/share/weechat_downloads` (maps to Home Assistant's `/share` via Samba)
- **Auto-Accept**: When enabled, DCC files are automatically accepted
- **Monitor Script**: When enabled, completed downloads trigger notifications to Home Assistant (requires [WeeChat Monitor custom component](https://github.com/Stullemon/hassio-weechat-integration))
- **Download Log**: View all completed downloads in `/config/weechat/dcc_history.log`

### Accessing Downloads

Downloads are stored in the Home Assistant `/share` directory:
- **Via Samba**: `\\<homeassistant>/share/weechat_downloads/`
- **Via Home Assistant UI**: Media → Share folder (if using Samba app)
- **Via SSH**: `/share/weechat_downloads/`

## Data Persistence

The app stores all data in `/config/weechat/`:
- **weechat.conf**: Main configuration file (auto-created on first run)
- **weechat.log**: Debug logs
- **python/**: Python scripts directory (weechat_monitor.py is auto-installed here)
- **dcc_history.log**: Download history (if monitor script enabled)

All data persists across restarts and updates.

⚠️ **Important**: weechat_monitor.py in Python script directory will automatically reset to build version upon start of app. Do not attempt to override directly (use new scripts or fork app instead).

## Security Considerations

⚠️ **Important**: This appuses `host_network: true` for IRC relay access.

- **Change the default relay password immediately** before enabling remote access
- Use a **strong, unique password** (20+ characters recommended)
- Restrict relay access to your internal network when possible
- Use a **VPN or firewall rules** if exposing the relay to the internet
- Monitor the logs for suspicious connection attempts
- Keep Home Assistant and the app updated for security patches

## Troubleshooting

### WeeChat Won't Start

Check the **Logs** tab for error messages. Common issues:

- **"SUPERVISOR_TOKEN not set"**: Ensure the app is running within Home Assistant (not manually in Docker)
- **Port already in use**: Change `relay_port` to an available port
- **Build failures**: Ensure your Home Assistant instance has enough disk space

### Relay Not Connecting

- Verify the relay port is listening: check app logs
- Ensure firewall allows connections to the relay port
- Try connecting from the same machine first to rule out network issues
- Check relay credentials (password, port number)

### DCC Not Working

- Ensure DCC protocol is supported in your IRC network
- Check that `/share` directory is accessible and writable
- Enable `auto_accept_dcc` if you want automatic acceptance
- Monitor the WeeChat logs for xfer-related errors

### Downloads Not Appearing in Home Assistant

- Verify `enable_monitor_script` is enabled
- Check that the weechat_monitor custom component is installed in Home Assistant
- Review logs for "weechat_monitor" messages
- Ensure `/config/weechat/dcc_history.log` is being created

## Development

### Building Locally

```bash
# This app is built using Home Assistant's build system
# For local development, use Home Assistant dev container or build scripts
```

### File Structure

```
weechat/
├── config.yaml          # App metadata and configuration schema
├── build.yaml           # Multi-architecture build configuration
├── Dockerfile           # Multi-stage build for WeeChat from source
├── run.sh               # Startup script and service orchestration
├── README.md            # This file
├── weechat_monitor.py   # WeeChat Python script for HA integration
└── translations/
    └── en.yaml          # Configuration translations
```

## License

This app is licensed under the [MIT License](../LICENSE).

## Disclaimer

- WeeChat is a registered trademark of its respective owners
- This app is not affiliated with the WeeChat project
- This app is provided as-is without warranty
- This app was created in part with the help of ChatGPT and Claude Sonnet
- Use at your own risk

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: https://github.com/Stullemon/hassio-addons/issues
- **GitHub Discussions**: https://github.com/Stullemon/hassio-addons/discussions

## Credits

- [WeeChat Project](https://weechat.org/)
- [Home Assistant](https://www.home-assistant.io/)
- [Home Assistant Community](https://community.home-assistant.io/)