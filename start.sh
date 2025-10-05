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

# Sistem Python kullan (paketler zaten yüklü)
echo -e "${GREEN}✓ Sistem Python kullanılıyor${NC}"

# JAVA_HOME'u ayarla (Java 17 için)
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk"
echo -e "${GREEN}✓ JAVA_HOME ayarlandı: $JAVA_HOME${NC}"

# Java kontrolü
if ! command -v java &> /dev/null; then
    echo -e "${RED}✗ Java bulunamadı!${NC}"
    echo -e "${YELLOW}Lütfen Java 21+ yükleyin:${NC}"
    echo -e "${CYAN}  sudo pacman -S jdk-openjdk${NC}"
    exit 1
fi

# Launcher'ı başlat
if [ -t 1 ]; then
    clear
fi

# VS Code/Cursor terminal kontrolü - Her zaman dış terminalde aç
if [[ "$TERM_PROGRAM" == "cursor" ]] || [[ "$TERM_PROGRAM" == "vscode" ]] || [[ "$TERMINAL_EMULATOR" == *"cursor"* ]] || [[ "$TERM" == *"cursor"* ]]; then
    echo -e "${YELLOW}⚠️  Cursor terminal tespit edildi!${NC}"
    echo -e "${CYAN}Launcher dış terminalde açılıyor...${NC}"
    
    # Dış terminalde aç
    if command -v kitty &> /dev/null; then
        kitty --hold bash -c "cd '$PWD' && python3 berke_minecraft_launcher.py" 2>/dev/null &
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd '$PWD' && python3 berke_minecraft_launcher.py; echo ''; echo 'Çıkmak için Enter...'; read" 2>/dev/null &
    elif command -v xterm &> /dev/null; then
        xterm -e "cd '$PWD' && python3 berke_minecraft_launcher.py; echo ''; echo 'Çıkmak için Enter...'; read" 2>/dev/null &
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -e bash -c "cd '$PWD' && python3 berke_minecraft_launcher.py; echo ''; echo 'Çıkmak için Enter...'; read" 2>/dev/null &
    else
        echo -e "${RED}✗ Uygun terminal bulunamadı!${NC}"
        echo -e "${CYAN}Manuel olarak terminal açıp çalıştırın:${NC}"
        echo -e "${GREEN}  cd $PWD && python3 berke_minecraft_launcher.py${NC}"
        exit 1
    fi
    exit 0
fi

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