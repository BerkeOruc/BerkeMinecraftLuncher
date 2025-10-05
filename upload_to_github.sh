#!/bin/bash
# BerkeMC - GitHub Otomatik Yükleme Scripti
# v2.3.1

set -e  # Hata durumunda dur

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
clear
echo -e "${CYAN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🚀 BerkeMC - GitHub Otomatik Yükleme                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Proje dizini
PROJECT_DIR="/home/berke0/BerkeMinecraftLuncher"
cd "$PROJECT_DIR"

echo -e "${CYAN}📁 Proje dizini: $PROJECT_DIR${NC}\n"

# Kullanıcı bilgilerini al
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}📝 GitHub Bilgilerini Gir${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

read -p "GitHub Kullanıcı Adı: " GITHUB_USERNAME
read -p "GitHub Email: " GITHUB_EMAIL
read -p "Repository Adı (varsayılan: BerkeMinecraftLuncher): " REPO_NAME
REPO_NAME=${REPO_NAME:-BerkeMinecraftLuncher}

echo ""
read -p "Sürüm numarası (varsayılan: 2.3.1): " VERSION
VERSION=${VERSION:-2.3.1}

echo ""
echo -e "${GREEN}✓ Bilgiler alındı!${NC}\n"

# Git config ayarla
echo -e "${CYAN}⚙️  Git yapılandırması...${NC}"
git config --global user.name "$GITHUB_USERNAME"
git config --global user.email "$GITHUB_EMAIL"
echo -e "${GREEN}✓ Git yapılandırıldı${NC}\n"

# Git init (eğer yapılmadıysa)
if [ ! -d ".git" ]; then
    echo -e "${CYAN}🔧 Git repository başlatılıyor...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository başlatıldı${NC}\n"
else
    echo -e "${GREEN}✓ Git repository zaten var${NC}\n"
fi

# .gitignore kontrolü
if [ ! -f ".gitignore" ]; then
    echo -e "${CYAN}📝 .gitignore oluşturuluyor...${NC}"
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Logs
logs/
*.log
*.log.gz

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Minecraft
.minecraft/
.berke_minecraft_launcher/

# Temporary
*.tmp
*.temp
GITIGNORE
    echo -e "${GREEN}✓ .gitignore oluşturuldu${NC}\n"
fi

# LICENSE kontrolü
if [ ! -f "LICENSE" ]; then
    echo -e "${CYAN}📜 MIT LICENSE oluşturuluyor...${NC}"
    YEAR=$(date +%Y)
    cat > LICENSE << LICENSE_TEXT
MIT License

Copyright (c) $YEAR $GITHUB_USERNAME

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
LICENSE_TEXT
    echo -e "${GREEN}✓ LICENSE oluşturuldu${NC}\n"
fi

# PKGBUILD email güncelle
echo -e "${CYAN}📦 PKGBUILD email güncelleniyor...${NC}"
sed -i "s/your-email@example.com/$GITHUB_EMAIL/g" PKGBUILD
echo -e "${GREEN}✓ PKGBUILD güncellendi${NC}\n"

# Dosyaları ekle
echo -e "${CYAN}📂 Dosyalar git'e ekleniyor...${NC}"
git add .
echo -e "${GREEN}✓ Dosyalar eklendi${NC}\n"

# Commit
echo -e "${CYAN}💾 Commit yapılıyor...${NC}"
COMMIT_MSG="v$VERSION - Ultra Fast Minecraft Launcher

✨ Özellikler:
- Tüm Minecraft sürümleri (alpha → latest)
- Online sunucu desteği
- Ultra hızlı indirme (16 thread)
- Performans ayarları (4 profil)
- Skin/Mod yönetimi
- Wayland/Hyprland desteği
- JVM optimizasyonları

🚀 Production Ready"

git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Commit yapıldı${NC}\n"

# Remote kontrol
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}⚠️  Remote 'origin' zaten var, güncelleniyor...${NC}"
    git remote set-url origin "$REMOTE_URL"
else
    echo -e "${CYAN}🔗 Remote ekleniyor...${NC}"
    git remote add origin "$REMOTE_URL"
fi
echo -e "${GREEN}✓ Remote: $REMOTE_URL${NC}\n"

# Branch
echo -e "${CYAN}🌿 Branch 'main' oluşturuluyor...${NC}"
git branch -M main
echo -e "${GREEN}✓ Branch hazır${NC}\n"

# GitHub'da repository oluşturma talimatı
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}📢 ÖNEMLİ: GitHub'da Repository Oluştur${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}1. Tarayıcıda aç: ${GREEN}https://github.com/new${NC}"
echo -e "${CYAN}2. Repository name: ${GREEN}$REPO_NAME${NC}"
echo -e "${CYAN}3. Description: ${GREEN}Ultra-fast Minecraft launcher for Arch Linux${NC}"
echo -e "${CYAN}4. Public seç${NC}"
echo -e "${CYAN}5. ${RED}README, .gitignore, LICENSE ekleme!${NC} (zaten var)"
echo -e "${CYAN}6. 'Create repository' butonuna bas${NC}\n"

read -p "Repository oluşturdun mu? (e/h): " REPO_CREATED

if [[ ! "$REPO_CREATED" =~ ^[Ee]$ ]]; then
    echo -e "\n${YELLOW}⚠️  Önce GitHub'da repository oluştur, sonra scripti tekrar çalıştır.${NC}"
    exit 1
fi

echo ""

# GitHub oturum kontrolü
echo -e "${CYAN}🔐 GitHub oturum kontrolü...${NC}\n"

if command -v gh &> /dev/null; then
    # GitHub CLI varsa kullan
    echo -e "${GREEN}✓ GitHub CLI bulundu${NC}"
    
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓ GitHub'a zaten giriş yapılmış${NC}\n"
    else
        echo -e "${YELLOW}⚠️  GitHub'a giriş yapılıyor...${NC}"
        gh auth login
        echo -e "${GREEN}✓ GitHub'a giriş yapıldı${NC}\n"
    fi
else
    # GitHub CLI yoksa, credential helper kullan
    echo -e "${YELLOW}⚠️  GitHub CLI bulunamadı${NC}"
    echo -e "${CYAN}💡 Git credential helper ayarlanıyor...${NC}"
    
    git config --global credential.helper store
    
    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🔑 GitHub Personal Access Token Gerekli${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${CYAN}1. Tarayıcıda aç: ${GREEN}https://github.com/settings/tokens/new${NC}"
    echo -e "${CYAN}2. Note: ${GREEN}BerkeMC Launcher${NC}"
    echo -e "${CYAN}3. Expiration: ${GREEN}No expiration${NC} (veya 1 year)"
    echo -e "${CYAN}4. Scopes: ${GREEN}repo${NC} (tüm kutucukları işaretle)"
    echo -e "${CYAN}5. 'Generate token' butonuna bas${NC}"
    echo -e "${CYAN}6. Token'ı kopyala (bir daha göremezsin!)${NC}\n"
    
    read -p "Token oluşturdun mu? (e/h): " TOKEN_CREATED
    
    if [[ ! "$TOKEN_CREATED" =~ ^[Ee]$ ]]; then
        echo -e "\n${YELLOW}⚠️  Token oluştur ve scripti tekrar çalıştır.${NC}"
        exit 1
    fi
    
    echo ""
fi

# Push
echo -e "${CYAN}🚀 GitHub'a yükleniyor...${NC}\n"

if git push -u origin main; then
    echo -e "\n${GREEN}✓ Kod başarıyla GitHub'a yüklendi!${NC}\n"
else
    echo -e "\n${RED}❌ Push başarısız!${NC}"
    echo -e "${YELLOW}Muhtemel sebepler:${NC}"
    echo -e "  1. Repository oluşturulmadı"
    echo -e "  2. Token yanlış veya yetkisiz"
    echo -e "  3. Repository adı yanlış"
    echo -e "\n${CYAN}Çözüm:${NC}"
    echo -e "  1. https://github.com/$GITHUB_USERNAME/$REPO_NAME adresini kontrol et"
    echo -e "  2. Token'ı yeniden oluştur"
    echo -e "  3. Scripti tekrar çalıştır"
    exit 1
fi

# Tag oluştur
echo -e "${CYAN}🏷️  Release tag oluşturuluyor...${NC}"
git tag -a "v$VERSION" -m "Release v$VERSION - Production Ready"

echo -e "${CYAN}🚀 Tag GitHub'a yükleniyor...${NC}"
git push origin "v$VERSION"
echo -e "${GREEN}✓ Tag yüklendi${NC}\n"

# Başarı mesajı
clear
echo -e "${GREEN}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     ✅ BAŞARILI! GitHub'a Yüklendi!                           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}\n"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📦 Proje Bilgileri${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}Repository:${NC} ${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
echo -e "${CYAN}Sürüm:${NC} ${GREEN}v$VERSION${NC}"
echo -e "${CYAN}Branch:${NC} ${GREEN}main${NC}"
echo -e "${CYAN}Commit:${NC} ${GREEN}$(git rev-parse --short HEAD)${NC}\n"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎯 Sonraki Adımlar${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}1. GitHub'da Release Oluştur:${NC}"
echo -e "   ${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/new${NC}"
echo -e "   Tag: ${GREEN}v$VERSION${NC}"
echo -e "   Title: ${GREEN}v$VERSION - Ultra Fast Edition${NC}\n"

echo -e "${CYAN}2. AUR'a Yükle:${NC}"
echo -e "   ${GREEN}cat AUR_KURULUM_REHBERI.md${NC}\n"

echo -e "${CYAN}3. Test Et:${NC}"
echo -e "   ${GREEN}git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git${NC}"
echo -e "   ${GREEN}cd $REPO_NAME && ./start.sh${NC}\n"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Proje Hazır!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Repository'yi tarayıcıda aç? (e/h):${NC} "
read -p "" OPEN_BROWSER

if [[ "$OPEN_BROWSER" =~ ^[Ee]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    elif command -v firefox &> /dev/null; then
        firefox "https://github.com/$GITHUB_USERNAME/$REPO_NAME" &
    else
        echo -e "${YELLOW}Tarayıcı bulunamadı. Manuel aç:${NC}"
        echo -e "${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
    fi
fi

echo -e "\n${GREEN}İyi oyunlar ve başarılı yayınlar! 🎮🚀${NC}\n"
