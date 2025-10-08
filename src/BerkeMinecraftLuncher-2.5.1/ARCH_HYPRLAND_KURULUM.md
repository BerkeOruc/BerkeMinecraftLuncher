# 🎮 Berke Minecraft Launcher - Arch Linux + Hyprland Kurulumu

## 📋 Gereksinimler (Otomatik Kontrol Edilir)

### Temel Paketler
```bash
# Java (17, 21 veya 25)
sudo pacman -S jdk-openjdk jdk21-openjdk jdk17-openjdk

# Eski Minecraft sürümleri için Java 8
sudo pacman -S jdk8-openjdk

# Python bağımlılıkları
sudo pacman -S python python-requests python-rich python-colorama python-psutil

# XWayland (Hyprland için ZORUNLU)
sudo pacman -S xorg-server-xwayland

# Opsiyonel: Text-to-speech desteği
sudo pacman -S flite
```

### AUR'dan Kurulum (Önerilen)
```bash
yay -S berkemc
```

### Manuel Kurulum
```bash
git clone https://github.com/berke0/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher
pip install -r requirements.txt
python berke_minecraft_launcher.py
```

## 🖥️ Hyprland Yapılandırması

### 1. Hyprland Config (~/.config/hypr/hyprland.conf)

```conf
# Minecraft için pencere kuralları
windowrulev2 = float,class:(Minecraft)
windowrulev2 = center,class:(Minecraft)
windowrulev2 = size 1280 720,class:(Minecraft)
windowrulev2 = workspace 2,class:(Minecraft)

# Java uygulamaları için
windowrulev2 = float,class:(java)
windowrulev2 = center,class:(java)

# XWayland optimizasyonu
env = GDK_BACKEND,x11
env = QT_QPA_PLATFORM,xcb
env = SDL_VIDEODRIVER,x11
env = _JAVA_AWT_WM_NONREPARENTING,1

# OpenGL performans
env = __GL_THREADED_OPTIMIZATIONS,1
env = MESA_GL_VERSION_OVERRIDE,4.5
env = MESA_GLSL_VERSION_OVERRIDE,450
```

### 2. Java Kurulumu ve Seçimi

```bash
# Tüm Java sürümlerini listele
archlinux-java status

# Java 21 seç (modern Minecraft için)
sudo archlinux-java set java-21-openjdk

# Java 8 seç (eski sürümler için)
sudo archlinux-java set java-8-openjdk

# Mevcut Java'yı kontrol et
java -version
```

## 🚀 Hızlı Başlangıç

### 1. Launcher'ı Başlat
```bash
berkemc
# veya
python berke_minecraft_launcher.py
```

### 2. İlk Kurulum
1. **Java Yönetimi** → Uygun Java sürümünü seç
2. **Sürüm İndir** → İstediğin Minecraft sürümünü indir
3. **Minecraft Başlat** → Oyunu başlat
4. ✅ **Kaynak İzleme** menüsü otomatik açılır

## 🎯 Minecraft Sürümleri ve Java

| Minecraft Sürümü | Önerilen Java | Komut |
|------------------|---------------|-------|
| 1.21+ | Java 21 | `sudo archlinux-java set java-21-openjdk` |
| 1.18 - 1.20 | Java 17 | `sudo archlinux-java set java-17-openjdk` |
| 1.17 | Java 17 | `sudo archlinux-java set java-17-openjdk` |
| 1.12 - 1.16 | Java 8 | `sudo archlinux-java set java-8-openjdk` |
| 1.7 - 1.11 | Java 8 | `sudo archlinux-java set java-8-openjdk` |
| Alpha/Beta/Classic | Java 8 | `sudo archlinux-java set java-8-openjdk` |

## 🔧 Sorun Giderme

### Minecraft Başlamıyor

1. **Java sürümünü kontrol et:**
```bash
java -version
```

2. **XWayland çalışıyor mu:**
```bash
pgrep -a Xwayland
```

3. **Log dosyalarını incele:**
```bash
tail -f ~/.berke_minecraft_launcher/logs/minecraft_*.log
```

4. **Java 8 kur (eski sürümler için):**
```bash
sudo pacman -S jdk8-openjdk
sudo archlinux-java set java-8-openjdk
```

### Pencere Açılmıyor

1. **Hyprland config'i kontrol et:**
```bash
cat ~/.config/hypr/hyprland.conf | grep -A 5 "Minecraft"
```

2. **Environment variables'ı kontrol et:**
```bash
env | grep -E "DISPLAY|WAYLAND|GDK|QT|SDL"
```

3. **XWayland'i yeniden başlat:**
```bash
killall Xwayland
# Hyprland otomatik yeniden başlatır
```

### ClassCastException Hatası

Bu hata eski Minecraft sürümlerinde modern Java kullandığınızda çıkar:
```bash
# Çözüm: Java 8 kur
sudo pacman -S jdk8-openjdk
sudo archlinux-java set java-8-openjdk
```

## 🎨 Mod Loader Kurulumu

### Forge
```bash
# Launcher'dan
Mod Yönetimi → Forge/Fabric Kur → Forge
```

### Fabric
```bash
# Launcher'dan
Mod Yönetimi → Forge/Fabric Kur → Fabric
```

### Modlar
Modları `~/.minecraft/mods/` klasörüne at:
```bash
cp mod.jar ~/.minecraft/mods/
```

## 📊 Performans Optimizasyonu

### GPU İzleme (AMD)
```bash
sudo pacman -S radeontop
radeontop
```

### GPU İzleme (NVIDIA)
```bash
sudo pacman -S nvidia-utils
nvidia-smi
```

### CPU İzleme
```bash
htop
```

## 📝 Debug Modu

Ayarlar → Debug Modu → Aç

Log dosyaları:
- `~/.berke_minecraft_launcher/logs/minecraft_*.log`
- `~/.berke_minecraft_launcher/logs/latest.log`

## 🆘 Destek

GitHub Issues: https://github.com/berke0/BerkeMinecraftLuncher/issues

## ✨ Özellikler

- ✅ Hyprland/Wayland desteği
- ✅ XWayland otomatik optimizasyonu
- ✅ Forge/Fabric otomatik kurulum
- ✅ Kaynak izleme (CPU, RAM, GPU)
- ✅ Çoklu Java sürüm yönetimi
- ✅ Otomatik güncelleme (AUR)
- ✅ Skin yönetimi
- ✅ Mod arama ve kurulum
- ✅ Paralel indirme (ultra hızlı)

---

**Geliştirici:** Berke Oruç (2009)  
**Lisans:** MIT  
**Platform:** Arch Linux + Hyprland
