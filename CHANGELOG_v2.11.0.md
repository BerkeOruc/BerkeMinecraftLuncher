# Changelog v2.11.0 - Mod Loader Visibility & Stability

## 🎮 Major Improvements

### ✅ **Mod Loader Visibility**
- ⚒️  **Forge** versions now show with icon and label
- 🧵 **Fabric** versions now show with icon and label  
- ⭐ **Vanilla** versions clearly marked
- 🎨 **Quilt** support added
- **All mod loaders visible** in launch menu!

### 🔧 **Launch Menu Improvements**
- Mod loader type shown for each version
- Better version display (25 chars width)
- Handles versions with custom JAR names
- Color-coded loader types
- Size information for all versions

### 📊 **Progress Indicators**
- Forge installation already has progress bar ✅
- Fabric installation already has progress bar ✅
- Asset downloads show progress ✅
- All downloads tracked properly ✅

### 🐛 **Bug Fixes**
- Fixed versions with non-standard JAR names
- Improved JAR file detection
- Better mod loader type detection
- Enhanced version list display

## 🎯 What You'll See Now

### Launch Menu:
```
1  1.21.1                    ⭐ Vanilla    45 MB
2  1.20.1-forge-47.2.0      ⚒️  Forge     52 MB
3  fabric-loader-0.15-1.20  🧵 Fabric    48 MB
4  1.19.4                    ⭐ Vanilla    42 MB
```

### Progress Bars:
- ✅ Forge: Shows installation steps with percentage
- ✅ Fabric: Shows download and installation progress
- ✅ Assets: Shows parallel download progress
- ✅ Libraries: Shows download count and speed

## 📦 Installation
```bash
yay -Syu berkemc
berkemc --version  # Should show 2.11.0
```

## 🚀 All Features Working
✅ Mod loaders visible everywhere
✅ Progress bars for all downloads
✅ Proper version detection
✅ All launcher types supported
✅ Clean, beautiful display

---

**Full Changelog**: https://github.com/BerkeOruc/berkemc/compare/v2.10.0...v2.11.0

