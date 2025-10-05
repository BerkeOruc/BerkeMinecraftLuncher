# 🚀 AUR'A YÜKLEME REHBERİ - BerkeMC

Bu rehber, **BerkeMC** launcher'ını AUR'a nasıl yükleyeceğinizi **adım adım** anlatır.

---

## 📦 Paket Bilgileri

**Paket Adı**: `berkemc`  
**Kurulum**: `yay -S berkemc`  
**Çalıştırma**: `berkemc`  

---

## 🎯 HIZLI BAŞLANGIÇ

### Kullanıcılar için (AUR'dan kurulum):

```bash
# Yay ile
yay -S berkemc

# Paru ile
paru -S berkemc

# Çalıştır
berkemc
```

---

## 📋 AUR'A YÜKLEME ADIMLARI

### ADIM 1: GitHub'a Yükle

```bash
cd /home/berke0/BerkeMinecraftLuncher

# Git başlat (eğer yapılmadıysa)
git init

# Tüm dosyaları ekle
git add .

# Commit yap
git commit -m "v2.3.1 - Ultra Fast Minecraft Launcher"

# GitHub repository oluştur (https://github.com/new)
# Repository adı: BerkeMinecraftLuncher

# Remote ekle (USERNAME yerine GitHub kullanıcı adını yaz)
git remote add origin https://github.com/USERNAME/BerkeMinecraftLuncher.git

# Push et
git branch -M main
git push -u origin main

# Release tag oluştur
git tag -a v2.3.1 -m "Release v2.3.1 - Production Ready"
git push origin v2.3.1
```

**✅ GitHub'da repository'n hazır!**

---

### ADIM 2: AUR Hesabı Oluştur

1. **AUR'a kayıt ol**: https://aur.archlinux.org/register
   - Username seç
   - Email doğrula
   - Profil bilgilerini doldur

2. **SSH Anahtarı Oluştur** (eğer yoksa):
   ```bash
   # Ed25519 anahtarı oluştur (en güvenli)
   ssh-keygen -t ed25519 -C "your-email@example.com"
   
   # Enter'a bas (varsayılan konum: ~/.ssh/id_ed25519)
   # Şifre iste (opsiyonel ama önerilir)
   ```

3. **Public Key'i Kopyala**:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   
   Çıktıyı kopyala (ssh-ed25519 ile başlayan satır)

4. **AUR'a SSH Key Ekle**:
   - https://aur.archlinux.org/account/ adresine git
   - "My Account" → "SSH Public Key" bölümüne yapıştır
   - "Update" butonuna bas

5. **SSH Bağlantısını Test Et**:
   ```bash
   ssh -T aur@aur.archlinux.org
   ```
   
   Çıktı: `Hi USERNAME! You've successfully authenticated...`

**✅ AUR hesabın hazır!**

---

### ADIM 3: AUR Repository Oluştur

```bash
# AUR repository'yi klonla
git clone ssh://aur@aur.archlinux.org/berkemc.git aur-berkemc

# Dizine gir
cd aur-berkemc

# Boş olacak (ilk kez yüklüyorsun)
ls -la
```

**✅ AUR repository'n hazır!**

---

### ADIM 4: PKGBUILD Dosyalarını Hazırla

```bash
# PKGBUILD'i kopyala
cp /home/berke0/BerkeMinecraftLuncher/PKGBUILD .

# Email adresini düzenle
nano PKGBUILD

# İlk satırı düzenle:
# Maintainer: Berke Oruc <gerçek-email@adresin.com>

# Kaydet ve çık (Ctrl+O, Enter, Ctrl+X)
```

**✅ PKGBUILD hazır!**

---

### ADIM 5: .SRCINFO Oluştur

```bash
# .SRCINFO'yu otomatik oluştur
makepkg --printsrcinfo > .SRCINFO

# Kontrol et
cat .SRCINFO
```

Çıktı şöyle olmalı:
```
pkgbase = berkemc
	pkgdesc = Ultra-fast terminal-based Minecraft launcher...
	pkgver = 2.3.1
	...
pkgname = berkemc
```

**✅ .SRCINFO hazır!**

---

### ADIM 6: Yerel Test (ÖNEMLİ!)

AUR'a yüklemeden önce **mutlaka** yerel test yap:

```bash
# PKGBUILD dizininde (aur-berkemc/)
makepkg -si

# Paket oluşturulacak ve kurulacak
# Şifre iste (sudo için)

# Test et
berkemc

# Çalışıyor mu kontrol et
# Minecraft başlatmayı dene

# Kaldır (test için)
sudo pacman -R berkemc
```

**✅ Yerel test başarılı!**

---

### ADIM 7: AUR'a Yükle

```bash
# aur-berkemc/ dizininde olduğundan emin ol
cd aur-berkemc

# Dosyaları git'e ekle
git add PKGBUILD .SRCINFO

# Commit yap
git commit -m "Initial commit: berkemc v2.3.1"

# AUR'a push et
git push origin master

# Şifre iste (SSH key şifresi)
```

**✅ AUR'a yüklendi!**

---

### ADIM 8: Doğrula

1. **AUR sayfasını aç**: https://aur.archlinux.org/packages/berkemc

2. **Kontrol et**:
   - Paket adı: berkemc
   - Sürüm: 2.3.1-1
   - Açıklama: Ultra-fast terminal-based...
   - Bağımlılıklar: python, python-requests, etc.

3. **Test et** (başka bir bilgisayarda):
   ```bash
   yay -S berkemc
   berkemc
   ```

**✅ AUR'da yayında!**

---

## 🔄 GÜNCELLEME NASIL YAPILIR?

Yeni sürüm yayınlamak için:

### 1. Kodu Güncelle

```bash
cd /home/berke0/BerkeMinecraftLuncher

# Değişiklikleri yap
nano berke_minecraft_launcher.py

# Commit et
git add .
git commit -m "v2.3.2 - Bug fixes"

# GitHub'a push et
git push origin main

# Yeni tag oluştur
git tag -a v2.3.2 -m "Release v2.3.2"
git push origin v2.3.2
```

### 2. PKGBUILD'i Güncelle

```bash
cd aur-berkemc

# PKGBUILD'i düzenle
nano PKGBUILD

# pkgver'i artır:
# pkgver=2.3.2

# pkgrel'i 1'e sıfırla:
# pkgrel=1

# Kaydet ve çık
```

### 3. .SRCINFO'yu Yenile

```bash
makepkg --printsrcinfo > .SRCINFO
```

### 4. AUR'a Push Et

```bash
git add PKGBUILD .SRCINFO
git commit -m "Update to v2.3.2"
git push origin master
```

### 5. Kullanıcılar Güncellesin

```bash
yay -Syu berkemc
```

**✅ Güncelleme tamamlandı!**

---

## 🛠️ SORUN GİDERME

### SSH Bağlantı Hatası

```bash
# SSH agent'ı başlat
eval "$(ssh-agent -s)"

# SSH key'i ekle
ssh-add ~/.ssh/id_ed25519

# Test et
ssh -T aur@aur.archlinux.org
```

### PKGBUILD Hataları

```bash
# PKGBUILD syntax kontrolü
namcap PKGBUILD

# Paket kontrolü
namcap berkemc-2.3.1-1-any.pkg.tar.zst
```

### Bağımlılık Sorunları

```bash
# Eksik bağımlılıkları kur
sudo pacman -S python python-requests python-rich python-colorama python-psutil jdk-openjdk
```

### Git Push Hatası

```bash
# SSH key'in doğru olduğundan emin ol
cat ~/.ssh/id_ed25519.pub

# AUR hesabında aynı key var mı kontrol et
# https://aur.archlinux.org/account/

# Yeniden dene
git push origin master
```

---

## 📊 AUR İSTATİSTİKLERİ

Paket yayınlandıktan sonra:

- **Oy sayısı**: Kullanıcılar paketi oylayabilir
- **Popülerlik**: İndirme sayısına göre hesaplanır
- **Yorumlar**: Kullanıcı geri bildirimleri
- **Bayraklar**: Sorun bildirimleri (out-of-date, etc.)

**AUR Sayfan**: https://aur.archlinux.org/packages/berkemc

---

## 🎯 KULLANICI DENEYİMİ

### Kurulum:
```bash
yay -S berkemc
```

### Başlatma:
```bash
berkemc
```

### Güncelleme:
```bash
yay -Syu berkemc
```

### Kaldırma:
```bash
sudo pacman -R berkemc
```

---

## 📝 ÖNEMLİ NOTLAR

1. **Email Adresi**: PKGBUILD'deki email adresini gerçek adresinle değiştir
2. **GitHub URL**: Repository URL'ini doğru yaz
3. **Lisans**: MIT lisansını ekle (LICENSE dosyası)
4. **Sürüm Numarası**: Her güncellemede `pkgver`'i artır, `pkgrel`'i 1'e sıfırla
5. **Test**: AUR'a yüklemeden önce **mutlaka** yerel test yap
6. **SSH Key**: AUR hesabına eklemeyi unutma
7. **GitHub Release**: Her sürüm için tag oluştur

---

## 🚀 HIZLI KOMUTLAR

```bash
# GitHub'a yükle
cd /home/berke0/BerkeMinecraftLuncher
git add . && git commit -m "v2.3.1" && git push origin main
git tag -a v2.3.1 -m "Release v2.3.1" && git push origin v2.3.1

# AUR'a yükle
cd aur-berkemc
cp /home/berke0/BerkeMinecraftLuncher/PKGBUILD .
nano PKGBUILD  # Email düzenle
makepkg --printsrcinfo > .SRCINFO
git add PKGBUILD .SRCINFO
git commit -m "Initial commit: v2.3.1"
git push origin master

# Yerel test
makepkg -si
berkemc

# Kullanıcı kurulumu
yay -S berkemc
```

---

## 📞 DESTEK

- **GitHub Issues**: https://github.com/USERNAME/BerkeMinecraftLuncher/issues
- **AUR Yorumlar**: https://aur.archlinux.org/packages/berkemc
- **Email**: your-email@example.com

---

## 🎉 BAŞARILI YÜKLEME!

Paket başarıyla AUR'a yüklendikten sonra, tüm Arch Linux kullanıcıları:

```bash
yay -S berkemc
berkemc
```

komutlarıyla launcher'ı kurabilir ve kullanabilir! 🚀

---

## 📋 KONTROL LİSTESİ

Yüklemeden önce kontrol et:

- [ ] GitHub'a yüklendi (tag ile)
- [ ] AUR hesabı oluşturuldu
- [ ] SSH key eklendi
- [ ] AUR repository klonlandı
- [ ] PKGBUILD email düzenlendi
- [ ] .SRCINFO oluşturuldu
- [ ] Yerel test yapıldı
- [ ] AUR'a push edildi
- [ ] AUR sayfası kontrol edildi
- [ ] Başka bir sistemde test edildi

**Hepsi ✅ ise, paket hazır!** 🎉

---

**Son Güncelleme**: 2025-10-05  
**Sürüm**: v2.3.1  
**Durum**: Production Ready ✅  
**Paket Adı**: `berkemc`  
**Kurulum**: `yay -S berkemc`
