# 📦 AUR'a Yükleme Rehberi

Bu rehber, **Berke Minecraft Launcher**'ı AUR (Arch User Repository) ve diğer paket yöneticilerine nasıl yükleyeceğinizi adım adım anlatır.

---

## 🎯 İçindekiler

1. [AUR'a Yükleme](#aura-yükleme)
2. [Pacman ile Yerel Kurulum](#pacman-ile-yerel-kurulum)
3. [Yay/Paru ile Kurulum](#yayparu-ile-kurulum)
4. [Test ve Doğrulama](#test-ve-doğrulama)

---

## 📋 Ön Hazırlık

### 1. GitHub Repository'yi Hazırla

Önce projeyi GitHub'a yükle (GITHUB_GUIDE.md'yi takip et):

```bash
cd /home/berke0/BerkeMinecraftLuncher

# Git init (eğer yapılmadıysa)
git init
git add .
git commit -m "v2.3.1 - Ultra Fast + Retro Edition"

# GitHub'a push
git remote add origin https://github.com/KULLANICI_ADIN/BerkeMinecraftLuncher.git
git branch -M main
git push -u origin main

# Release oluştur
git tag -a v2.3.1 -m "Release v2.3.1"
git push origin v2.3.1
```

---

## 🚀 AUR'a Yükleme

### Adım 1: AUR Hesabı Oluştur

1. **AUR'a kayıt ol**: https://aur.archlinux.org/register
2. **SSH anahtarı ekle**:
   ```bash
   # SSH anahtarı oluştur (eğer yoksa)
   ssh-keygen -t ed25519 -C "your-email@example.com"
   
   # Public key'i kopyala
   cat ~/.ssh/id_ed25519.pub
   
   # AUR hesabına ekle: https://aur.archlinux.org/account/
   ```

### Adım 2: AUR Repository'yi Klonla

```bash
# AUR repository'yi klonla
git clone ssh://aur@aur.archlinux.org/berke-minecraft-launcher.git aur-berke-minecraft-launcher
cd aur-berke-minecraft-launcher
```

### Adım 3: PKGBUILD Dosyalarını Kopyala

```bash
# PKGBUILD ve .SRCINFO'yu kopyala
cp /home/berke0/BerkeMinecraftLuncher/PKGBUILD .
cp /home/berke0/BerkeMinecraftLuncher/.SRCINFO .

# PKGBUILD'i düzenle (email adresini güncelle)
nano PKGBUILD
# İlk satırı düzenle:
# Maintainer: Berke Oruc <your-email@example.com>
```

### Adım 4: .SRCINFO Oluştur

```bash
# .SRCINFO dosyasını otomatik oluştur
makepkg --printsrcinfo > .SRCINFO
```

### Adım 5: AUR'a Yükle

```bash
# Dosyaları commit et
git add PKGBUILD .SRCINFO
git commit -m "Initial commit: berke-minecraft-launcher v2.3.1"

# AUR'a push et
git push origin master
```

### Adım 6: Doğrula

1. AUR sayfasını kontrol et: https://aur.archlinux.org/packages/berke-minecraft-launcher
2. Paket bilgilerini gözden geçir
3. Yorumları ve oy sayısını takip et

---

## 📦 Pacman ile Yerel Kurulum

AUR'a yüklemeden önce yerel olarak test et:

### Adım 1: Paketi Oluştur

```bash
cd /home/berke0/BerkeMinecraftLuncher

# Paketi oluştur
makepkg -si

# Sadece oluştur (kurma)
makepkg

# Temiz build
makepkg -c
```

### Adım 2: Paketi Kur

```bash
# Oluşturulan paketi kur
sudo pacman -U berke-minecraft-launcher-2.3.1-1-any.pkg.tar.zst
```

### Adım 3: Test Et

```bash
# Komutu test et
berkemc

# Veya uygulama menüsünden başlat
```

### Adım 4: Kaldır (Test için)

```bash
sudo pacman -R berke-minecraft-launcher
```

---

## 🎨 Yay/Paru ile Kurulum

Kullanıcılar AUR'dan şu şekilde kurabilir:

### Yay ile:

```bash
yay -S berke-minecraft-launcher
```

### Paru ile:

```bash
paru -S berke-minecraft-launcher
```

### Manuel AUR Helper:

```bash
# Clone
git clone https://aur.archlinux.org/berke-minecraft-launcher.git
cd berke-minecraft-launcher

# Build ve install
makepkg -si
```

---

## ✅ Test ve Doğrulama

### 1. Paket Bilgilerini Kontrol Et

```bash
# Paket bilgileri
pacman -Qi berke-minecraft-launcher

# Dosya listesi
pacman -Ql berke-minecraft-launcher

# Bağımlılıklar
pacman -Qii berke-minecraft-launcher
```

### 2. Çalıştırma Testi

```bash
# Terminal'den çalıştır
berkemc

# Desktop entry kontrolü
ls -la /usr/share/applications/berke-minecraft-launcher.desktop

# Icon kontrolü
ls -la /usr/share/pixmaps/berke-minecraft-launcher.png
```

### 3. Kurulum Konumları

```bash
# Ana program
/opt/berke-minecraft-launcher/berke_minecraft_launcher.py

# Başlatma scripti
/opt/berke-minecraft-launcher/start.sh

# Sistem komutu
/usr/bin/berkemc

# Desktop entry
/usr/share/applications/berke-minecraft-launcher.desktop

# Icon
/usr/share/pixmaps/berke-minecraft-launcher.png

# Dokümantasyon
/usr/share/doc/berke-minecraft-launcher/
```

---

## 🔄 Güncelleme Süreci

### Yeni Sürüm Yayınlama:

1. **Sürüm numarasını güncelle**:
   ```bash
   # PKGBUILD'de pkgver'i artır
   nano PKGBUILD
   # pkgver=2.3.2
   ```

2. **GitHub'a yeni release**:
   ```bash
   git tag -a v2.3.2 -m "Release v2.3.2"
   git push origin v2.3.2
   ```

3. **.SRCINFO'yu güncelle**:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

4. **AUR'a push et**:
   ```bash
   cd aur-berke-minecraft-launcher
   git add PKGBUILD .SRCINFO
   git commit -m "Update to v2.3.2"
   git push origin master
   ```

5. **Kullanıcılar güncellesin**:
   ```bash
   yay -Syu berke-minecraft-launcher
   ```

---

## 🛠️ Sorun Giderme

### PKGBUILD Hataları

```bash
# PKGBUILD syntax kontrolü
namcap PKGBUILD

# Paket kontrolü
namcap berke-minecraft-launcher-2.3.1-1-any.pkg.tar.zst
```

### Bağımlılık Sorunları

```bash
# Eksik bağımlılıkları kur
sudo pacman -S python python-requests python-rich python-colorama python-psutil jdk-openjdk
```

### SSH Anahtarı Sorunları

```bash
# SSH agent'ı başlat
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# AUR bağlantısını test et
ssh -T aur@aur.archlinux.org
```

---

## 📊 AUR İstatistikleri

Paket yayınlandıktan sonra:

- **Oy sayısı**: Kullanıcılar paketi oylayabilir
- **Popülerlik**: İndirme sayısına göre
- **Yorumlar**: Kullanıcı geri bildirimleri
- **Bayraklar**: Sorun bildirimleri

**AUR sayfası**: https://aur.archlinux.org/packages/berke-minecraft-launcher

---

## 🎯 Alternatif Paket Yöneticileri

### Flatpak (Gelecek)

```bash
# Flatpak manifest oluştur
# com.berke.MinecraftLauncher.yml
```

### Snap (Gelecek)

```bash
# Snapcraft.yaml oluştur
```

### AppImage (Gelecek)

```bash
# AppImage builder kullan
```

---

## 📝 Önemli Notlar

1. **Email Adresi**: PKGBUILD'deki email adresini gerçek adresinle değiştir
2. **GitHub URL**: Repository URL'ini doğru yaz
3. **Lisans**: MIT lisansını ekle (LICENSE dosyası)
4. **Sürüm Numarası**: Her güncellemede artır
5. **Test**: AUR'a yüklemeden önce mutlaka yerel test yap

---

## 🚀 Hızlı Komutlar

```bash
# Yerel test
cd /home/berke0/BerkeMinecraftLuncher
makepkg -si

# AUR'a yükle
cd aur-berke-minecraft-launcher
git add PKGBUILD .SRCINFO
git commit -m "Update"
git push origin master

# Kullanıcı kurulumu
yay -S berke-minecraft-launcher
```

---

## 📞 Destek

- **GitHub Issues**: https://github.com/berke0/BerkeMinecraftLuncher/issues
- **AUR Yorumlar**: https://aur.archlinux.org/packages/berke-minecraft-launcher
- **Email**: your-email@example.com

---

## 🎉 Başarılı Yükleme!

Paket başarıyla AUR'a yüklendikten sonra, tüm Arch Linux kullanıcıları:

```bash
yay -S berke-minecraft-launcher
berkemc
```

komutlarıyla launcher'ı kurabilir ve kullanabilir! 🚀

---

**Son Güncelleme**: 2025-10-05  
**Sürüm**: v2.3.1  
**Durum**: Production Ready ✅
