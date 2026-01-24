# Home Assistant Add-ons Repository

A collection of custom Home Assistant add-ons maintained by Stulle.

## 📦 Available Add-ons

### [WeeChat](./weechat)

A headless WeeChat IRC client add-on for Home Assistant with relay support and DCC file transfer capabilities.

- **Features**: Remote IRC client via relay, file transfers, Home Assistant integration
- **Status**: Alpha
- **Architectures**: aarch64, amd64, armv7

[Read the WeeChat add-on documentation](./weechat/README.md)

## 🚀 Installation

### Add This Repository to Home Assistant

Use this button or the below steps:

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FStullemon%2Fhassio-addons)


1. Open Home Assistant and navigate to **Settings → Add-ons, Backups & Supervisor → Add-on Store**

2. Click the three-dot menu (⋯) in the top right corner

3. Select **Repositories**

4. Enter this repository URL:
   ```
   https://github.com/Stullemon/hassio-addons
   ```

5. Click **Create**

6. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)

7. The add-ons from this repository should now appear in your Add-on Store

### Install Individual Add-ons

1. Search for the desired add-on in the Add-on Store (e.g., "WeeChat")

2. Click on the add-on card

3. Click **Install**

4. Configure the add-on via the **Configuration** tab

5. Click **Start**

6. Monitor the **Logs** tab to verify successful startup

## 📋 Requirements

- Home Assistant 2024.1 or later
- Supervisor (running on HAOS or Home Assistant Container)

## 🔒 Security

These add-ons follow Home Assistant's security guidelines:

- All add-ons run in isolated containers
- Network and storage access is restricted to configured mounts/ports
- No access to the Home Assistant core or other containers by default
- Code is open-source for community review

⚠️ **Important**: Always review the configuration and security settings for each add-on before using in production, especially those that expose network services.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-addon`)
3. Test your changes thoroughly
4. Submit a pull request with a clear description

## 📝 License

All add-ons in this repository are licensed under the [MIT License](./LICENSE) unless otherwise specified.

## ⚠️ Disclaimer

These add-ons are provided as-is without warranty. Users are responsible for:

- Securing their add-on configurations (especially passwords and API tokens)
- Regular backups of their Home Assistant data
- Keeping add-ons and Home Assistant updated
- Understanding the implications of exposing network services

## 🐛 Support & Issues

- **Report Issues**: https://github.com/Stullemon/hassio-addons/issues
- **Discussions**: https://github.com/Stullemon/hassio-addons/discussions
- **Home Assistant Community**: https://community.home-assistant.io/

## 📚 Resources

- [Home Assistant Add-ons Documentation](https://developers.home-assistant.io/docs/add-ons)
- [Home Assistant Supervisor Documentation](https://github.com/home-assistant/supervisor/wiki)
- [Home Assistant Community Forums](https://community.home-assistant.io/)

---

**Repository maintained by**: [@Stullemon](https://github.com/Stullemon)
