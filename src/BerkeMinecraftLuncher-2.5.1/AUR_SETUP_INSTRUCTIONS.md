# 🔑 AUR Setup Instructions

## SSH Key (AUR hesabınıza ekleyin):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH2PUvU+hkDuaf216qFh9YJb6ngMj1W07yzAf/Cu/wuY berke3oruc@gmail.com
```

## 📋 AUR Hesabı Kurulum Adımları:

### 1. AUR Hesabı Oluşturun
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

### 3. AUR Repository Oluşturma
1. AUR ana sayfasında "Submit Package" butonuna tıklayın
2. Package name: `berke-minecraft-launcher`
3. Package description: `Advanced Minecraft launcher with mod support, skin management, and performance monitoring`
4. URL: `https://github.com/berke0/BerkeMinecraftLuncher`
5. License: `MIT`
6. "Submit" butonuna tıklayın

## 🚀 Otomatik Upload Scripti
SSH key'i ekledikten sonra şu komutu çalıştırın:
```bash
./upload_to_aur.sh
```

## ✅ Test Etme
AUR'a yüklendikten sonra test edin:
```bash
# yay ile
yay -S berke-minecraft-launcher

# veya pacman ile
pacman -S berke-minecraft-launcher
```

## 🔧 Manuel Upload (Alternatif)
SSH key'i ekledikten sonra:
```bash
cd /tmp
git clone ssh://aur@aur.archlinux.org/berke-minecraft-launcher.git
cd berke-minecraft-launcher
cp /home/berke0/BerkeMinecraftLuncher/{PKGBUILD,.SRCINFO,berke-minecraft-launcher.desktop,setup.py} .
git add .
git commit -m "Initial release"
git push
```

## 📝 Notlar
- AUR hesabı oluşturma işlemi birkaç dakika sürebilir
- SSH key ekledikten sonra birkaç dakika beklemeniz gerekebilir
- İlk kez AUR'a package gönderirken onay süreci olabilir
