# 📦 Kurulum Rehberi

Berke Minecraft Launcher için detaylı kurulum talimatları.

## 📋 İçindekiler

- [Sistem Gereksinimleri](#sistem-gereksinimleri)
- [Kurulum Yöntemleri](#kurulum-yöntemleri)
  - [AUR (Önerilen)](#1-aur-önerilen)
  - [Manuel Kurulum](#2-manuel-kurulum)
  - [Sistem Geneli Kurulum](#3-sistem-geneli-kurulum)
- [İlk Çalıştırma](#ilk-çalıştırma)
- [Sorun Giderme](#sorun-giderme)

---

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşletim Sistemi**: Arch Linux (veya türevleri)
- **Python**: 3.10 veya üzeri
- **Java**: 21 veya üzeri (otomatik kurulacak)
- **RAM**: 4 GB
- **Disk Alanı**: 2 GB (Minecraft + modlar için daha fazla)

### Önerilen Gereksinimler
- **İşletim Sistemi**: Arch Linux (güncel)
- **Python**: 3.11+
- **Java**: 25 (OpenJDK)
- **RAM**: 8 GB veya üzeri
- **Disk Alanı**: 10 GB
- **İnternet**: Hızlı bağlantı (indirmeler için)

### Bağımlılıklar

**Sistem Paketleri:**
```bash
sudo pacman -S python python-pip git jdk-openjdk xorg-server-xwayland
```

**Python Paketleri:**
- requests >= 2.31.0
- rich >= 13.7.0
- click >= 8.1.7
- psutil >= 5.9.6
- colorama >= 0.4.6

---

## 🚀 Kurulum Yöntemleri

### 1. AUR (Önerilen)

**Yakında!** AUR'da yayınlanacak.

#### yay ile:
```bash
yay -S berke-minecraft-launcher
```

#### paru ile:
```bash
paru -S berke-minecraft-launcher
```

#### makepkg ile:
```bash
git clone https://aur.archlinux.org/berke-minecraft-launcher.git
cd berke-minecraft-launcher
makepkg -si
```

### 2. Manuel Kurulum

#### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/berke0/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher
```

#### Adım 2: Başlatma Scriptini Çalıştırın
```bash
chmod +x start.sh
./start.sh
```

Script otomatik olarak:
- ✅ Python ve bağımlılıkları kontrol eder
- ✅ Virtual environment oluşturur
- ✅ Python paketlerini yükler
- ✅ Java'yı kontrol eder ve gerekirse kurar
- ✅ Launcher'ı başlatır

### 3. Sistem Geneli Kurulum

Launcher'ı sistem genelinde kurmak ve uygulama menüsüne eklemek için:

```bash
chmod +x install_system.sh
./install_system.sh
```

Bu komut:
- Launcher'ı `~/.local/share/berke-minecraft-launcher/` dizinine kurar
- `.desktop` dosyası oluşturur
- Uygulama menüsüne ekler (GNOME, KDE, Hyprland, XFCE)
- İkon ekler
- PATH'e ekler

**Başlatma:**
```bash
# Terminal'den
berke-minecraft-launcher

# Veya uygulama menüsünden:
# Uygulamalar → Oyunlar → Berke Minecraft Launcher
```

**Kaldırma:**
```bash
./uninstall_system.sh
```

---

## 🎮 İlk Çalıştırma

### 1. Launcher'ı Başlatın

```bash
./start.sh
```

### 2. İlk Kurulum Adımları

Launcher ilk çalıştırıldığında:

1. **Java Kontrolü**
   - Java 21+ var mı kontrol edilir
   - Yoksa otomatik kurulum önerilir

2. **Minecraft Dizini**
   - `~/.minecraft` dizini oluşturulur
   - `~/.berke_minecraft_launcher` dizini oluşturulur

3. **Config Dosyası**
   - Varsayılan ayarlar oluşturulur
   - `config.json` dosyası kaydedilir

### 3. İlk Minecraft Sürümünü İndirin

1. Ana menüden **2** (Sürüm İndir) seçin
2. Bir sürüm seçin (örn: 1.20.1)
3. İndirme tamamlanana kadar bekleyin
4. Ana menüden **1** (Minecraft Başlat) seçin
5. İndirdiğiniz sürümü seçin
6. Oyun başlasın!

---

## 🔧 Sorun Giderme

### Python Bulunamadı

```bash
# Python kurulumu
sudo pacman -S python python-pip

# Versiyon kontrolü
python --version  # 3.10+ olmalı
```

### Java Bulunamadı

```bash
# Java kurulumu
sudo pacman -S jdk-openjdk

# Versiyon kontrolü
java -version  # 21+ olmalı

# Varsayılan Java'yı ayarla
sudo archlinux-java set java-openjdk
```

### Bağımlılık Hataları

```bash
# Virtual environment yeniden oluştur
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Minecraft Başlamıyor

1. **Java Sürümünü Kontrol Edin:**
   ```bash
   java -version
   ```
   Java 21+ olmalı.

2. **Log Dosyalarını Kontrol Edin:**
   ```bash
   tail -f ~/.berke_minecraft_launcher/logs/minecraft_*.log
   ```

3. **Sürümü Yeniden İndirin:**
   - Menü 3 → Sürümü seçin → Sil
   - Menü 2 → Sürümü yeniden indirin

4. **Sistem Testini Çalıştırın:**
   - Menü 5 (Ayarlar) → Seçenek 22 (Sistem Testi)

### Hyprland/Wayland Sorunları

```bash
# XWayland kurulumu
sudo pacman -S xorg-server-xwayland

# Environment değişkenlerini kontrol edin
echo $XDG_SESSION_TYPE  # "wayland" olmalı
echo $WAYLAND_DISPLAY   # Boş olmamalı
```

### Mod İndirme Hataları

1. **İnternet Bağlantısını Kontrol Edin:**
   ```bash
   ping -c 3 modrinth.com
   ```

2. **Minecraft Sürümünü Kontrol Edin:**
   - Mod, seçtiğiniz Minecraft sürümünü destekliyor mu?

3. **Mod Klasörünü Kontrol Edin:**
   ```bash
   ls -la ~/.minecraft/mods/
   ```

### İzin Hataları

```bash
# Script'lere execute izni verin
chmod +x start.sh
chmod +x install_system.sh
chmod +x uninstall_system.sh

# Launcher dizinine yazma izni
chmod -R u+w ~/.berke_minecraft_launcher/
```

---

## 📚 Ek Kaynaklar

- **README.md**: Genel bilgiler
- **CONTRIBUTING.md**: Katkıda bulunma rehberi
- **CHANGELOG.md**: Sürüm geçmişi
- **GitHub Issues**: https://github.com/berke0/BerkeMinecraftLuncher/issues

---

## 💡 İpuçları

### Performans İyileştirme

1. **Ayarlar → Bellek**: RAM miktarını artırın (8GB önerilir)
2. **Ayarlar → CPU Optimizasyonu**: Açık
3. **Ayarlar → RAM Optimizasyonu**: Açık
4. **Mod Yönetimi**: Sodium, Lithium, Phosphor modlarını kurun

### Hızlı Başlatma

```bash
# Alias oluşturun
echo "alias mc='cd ~/BerkeMinecraftLuncher && ./start.sh'" >> ~/.bashrc
source ~/.bashrc

# Artık sadece:
mc
```

### Otomatik Güncelleme

```bash
# Repository'yi güncelleyin
cd BerkeMinecraftLuncher
git pull
./start.sh
```

---

Sorun yaşıyorsanız, [GitHub Issues](https://github.com/berke0/BerkeMinecraftLuncher/issues) sayfasından yardım alabilirsiniz!
