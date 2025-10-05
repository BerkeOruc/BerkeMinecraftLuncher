#!/bin/bash

# Berke Minecraft Launcher - Tam Kurulum Scripti
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║       🎮 BERKE MINECRAFT LAUNCHER - TAM KURULUM 🎮       ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hata kontrolü
set -e
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'echo -e "${RED}❌ Hata oluştu: \"${last_command}\" komutu başarısız!${NC}"' ERR

echo -e "${BLUE}📋 Adım 1/6: Sistem güncellemesi...${NC}"
sudo pacman -Syu --noconfirm || echo -e "${YELLOW}⚠️ Sistem güncellemesi atlandı${NC}"

echo ""
echo -e "${BLUE}📦 Adım 2/6: Bağımlılıklar kuruluyor...${NC}"
sudo pacman -S --needed --noconfirm python python-pip jdk-openjdk xorg-server-xwayland git || {
    echo -e "${RED}❌ Bağımlılık kurulumu başarısız!${NC}"
    exit 1
}

echo ""
echo -e "${BLUE}🐍 Adım 3/6: Python virtual environment oluşturuluyor...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment oluşturuldu${NC}"
else
    echo -e "${GREEN}✅ Virtual environment zaten mevcut${NC}"
fi

echo ""
echo -e "${BLUE}📦 Adım 4/6: Python paketleri kuruluyor...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Python paketleri kuruldu${NC}"

echo ""
echo -e "${BLUE}☕ Adım 5/6: Java 21 ayarlanıyor...${NC}"

# Java 21 yolunu bul
JAVA21_PATH=""
if [ -f "/usr/lib/jvm/java-21-openjdk/bin/java" ]; then
    JAVA21_PATH="/usr/lib/jvm/java-21-openjdk/bin/java"
elif [ -f "/usr/lib/jvm/java-openjdk/bin/java" ]; then
    JAVA21_PATH="/usr/lib/jvm/java-openjdk/bin/java"
fi

if [ -n "$JAVA21_PATH" ]; then
    echo -e "${GREEN}✅ Java 21 bulundu: $JAVA21_PATH${NC}"
    
    # Java sürümünü göster
    $JAVA21_PATH -version 2>&1 | head -n 1
    
    # Environment ayarları
    if ! grep -q "JAVA_HOME=/usr/lib/jvm/java-21-openjdk" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# Minecraft Launcher Java 21" >> ~/.bashrc
        echo "export JAVA_HOME=/usr/lib/jvm/java-21-openjdk" >> ~/.bashrc
        echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~/.bashrc
        echo -e "${GREEN}✅ .bashrc güncellendi${NC}"
    fi
    
    # Fish shell için
    if [ -f ~/.config/fish/config.fish ]; then
        if ! grep -q "JAVA_HOME /usr/lib/jvm/java-21-openjdk" ~/.config/fish/config.fish; then
            echo "" >> ~/.config/fish/config.fish
            echo "# Minecraft Launcher Java 21" >> ~/.config/fish/config.fish
            echo "set -x JAVA_HOME /usr/lib/jvm/java-21-openjdk" >> ~/.config/fish/config.fish
            echo "set -x PATH \$JAVA_HOME/bin \$PATH" >> ~/.config/fish/config.fish
            echo -e "${GREEN}✅ Fish config güncellendi${NC}"
        fi
    fi
else
    echo -e "${RED}❌ Java 21 bulunamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔧 Adım 6/6: Hyprland/Wayland ayarları...${NC}"

# Wayland environment değişkenleri
if ! grep -q "GDK_BACKEND=x11" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Minecraft Launcher Wayland/Hyprland" >> ~/.bashrc
    echo "export GDK_BACKEND=x11" >> ~/.bashrc
    echo "export QT_QPA_PLATFORM=xcb" >> ~/.bashrc
    echo "export SDL_VIDEODRIVER=x11" >> ~/.bashrc
    echo "export _JAVA_AWT_WM_NONREPARENTING=1" >> ~/.bashrc
    echo "export AWT_TOOLKIT=MToolkit" >> ~/.bashrc
    echo -e "${GREEN}✅ Wayland ayarları eklendi${NC}"
fi

# Fish shell için
if [ -f ~/.config/fish/config.fish ]; then
    if ! grep -q "GDK_BACKEND x11" ~/.config/fish/config.fish; then
        echo "" >> ~/.config/fish/config.fish
        echo "# Minecraft Launcher Wayland/Hyprland" >> ~/.config/fish/config.fish
        echo "set -x GDK_BACKEND x11" >> ~/.config/fish/config.fish
        echo "set -x QT_QPA_PLATFORM xcb" >> ~/.config/fish/config.fish
        echo "set -x SDL_VIDEODRIVER x11" >> ~/.config/fish/config.fish
        echo "set -x _JAVA_AWT_WM_NONREPARENTING 1" >> ~/.config/fish/config.fish
        echo "set -x AWT_TOOLKIT MToolkit" >> ~/.config/fish/config.fish
        echo -e "${GREEN}✅ Fish Wayland ayarları eklendi${NC}"
    fi
fi

# Minecraft dizini oluştur
mkdir -p ~/.minecraft

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}║         ✅ KURULUM BAŞARIYLA TAMAMLANDI! ✅              ║${NC}"
echo -e "${GREEN}║                                                          ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 Sonraki Adımlar:${NC}"
echo -e "${BLUE}1. Yeni terminal açın veya komutu çalıştırın:${NC}"
echo -e "   ${GREEN}source ~/.bashrc${NC}"
echo ""
echo -e "${BLUE}2. Java sürümünü kontrol edin:${NC}"
echo -e "   ${GREEN}java -version${NC} (21+ olmalı)"
echo ""
echo -e "${BLUE}3. Launcher'ı başlatın:${NC}"
echo -e "   ${GREEN}./run.sh${NC}"
echo ""
echo -e "${YELLOW}💡 İpuçları:${NC}"
echo -e "  • İlk çalıştırmada bir Minecraft sürümü indirin"
echo -e "  • Ayarlar menüsünden Java yolunu kontrol edin"
echo -e "  • Sorun yaşarsanız: ./debug_minecraft.sh"
echo ""
echo -e "${BLUE}🎮 İyi oyunlar! 🎮${NC}"
