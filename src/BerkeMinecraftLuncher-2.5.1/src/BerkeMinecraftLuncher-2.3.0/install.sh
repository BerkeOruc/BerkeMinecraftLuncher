#!/bin/bash
# BerkeMC - Otomatik Kurulum Scripti
# v2.3.1

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}║     🚀 BerkeMC - Otomatik Kurulum                              ║${NC}"
echo -e "${CYAN}║                                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

PROJECT_DIR="$(pwd)"
echo -e "📁 Proje dizini: ${CYAN}$PROJECT_DIR${NC}\n"

# Python kontrolü
echo -e "🐍 Python kontrolü..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION bulundu${NC}"
else
    echo -e "${RED}❌ Python3 bulunamadı! Lütfen Python 3.10+ kurun.${NC}"
    exit 1
fi

# Java kontrolü ve kurulumu
echo -e "\n☕ Java kontrolü..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    echo -e "${GREEN}✓ Java $JAVA_VERSION bulundu${NC}"
else
    echo -e "${YELLOW}⚠️  Java bulunamadı. Otomatik kurulum başlatılıyor...${NC}"
    
    # Arch Linux için Java kurulumu
    if command -v pacman &> /dev/null; then
        echo -e "📦 Arch Linux tespit edildi. Java kuruluyor..."
        sudo pacman -S --noconfirm jdk-openjdk
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Java başarıyla kuruldu${NC}"
        else
            echo -e "${RED}❌ Java kurulumu başarısız! Manuel kurulum gerekli.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Desteklenmeyen dağıtım! Lütfen Java'yı manuel kurun.${NC}"
        exit 1
    fi
fi

# Python bağımlılıklarını kur
echo -e "\n📦 Python bağımlılıkları kuruluyor..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python bağımlılıkları kuruldu${NC}"
    else
        echo -e "${RED}❌ Python bağımlılıkları kurulamadı!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  requirements.txt bulunamadı. Manuel kurulum yapılıyor...${NC}"
    pip3 install requests rich colorama psutil
fi

# Dosya izinlerini ayarla
echo -e "\n🔧 Dosya izinleri ayarlanıyor..."
chmod +x start.sh
chmod +x berke_minecraft_launcher.py
if [ -f "scripts/auto_optimize.sh" ]; then
    chmod +x scripts/auto_optimize.sh
fi
echo -e "${GREEN}✓ Dosya izinleri ayarlandı${NC}"

# Sistem entegrasyonu
echo -e "\n🖥️  Sistem entegrasyonu..."
read -p "Sistem genelinde 'berkemc' komutunu kurmak istiyor musunuz? (y/n): " INSTALL_SYSTEM

if [[ "$INSTALL_SYSTEM" =~ ^[Yy]$ ]]; then
    echo -e "📋 Sistem komutu kuruluyor..."
    
    # berkemc komutunu /usr/local/bin/ dizinine kopyala
    sudo cp berkemc /usr/local/bin/
    sudo chmod +x /usr/local/bin/berkemc
    
    # Desktop entry oluştur
    sudo tee /usr/share/applications/berkemc.desktop > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BerkeMC
Comment=Ultra-Fast Minecraft Launcher
Exec=/usr/local/bin/berkemc
Icon=$PROJECT_DIR/bmc_logo.png
Terminal=true
Categories=Game;
Keywords=minecraft;launcher;game;bmc;
StartupNotify=true
EOF
    
    # Desktop database güncelle
    if command -v update-desktop-database &> /dev/null; then
        sudo update-desktop-database /usr/share/applications/
    fi
    
    echo -e "${GREEN}✓ Sistem entegrasyonu tamamlandı${NC}"
    echo -e "  Komut: ${CYAN}berkemc${NC}"
    echo -e "  Menü: ${CYAN}Uygulamalar > Oyunlar > BerkeMC${NC}"
else
    echo -e "${YELLOW}⚠️  Sistem entegrasyonu atlandı${NC}"
fi

# Test çalıştırma
echo -e "\n🧪 Test çalıştırma..."
if ./start.sh --test &> /dev/null; then
    echo -e "${GREEN}✓ Launcher başarıyla test edildi${NC}"
else
    echo -e "${YELLOW}⚠️  Launcher test edilemedi, ancak kurulum tamamlandı${NC}"
fi

# Başarı raporu
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}║     ✅ KURULUM TAMAMLANDI!                                      ║${NC}"
echo -e "${GREEN}║                                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "🎯 Kullanım"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

if [[ "$INSTALL_SYSTEM" =~ ^[Yy]$ ]]; then
    echo -e "Sistem komutu: ${CYAN}berkemc${NC}"
    echo -e "Proje dizini: ${CYAN}./start.sh${NC}"
else
    echo -e "Proje dizini: ${CYAN}./start.sh${NC}"
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "🚀 Hızlı Başlangıç"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "1. Launcher'ı başlat: ${CYAN}./start.sh${NC}"
echo -e "2. Minecraft sürümü seç"
echo -e "3. Oyunu başlat"
echo -e "4. İyi oyunlar! 🎮"
echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "📚 Daha Fazla Bilgi"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "GitHub: ${CYAN}https://github.com/berke0/BerkeMinecraftLuncher${NC}"
echo -e "Sorun bildir: ${CYAN}GitHub Issues${NC}"
echo ""

read -p "Launcher'ı şimdi başlatmak istiyor musunuz? (y/n): " START_NOW
if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo -e "\n🚀 BerkeMC başlatılıyor...\n"
    ./start.sh
fi
