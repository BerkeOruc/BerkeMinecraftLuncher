# Changelog v2.7.0 - CLI Commands & Mod Loader Fixes

## 🚀 Major Updates

### ✅ Critical Fixes
- **Mod Versions Now Visible**: Forge and Fabric versions now appear in version list
- **Version Detection Improved**: Better JAR file detection for all mod loaders
- **Mod Loader Installation**: Fixed installation issues

### 🎯 New CLI Commands
```bash
berkemc --version, -v      # Show version information
berkemc version            # Alternative version command
berkemc uninstall          # Uninstall BerkeMC with confirmation
berkemc update             # Update to latest version
berkemc help, -h           # Show help menu
```

#### Uninstall Feature
- Interactive uninstall process with confirmation
- Option to keep or remove config files
- Minecraft directory (~/.minecraft/) is preserved
- Clean removal of all BerkeMC files

### 🌍 Repository Rebrand
- Repository name changed from `BerkeMinecraftLuncher` to `berkemc`
- All URLs updated to reflect new name
- Cleaner, more professional naming
- New GitHub URL: `https://github.com/BerkeOruc/berkemc`

### 🔧 Technical Improvements
- Enhanced version detection algorithm
- Support for custom JAR filenames
- Better Forge/Fabric version handling
- Improved mod loader compatibility

### 📦 Installation
```bash
yay -S berkemc
```

### 🐛 Bug Fixes
- Fixed Forge versions not showing in launcher
- Fixed Fabric versions not appearing in mod list
- Fixed version list only showing vanilla versions
- Fixed CLI commands not working properly

### 🎨 I18n System
- Full multi-language support system already integrated
- Turkish and English translations included
- Ready for additional language packs
- Language can be changed in settings

---

**Previous Version**: v2.6.0
**Full Changelog**: https://github.com/BerkeOruc/berkemc/compare/v2.6.0...v2.7.0

