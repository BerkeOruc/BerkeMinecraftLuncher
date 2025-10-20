# Changelog v2.6.0 - Mod Loader & Asset Fix Update

## 🎮 Major Improvements

### ✅ Fixed Critical Issues
- **Asset Path Fixed**: Assets now correctly load from `~/.minecraft/assets` instead of `/home/user/assets`
- **Asset Download System**: Added comprehensive parallel asset downloading with progress tracking
- **Fabric Installation**: Fabric now properly installs and appears in version list
- **Forge Installation**: Forge installation improved with better error handling

### 🚀 New Features

#### Automatic Asset Management
- **Asset Verification**: Automatic asset integrity check before launch
- **Asset Repair**: Auto-download missing assets with progress bar
- **Parallel Downloads**: Ultra-fast asset downloads using 16 parallel threads
- **Smart Caching**: Only downloads missing assets, uses cache for existing ones

#### Enhanced Mod Loader Support
- **Forge Auto-Install**: Full Forge installer with progress tracking
  - Automatic base version download
  - Proper JAR file installation
  - Version appears in launcher immediately
- **Fabric Auto-Install**: Complete Fabric loader installation
  - Library downloads with progress bar
  - Proper version ID formatting: `fabric-loader-{version}-{mc_version}`
  - Instant availability in version list

#### Progress Indicators
- **Download Progress Bars**: Visual progress for all downloads
  - Asset downloads with speed indicators
  - Forge installer with step-by-step progress
  - Fabric installation with detailed stages
- **Real-time Feedback**: Clear status messages during installation

### 🔧 Technical Improvements
- Better error handling for mod loader installations
- Improved version detection for installed mod loaders
- Enhanced library management for Fabric
- Proper JAR file copying for both Forge and Fabric
- launcher_profiles.json auto-creation for compatibility

### 📦 Installation
```bash
yay -S berkemc
```

### 🐛 Bug Fixes
- Fixed Mojang loading screen crash (asset path issue)
- Fixed Fabric versions not appearing in launcher
- Fixed Forge installation not completing properly
- Fixed missing progress indicators during downloads
- Fixed asset download failures

### 🎯 Performance
- 16-thread parallel downloads for assets (ultra fast!)
- Efficient caching system reduces redundant downloads
- Optimized library management

---

**Full Changelog**: https://github.com/BerkeOruc/BerkeMinecraftLuncher/compare/v2.5.2...v2.6.0

