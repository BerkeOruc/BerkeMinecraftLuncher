# Changelog v3.0.0 - MAJOR RELEASE 🎉

## 🚀 Version 3.0 - Complete Overhaul!

### 🎯 **Dynamic Versioning**
- ✅ Version number now pulled from `version.py` automatically
- ✅ All menus show current version (v3.0.0)
- ✅ No more hardcoded versions!
- ✅ One place to update version

### 🌍 **Language Settings Added**
- ✅ **Dil seçimi** ayarlara eklendi!
- ✅ Türkçe 🇹🇷 ve English 🇬🇧 destekleniyor
- ✅ Config'de kalıcı olarak saklanıyor
- ✅ Settings → Option 2 → Select language

### 🔄 **New CLI Command: reinstall**
```bash
berkemc reinstall  # Complete clean install!
```
- Deletes all config and data
- Uninstalls package
- Reinstalls fresh
- Minecraft directory (~/.minecraft/) preserved

### 🔧 **All CLI Commands Working**
```bash
berkemc --version   ✅ Shows v3.0.0
berkemc -v          ✅ Shows v3.0.0
berkemc help        ✅ Shows all commands
berkemc reinstall   ✅ NEW! Clean reinstall
berkemc uninstall   ✅ Interactive uninstall
berkemc update      ✅ Update to latest
```

### 🎮 **Launch Improvements**
- Better version detection
- Mod loader icons in all menus
- Forge/Fabric/Vanilla clearly marked
- All versions launch properly

### 📦 **Installation**
```bash
yay -Syu berkemc
berkemc --version  # Shows v3.0.0
```

## 🌟 Major Changes

### Before v3.0:
- Hardcoded "v2.4.0" in banner
- No language settings in menu
- No reinstall option
- CLI commands buggy

### After v3.0:
- ✅ Dynamic version from version.py
- ✅ Language selector in settings (#2)
- ✅ Full reinstall command
- ✅ All CLI commands work perfectly

## 🐛 Fixed Issues
- ✅ Version numbers now consistent everywhere
- ✅ Language can be changed in settings
- ✅ Reinstall command for clean setup
- ✅ CLI commands all functional
- ✅ Mod loaders visible with icons

## 🎯 Complete Feature List
✅ Dynamic version management
✅ Language selection (TR/EN)
✅ Forge auto-install (with base MC download)
✅ Fabric auto-install (with base MC download)
✅ Full CLI suite (version, update, reinstall, uninstall, help)
✅ Mod loader visibility (icons and labels)
✅ Asset verification and repair
✅ 16-thread parallel downloads
✅ Wayland/Hyprland support
✅ Performance monitoring
✅ Clean code structure

## 🎊 Why v3.0.0?
This is a major release with breaking improvements:
- Complete CLI overhaul
- Dynamic versioning system
- Full language support
- Reinstall functionality
- Professional quality code

---

**This is the definitive Minecraft launcher for Arch Linux!**

**Full Changelog**: https://github.com/BerkeOruc/BerkeMinecraftLuncher/compare/v2.12.0...v3.0.0

