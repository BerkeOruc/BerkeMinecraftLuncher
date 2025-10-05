#!/bin/bash

# Berke Minecraft Launcher - Sistem Kurulumu
# v2.3.0 - Production Ready

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║       BERKE MINECRAFT LAUNCHER - SISTEM KURULUMU           ║"
echo "║                                                            ║"
echo "║                      v2.3.0                                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Root kontrolü
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}✗ Bu scripti root olarak çalıştırmayın!${NC}"
    echo -e "${YELLOW}  Normal kullanıcı olarak çalıştırın.${NC}"
    exit 1
fi

echo -e "${CYAN}[1/8] Bağımlılıklar kontrol ediliyor...${NC}"

# Arch Linux kontrolü
if ! command -v pacman &> /dev/null; then
    echo -e "${RED}✗ Bu script sadece Arch Linux için tasarlandı!${NC}"
    exit 1
fi

# Gerekli paketler
REQUIRED_PACKAGES=(
    "python"
    "python-pip"
    "jdk-openjdk"
    "xorg-server-xwayland"
    "mesa"
    "lib32-mesa"
)

MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! pacman -Qi "$pkg" &> /dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Eksik paketler bulundu: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${CYAN}Yüklemek istiyor musunuz? (y/n)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        sudo pacman -S --needed "${MISSING_PACKAGES[@]}"
    else
        echo -e "${RED}✗ Gerekli paketler yüklenmedi. Kurulum iptal edildi.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Tüm bağımlılıklar mevcut${NC}"

echo -e "${CYAN}[2/8] Python sanal ortamı oluşturuluyor...${NC}"

# Virtual environment oluştur
if [ ! -d "venv" ]; then
    python -m venv venv
    echo -e "${GREEN}✓ Virtual environment oluşturuldu${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment zaten mevcut${NC}"
fi

# Virtual environment'ı aktifleştir
source venv/bin/activate

echo -e "${CYAN}[3/8] Python paketleri yükleniyor...${NC}"

# Pip'i güncelle
pip install --upgrade pip > /dev/null 2>&1

# Requirements'ı yükle
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Python paketleri yüklendi${NC}"
else
    echo -e "${RED}✗ requirements.txt bulunamadı!${NC}"
    exit 1
fi

echo -e "${CYAN}[4/8] Launcher dosyaları kontrol ediliyor...${NC}"

# Ana dosyaları kontrol et
REQUIRED_FILES=(
    "berke_minecraft_launcher.py"
    "start.sh"
    "berkemc"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Gerekli dosya bulunamadı: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Tüm dosyalar mevcut${NC}"

echo -e "${CYAN}[5/8] Çalıştırma izinleri veriliyor...${NC}"

# Scriptlere çalıştırma izni ver
chmod +x berke_minecraft_launcher.py
chmod +x start.sh
chmod +x berkemc

echo -e "${GREEN}✓ İzinler verildi${NC}"

echo -e "${CYAN}[6/8] Sistem entegrasyonu yapılıyor...${NC}"

# berkemc komutunu /usr/local/bin'e kopyala
sudo cp berkemc /usr/local/bin/berkemc
sudo chmod +x /usr/local/bin/berkemc

echo -e "${GREEN}✓ 'berkemc' komutu sistem geneline eklendi${NC}"

echo -e "${CYAN}[7/8] .desktop dosyası oluşturuluyor...${NC}"

# .desktop dosyası oluştur
DESKTOP_FILE="$HOME/.local/share/applications/berke-minecraft-launcher.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Berke Minecraft Launcher
Comment=Ultra-Fast Minecraft Launcher for Arch Linux
Exec=$PWD/start.sh
Icon=$PWD/bmc_logo.png
Terminal=true
Categories=Game;
Keywords=minecraft;launcher;game;bmc;
StartupNotify=true
EOF

echo -e "${GREEN}✓ .desktop dosyası oluşturuldu${NC}"

echo -e "${CYAN}[8/8] Java kontrol ediliyor...${NC}"

# Java sürümünü kontrol et
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
    if [ "$JAVA_VERSION" -ge 21 ]; then
        echo -e "${GREEN}✓ Java $JAVA_VERSION kurulu (Minecraft için uygun)${NC}"
    else
        echo -e "${YELLOW}⚠ Java $JAVA_VERSION kurulu (Java 21+ önerilir)${NC}"
        echo -e "${CYAN}  Java 21 kurmak için: sudo pacman -S jdk21-openjdk${NC}"
    fi
else
    echo -e "${RED}✗ Java bulunamadı!${NC}"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              ✓ KURULUM BAŞARIYLA TAMAMLANDI!               ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Launcher'ı başlatmak için:${NC}"
echo ""
echo -e "  ${CYAN}1. Terminalden:${NC}     berkemc"
echo -e "  ${CYAN}2. Veya:${NC}            ./start.sh"
echo -e "  ${CYAN}3. Uygulama menüsünden: Berke Minecraft Launcher${NC}"
echo ""
echo -e "${YELLOW}İlk çalıştırmada:${NC}"
echo -e "  • Kullanıcı adınızı ayarlayın"
echo -e "  • Bir Minecraft sürümü indirin"
echo -e "  • Oyunun keyfini çıkarın!"
echo ""
echo -e "${CYAN}Kaldırmak için:${NC} ./uninstall_system.sh"
echo ""