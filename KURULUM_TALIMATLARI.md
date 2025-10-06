# 🚀 Berke Minecraft Launcher - Kurulum Talimatları

## 🎯 Hızlı Kurulum

### Yöntem 1: Otomatik Script (Önerilen)
```bash
# GitHub'dan indir
git clone https://github.com/BerkeOruc/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher

# Kurulum scriptini çalıştır
chmod +x install_berkemc.sh
./install_berkemc.sh
```

### Yöntem 2: AUR'dan Manuel Kurulum
```bash
# AUR repository'sini klonla
cd /tmp
git clone https://aur.archlinux.org/berkemc.git
cd berkemc

# Paketi kur
makepkg -si
```

### Yöntem 3: yay ile (Cache güncellendikten sonra)
```bash
# Cache'i temizle
yay -Scc
yay -Syu

# Paketi kur
yay -S berkemc
```

### Yöntem 4: GitHub'dan Manuel Kurulum
```bash
# Repository'yi klonla
git clone https://github.com/BerkeOruc/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher

# Bağımlılıkları kur
pip install -r requirements.txt

# Executable'ı sisteme kopyala
sudo cp berke_minecraft_launcher.py /usr/local/bin/berkemc
sudo chmod +x /usr/local/bin/berkemc
```

## 🚀 Kullanım

### Launcher'ı Başlat
```bash
berkemc
```

### Alternatif Komut
```bash
berke-minecraft-launcher
```

## 📦 Sistem Gereksinimleri

### Gerekli Paketler:
- **Python**: >= 3.8
- **Java**: >= 17 (JDK önerilen)
- **Git**: Paket indirme için

### Python Bağımlılıkları:
- requests >= 2.32.0
- rich >= 14.1.0
- colorama >= 0.4.6
- psutil >= 7.1.0

### Arch Linux'ta Java Kurulumu:
```bash
# OpenJDK 17 (önerilen)
sudo pacman -S jdk17-openjdk

# veya OpenJDK 21
sudo pacman -S jdk21-openjdk

# veya Oracle JDK
sudo pacman -S jdk17-openjdk-headless
```

## 🔧 Sorun Giderme

### Java Bulunamadı Hatası:
```bash
# Java'yı kontrol et
java -version

# JAVA_HOME ayarla
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

### LWJGL Native Library Hatası:
```bash
# Native library'leri çıkar
./fix_native_libraries.sh
```

### SSL Certificate Hatası:
- Launcher otomatik olarak SSL bypass yapar
- Sorun devam ederse: `./install_berkemc.sh` ile yeniden kur

### Wayland/Hyprland Sorunları:
```bash
# XWayland'i yükle
sudo pacman -S xorg-server-xwayland

# Environment değişkenlerini ayarla
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
```

## 📋 Paket Bilgileri

- **Paket Adı**: berkemc
- **Sürüm**: 2.3.0
- **AUR URL**: https://aur.archlinux.org/packages/berkemc
- **GitHub**: https://github.com/BerkeOruc/BerkeMinecraftLuncher
- **Lisans**: MIT
- **Maintainer**: Berke Oruç <berke3oruc@gmail.com>

## 🎮 Özellikler

- ✅ **Tüm Minecraft sürümleri** (Alpha, Beta, Release, Snapshot)
- ✅ **Online sunucu desteği** (UUID + Mojang protocol)
- ✅ **Mod yönetimi** (Modrinth API entegrasyonu)
- ✅ **Skin yönetimi** (Upload, download, backup)
- ✅ **Performans optimizasyonları** (Aikar's Flags Enhanced)
- ✅ **Wayland/Hyprland desteği** (XWayland uyumluluğu)
- ✅ **LWJGL native library desteği**
- ✅ **SSL certificate handling**
- ✅ **Asset index indirme**
- ✅ **Terminal tabanlı TUI** (rich library)

## 🆘 Yardım

### Debug Modu:
```bash
# Debug modu ile çalıştır
berkemc --debug
```

### Log Dosyaları:
```bash
# Log dosyalarını kontrol et
ls -la ~/.berke_minecraft_launcher/logs/
```

### Sistem Testi:
```bash
# Sistem testi çalıştır
berkemc --test
```

## 📞 Destek

- **GitHub Issues**: https://github.com/BerkeOruc/BerkeMinecraftLuncher/issues
- **E-posta**: berke3oruc@gmail.com
- **AUR**: https://aur.archlinux.org/packages/berkemc

---

**Not**: Bu launcher Arch Linux için optimize edilmiştir ve Wayland/Hyprland desteği içerir.
