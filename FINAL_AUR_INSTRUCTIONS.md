# 🎉 AUR Yükleme - Son Adımlar

## ✅ Hazırlık Tamamlandı!
- ✅ Git tag oluşturuldu (v2.3.0)
- ✅ GitHub'a push edildi
- ✅ PKGBUILD doğrulandı ve test edildi
- ✅ SHA256 checksum hesaplandı
- ✅ Paket başarıyla build edildi

## 🔑 SSH Key (AUR hesabınıza ekleyin):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH2PUvU+hkDuaf216qFh9YJb6ngMj1W07yzAf/Cu/wuY berke3oruc@gmail.com
```

## 📋 AUR Hesabı Kurulum Adımları:

### 1. AUR Hesabı Oluşturun (Eğer yoksa)
1. https://aur.archlinux.org/account/ adresine gidin
2. "Sign Up" butonuna tıklayın
3. Kullanıcı adı: `berke0` (önerilen)
4. E-posta: `berke3oruc@gmail.com`
5. Şifre oluşturun ve hesabınızı doğrulayın

### 2. SSH Key Ekleme
1. AUR hesabınıza giriş yapın
2. "My Account" sekmesine gidin
3. "SSH Keys" bölümüne gidin
4. "Add SSH Key" butonuna tıklayın
5. Yukarıdaki SSH key'i kopyalayıp yapıştırın
6. "Add Key" butonuna tıklayın

### 3. AUR Repository Oluşturma (İlk kez)
1. AUR ana sayfasında "Submit Package" butonuna tıklayın
2. Package name: `berke-minecraft-launcher`
3. Package description: `Advanced Minecraft launcher with mod support, skin management, and performance monitoring`
4. URL: `https://github.com/BerkeOruc/BerkeMinecraftLuncher`
5. License: `MIT`
6. "Submit" butonuna tıklayın

## 🚀 Otomatik Upload (Önerilen)
SSH key'i ekledikten sonra:
```bash
./auto_upload_to_aur.sh
```

## 🔧 Manuel Upload (Alternatif)
SSH key'i ekledikten sonra:
```bash
cd /tmp
git clone ssh://aur@aur.archlinux.org/berke-minecraft-launcher.git
cd berke-minecraft-launcher
cp /home/berke0/BerkeMinecraftLuncher/{PKGBUILD,.SRCINFO,berke-minecraft-launcher.desktop,setup.py} .
git add .
git commit -m "Initial release v2.3.0"
git push
```

## ✅ Test Etme
AUR'a yüklendikten sonra test edin:

### yay ile:
```bash
yay -S berke-minecraft-launcher
```

### pacman ile:
```bash
# Önce AUR helper'ı kurun (yay önerilen)
yay -S yay

# Sonra paketi kurun
yay -S berke-minecraft-launcher
```

### Kullanım:
```bash
# Launcher'ı başlat
berke-minecraft-launcher
# veya
berkemc
```

## 📦 Paket Bilgileri
- **Package Name**: berke-minecraft-launcher
- **Version**: 2.3.0
- **Description**: Advanced Minecraft launcher with mod support, skin management, and performance monitoring
- **Dependencies**: python>=3.8, java-runtime>=17, python-requests, python-rich, python-colorama, python-psutil
- **License**: MIT
- **Source**: https://github.com/BerkeOruc/BerkeMinecraftLuncher

## 🎯 Başarı Kontrolü
AUR'a yüklendikten sonra:
1. https://aur.archlinux.org/packages/berke-minecraft-launcher adresini kontrol edin
2. `yay -S berke-minecraft-launcher` komutuyla test edin
3. `berke-minecraft-launcher` komutuyla çalıştırın

## 📝 Notlar
- AUR hesabı oluşturma işlemi birkaç dakika sürebilir
- SSH key ekledikten sonra birkaç dakika beklemeniz gerekebilir
- İlk kez AUR'a package gönderirken onay süreci olabilir
- Paket onaylandıktan sonra hem `pacman` hem de `yay` ile kurulabilir

## 🎉 Sonuç
Paket başarıyla AUR'a yüklendikten sonra:
- ✅ `yay -S berke-minecraft-launcher` ile kurulabilir
- ✅ `pacman -S berke-minecraft-launcher` ile kurulabilir
- ✅ `berke-minecraft-launcher` komutuyla çalıştırılabilir
- ✅ `berkemc` kısayolu ile çalıştırılabilir
