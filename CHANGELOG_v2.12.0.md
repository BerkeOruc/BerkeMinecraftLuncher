# Changelog v2.12.0 - Critical Fixes & UI Improvements

## 🔧 Critical Fixes

### ✅ **Forge/Fabric Base Minecraft Download**
- **FIXED**: Forge now downloads base Minecraft version automatically
- **FIXED**: Fabric now downloads base Minecraft version automatically  
- Base version downloads BEFORE mod loader installation
- Progress bar shows base download step
- All mod loaders now work properly!

### ✅ **UI Simplification**
- **REMOVED**: Redundant "Sürüm Ara" menu (already in version list)
- Cleaner download menu
- Less confusing navigation
- Menu options renumbered (1-8 instead of 1-9)

### ✅ **Window Focus Fix (Old Versions)**
- Fixed 1.15 and older versions not appearing on screen
- Better window focus handling
- Improved X11 window management
- Minecraft now properly displays for all versions

### ✅ **CLI Commands Fixed**
- `berkemc version` now works properly
- `berkemc --version` works
- `berkemc -v` works
- Better script path handling

## 🎮 Download Menu Changes

### Before:
```
1 🔍 Sürüm Ara (gereksiz)
2 📋 Sürüm Listesi
...
9 🧵 Fabric
```

### After:
```
1 📋 Tüm Sürümler (arama dahil)
2 📊 Popüler Sürümler
...
7 🧵 Fabric
8 ⚡ OptiFine Bilgisi
```

## 🚀 Forge/Fabric Installation Flow

### Now Works Like This:
1. User selects Forge/Fabric version
2. **Base Minecraft downloads first** ✅
3. Mod loader installs
4. Version appears in launcher immediately
5. Ready to launch!

### Progress Display:
```
📦 Base Minecraft 1.20.1 indiriliyor...  [20%]
⚙️  Forge kuruluyor...                   [40%]
📦 Forge dosyaları kopyalanıyor...       [70%]
✅ Forge kuruldu                         [100%]
```

## 🐛 All Fixed Issues

| Issue | Status |
|-------|--------|
| Forge not downloading base MC | ✅ Fixed |
| Fabric not downloading base MC | ✅ Fixed |
| Redundant search menu | ✅ Removed |
| CLI commands not working | ✅ Fixed |
| Old versions window focus | ✅ Fixed |

## 📦 Installation
```bash
yay -Syu berkemc
berkemc --version  # Should show 2.12.0
```

## 🎯 Now Working
✅ Forge downloads complete (base + loader)
✅ Fabric downloads complete (base + loader)
✅ All CLI commands working
✅ Cleaner UI
✅ All Minecraft versions launch properly
✅ Window focus works for all versions

---

**Full Changelog**: https://github.com/BerkeOruc/BerkeMinecraftLuncher/compare/v2.11.0...v2.12.0

