#!/bin/bash

# Berke Minecraft Launcher - Hızlı Başlatma
# v2.3.0

# Proje dizinine git
cd "$(dirname "$0")"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment bulunamadı!${NC}"
    echo -e "${CYAN}Oluşturuluyor...${NC}"
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment hazır${NC}"
else
    source venv/bin/activate
fi

# Python paketlerini kontrol et
if ! python -c "import rich" 2>/dev/null; then
    echo -e "${YELLOW}⚠ Gerekli paketler eksik!${NC}"
    echo -e "${CYAN}Yükleniyor...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Paketler yüklendi${NC}"
fi

# Java kontrolü
if ! command -v java &> /dev/null; then
    echo -e "${RED}✗ Java bulunamadı!${NC}"
    echo -e "${YELLOW}Lütfen Java 21+ yükleyin:${NC}"
    echo -e "${CYAN}  sudo pacman -S jdk-openjdk${NC}"
    exit 1
fi

# Launcher'ı başlat
clear
python berke_minecraft_launcher.py

# Çıkış kodu
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Launcher beklenmedik şekilde kapandı (kod: $EXIT_CODE)${NC}"
    echo -e "${YELLOW}Hata ayıklama için:${NC}"
    echo -e "${CYAN}  python berke_minecraft_launcher.py${NC}"
    echo ""
    read -p "Devam etmek için Enter'a basın..."
fi