# 🚀 GitHub'a Yükleme Kılavuzu

## Berke Minecraft Launcher - GitHub Repository Oluşturma ve Yükleme

---

## 📋 Ön Hazırlık Tamamlandı ✅

Proje GitHub'a yüklenmeye hazır!

**Temizlenen:**
- ✅ `__pycache__/` silindi
- ✅ Gereksiz `.desktop` dosyası silindi  
- ✅ Eski scriptler silindi
- ✅ Gereksiz docs silindi
- ✅ `.gitignore` güncellendi
- ✅ BMC logosu oluşturuldu
- ✅ Tüm emojiler temizlendi

---

## 🔧 ADIM 1: Git Kurulumu ve Yapılandırma

### 1.1. Git Kontrolü
```bash
git --version
```

Eğer kurulu değilse:
```bash
sudo pacman -S git
```

### 1.2. Git Yapılandırması
```bash
git config --global user.name "Berke Oruç"
git config --global user.email "berke3oruc@gmail.com"
```

### 1.3. Yapılandırmayı Kontrol Et
```bash
git config --list
```

---

## 📦 ADIM 2: Local Repository Oluşturma

### 2.1. Proje Dizinine Git
```bash
cd /home/berke0/BerkeMinecraftLuncher
```

### 2.2. Git Repository Başlat
```bash
git init
```

### 2.3. Dosyaları Staging'e Ekle
```bash
git add .
```

### 2.4. Hangi Dosyaların Ekleneceğini Kontrol Et
```bash
git status
```

**Eklenecek dosyalar:**
- ✅ `berke_minecraft_launcher.py`
- ✅ `start.sh`, `berkemc`
- ✅ `install_system.sh`, `uninstall_system.sh`
- ✅ `README.md`, `LICENSE`, `requirements.txt`
- ✅ `PKGBUILD`, `version.py`, `i18n.py`
- ✅ `bmc_logo.png`, `BMC_LOGO.txt`
- ✅ `.gitignore`, `.github/workflows/ci.yml`
- ✅ Tüm docs/ ve scripts/ içerikleri

**Eklenmeyecek (gitignore'da):**
- ❌ `venv/`
- ❌ `logs/`
- ❌ `__pycache__/`
- ❌ `*.log`, `*.log.gz`

### 2.5. İlk Commit
```bash
git commit -m "🎮 Initial commit: Berke Minecraft Launcher v2.3.0

✨ Features:
- Minimal TUI interface with Rich library
- All Minecraft versions support (1.0 - latest)
- Skin management system with popular skins
- Mod management (Modrinth API integration)
- Real-time performance monitoring
- Advanced JVM optimizations
- Wayland/Hyprland support
- System-wide installation (berkemc command)
- Emoji-free professional design
- BMC logo and branding

🚀 Production ready for Arch Linux
👨‍💻 Developer: Berke Oruç (2009)"
```

---

## 🌐 ADIM 3: GitHub Repository Oluşturma

### 3.1. GitHub'a Git
1. Tarayıcıda aç: https://github.com/new
2. Veya: GitHub → Repositories → New

### 3.2. Repository Ayarları

**Repository name:**
```
BerkeMinecraftLauncher
```

**Description:**
```
🎮 Ultra-Fast Minecraft Launcher for Arch Linux with TUI interface | All versions, mods, skins, performance monitoring
```

**Visibility:**
- ✅ **Public** (Herkes görebilir)
- ❌ Private

**Initialize this repository with:**
- ❌ **README** (zaten var)
- ❌ **.gitignore** (zaten var)
- ❌ **license** (zaten var - MIT)

### 3.3. Create Repository
"Create repository" butonuna tıkla!

---

## 🔗 ADIM 4: Remote Repository Bağlantısı

### 4.1. Repository URL'ini Kopyala

GitHub'da oluşturduğun repository sayfasında göreceksin:
```
https://github.com/berke3oruc/BerkeMinecraftLauncher.git
```

### 4.2. Remote Ekle
```bash
git remote add origin https://github.com/berke3oruc/BerkeMinecraftLauncher.git
```

### 4.3. Branch Adını Ayarla
```bash
git branch -M main
```

### 4.4. Remote'u Kontrol Et
```bash
git remote -v
```

Çıktı:
```
origin  https://github.com/berke3oruc/BerkeMinecraftLauncher.git (fetch)
origin  https://github.com/berke3oruc/BerkeMinecraftLauncher.git (push)
```

---

## 🚀 ADIM 5: GitHub'a Push

### 5.1. Push Yap
```bash
git push -u origin main
```

### 5.2. Kimlik Doğrulama

**Seçenek 1: Personal Access Token (Kolay)**

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. **Note:** `BerkeMinecraftLauncher`
4. **Expiration:** 90 days
5. **Scopes:** ✅ `repo` (tüm repo izinleri)
6. "Generate token"
7. **Token'ı KOPYALA** (bir daha göremezsin!)

Push yaparken:
- **Username:** `berke3oruc`
- **Password:** `<token'ı yapıştır>`

**Seçenek 2: SSH Key (Güvenli - Önerilen)**

```bash
# SSH key oluştur
ssh-keygen -t ed25519 -C "berke3oruc@gmail.com"

# Enter 3 kez (şifre istemezsen)

# Public key'i kopyala
cat ~/.ssh/id_ed25519.pub
```

GitHub'da:
1. Settings → SSH and GPG keys → New SSH key
2. **Title:** `Arch Linux - BerkeMinecraftLauncher`
3. **Key:** Kopyaladığın public key'i yapıştır
4. "Add SSH key"

Remote URL'i SSH'e çevir:
```bash
git remote set-url origin git@github.com:berke3oruc/BerkeMinecraftLauncher.git
```

Push:
```bash
git push -u origin main
```

---

## 📝 ADIM 6: Repository Ayarlarını Düzenle

### 6.1. About Bölümü

GitHub repository sayfasında, sağ üstte "About" yanındaki ⚙️ (ayarlar):

**Website:**
```
https://github.com/berke3oruc/BerkeMinecraftLauncher
```

**Topics (etiketler):**
```
minecraft
launcher
arch-linux
python
tui
terminal
minecraft-launcher
rich
wayland
hyprland
modrinth
skin-manager
mod-manager
performance
gaming
```

**Description:**
```
🎮 Ultra-Fast Minecraft Launcher for Arch Linux with TUI interface
```

### 6.2. README Badges Ekle

`README.md` dosyasının en üstüne ekle:

```markdown
# Berke Minecraft Launcher

![Version](https://img.shields.io/badge/version-2.3.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Arch%20Linux-blue)
![Status](https://img.shields.io/badge/status-production-green)
![Maintenance](https://img.shields.io/badge/maintained-yes-green)

🎮 Ultra-Fast Minecraft Launcher for Arch Linux with TUI interface
```

Commit ve push:
```bash
git add README.md
git commit -m "📝 Docs: Add badges to README"
git push
```

---

## 🏷️ ADIM 7: İlk Release Oluştur

### 7.1. Releases Sayfasına Git
GitHub repository → Releases → "Create a new release"

### 7.2. Release Bilgileri

**Tag:**
```
v2.3.0
```

**Release title:**
```
🎮 Berke Minecraft Launcher v2.3.0 - Ultra Fast Edition
```

**Description:**
```markdown
## 🎮 Berke Minecraft Launcher v2.3.0

### ✨ Features

- 🖥️ **Minimal TUI Interface** - Beautiful terminal UI with Rich library
- 🎯 **All Minecraft Versions** - From 1.0 to latest (1.21+)
- 👤 **Skin Management** - Download, upload, and manage skins
- 🔧 **Mod Management** - Modrinth API integration for easy mod installation
- 📊 **Performance Monitoring** - Real-time CPU, RAM, and FPS tracking
- ⚡ **JVM Optimizations** - Advanced Java arguments for best performance
- 🌊 **Wayland/Hyprland Support** - Native support for modern compositors
- 🚀 **System Integration** - Install system-wide with `berkemc` command
- 🎨 **Professional Design** - Emoji-free, clean, minimal interface
- 🔰 **BMC Branding** - Custom logo and consistent design

### 📦 Installation

#### Quick Install (Arch Linux)

\`\`\`bash
git clone https://github.com/berke3oruc/BerkeMinecraftLauncher.git
cd BerkeMinecraftLauncher
./install_system.sh
\`\`\`

#### Launch

\`\`\`bash
berkemc
\`\`\`

### 📖 Documentation

- [README.md](README.md) - Full documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

### 🐛 Bug Reports

Report issues: https://github.com/berke3oruc/BerkeMinecraftLauncher/issues

### 👨‍💻 Developer

**Berke Oruç** (2009)
- Email: berke3oruc@gmail.com
- GitHub: [@berke3oruc](https://github.com/berke3oruc)

### 📜 License

MIT License - See [LICENSE](LICENSE) for details

---

**Enjoy gaming! 🎮**
```

### 7.3. Publish Release
"Publish release" butonuna tıkla!

---

## 🔄 ADIM 8: Gelecekteki Güncellemeler

### 8.1. Değişiklikleri Commit Et

```bash
# Değişiklikleri gör
git status

# Dosyaları ekle
git add .

# Commit (emoji ile profesyonel mesaj)
git commit -m "✨ Feature: Yeni özellik açıklaması"

# Push
git push
```

### 8.2. Commit Mesaj Formatı

**Emoji Kullanımı:**
- `✨ Feature:` - Yeni özellik
- `🐛 Fix:` - Bug düzeltme
- `📝 Docs:` - Dokümantasyon
- `🎨 Style:` - Kod formatı, UI değişikliği
- `♻️ Refactor:` - Kod yeniden yapılandırma
- `⚡ Perf:` - Performans iyileştirme
- `✅ Test:` - Test ekleme/güncelleme
- `🔧 Config:` - Yapılandırma değişikliği
- `🚀 Deploy:` - Deployment/release
- `🔒 Security:` - Güvenlik güncellemesi

**Örnekler:**
```bash
git commit -m "✨ Feature: Add automatic Java version detection"
git commit -m "🐛 Fix: Resolve skin download timeout issue"
git commit -m "📝 Docs: Update installation instructions for Ubuntu"
git commit -m "⚡ Perf: Optimize mod search with caching"
```

---

## ✅ KONTROL LİSTESİ

Yüklemeden önce kontrol et:

- [ ] `.gitignore` güncel ve doğru
- [ ] `README.md` güncel ve kapsamlı
- [ ] `LICENSE` dosyası mevcut
- [ ] `requirements.txt` güncel
- [ ] Gereksiz dosyalar silindi
- [ ] `__pycache__` silindi
- [ ] `venv/` gitignore'da
- [ ] `logs/` gitignore'da
- [ ] Git yapılandırması yapıldı
- [ ] GitHub repository oluşturuldu
- [ ] Remote bağlantısı kuruldu
- [ ] İlk commit yapıldı
- [ ] Push başarılı
- [ ] README badges eklendi
- [ ] Release oluşturuldu
- [ ] BMC logosu eklendi

---

## 🎉 BAŞARILI!

Projeniz artık GitHub'da yayında!

### Repository URL:
```
https://github.com/berke3oruc/BerkeMinecraftLauncher
```

### Clone:
```bash
git clone https://github.com/berke3oruc/BerkeMinecraftLauncher.git
```

### Star:
⭐ Repository'ye star vermeyi unutma!

---

## 📞 Destek ve İletişim

- **Issues:** https://github.com/berke3oruc/BerkeMinecraftLauncher/issues
- **Pull Requests:** https://github.com/berke3oruc/BerkeMinecraftLauncher/pulls
- **Email:** berke3oruc@gmail.com

---

## 🔮 Sonraki Adımlar

1. **AUR Package:** Arch User Repository'ye ekle
2. **CI/CD:** GitHub Actions ile otomatik test
3. **Documentation:** Wiki sayfaları oluştur
4. **Community:** Discord sunucusu aç
5. **Features:** Kullanıcı geri bildirimlerine göre geliştir

---

**Hazırlayan:** Berke Oruç (2009)  
**Tarih:** 2025-10-05  
**Sürüm:** v2.3.0  
**Lisans:** MIT
