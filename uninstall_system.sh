#!/bin/bash

# Berke Minecraft Launcher - Sistem Kaldırma

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🗑️  BERKE MINECRAFT LAUNCHER - KALDIRMA 🗑️              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

INSTALL_DIR="$HOME/.local/share/berke-minecraft-launcher"
DESKTOP_FILE="$HOME/.local/share/applications/berke-minecraft-launcher.desktop"
ICON_FILE="$HOME/.local/share/icons/berke-minecraft.png"

echo -e "${YELLOW}⚠️  UYARI: Bu işlem launcher'ı sistemden kaldıracak!${NC}"
echo ""
echo -e "${BLUE}Kaldırılacak dosyalar:${NC}"
echo -e "  • $INSTALL_DIR"
echo -e "  • $DESKTOP_FILE"
echo -e "  • $ICON_FILE"
echo ""
echo -e "${YELLOW}NOT: Minecraft dosyaları (~/.minecraft) ve ayarlar silinmeyecek!${NC}"
echo ""

read -p "Kaldırmaya devam etmek istiyor musunuz? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Kaldırma iptal edildi.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🗑️  Dosyalar kaldırılıyor...${NC}"

# Dosyaları sil
rm -rf "$INSTALL_DIR"
rm -f "$DESKTOP_FILE"
rm -f "$ICON_FILE"

# Desktop veritabanını güncelle
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
fi

echo ""
echo -e "${GREEN}✅ Launcher başarıyla kaldırıldı!${NC}"
echo ""
echo -e "${YELLOW}Minecraft dosyalarınız hala şurada:${NC}"
echo -e "  ${BLUE}~/.minecraft${NC}"
echo -e "  ${BLUE}~/.berke_minecraft_launcher${NC}"
echo ""
echo -e "${YELLOW}Bu dosyaları da silmek isterseniz:${NC}"
echo -e "  ${RED}rm -rf ~/.minecraft${NC}"
echo -e "  ${RED}rm -rf ~/.berke_minecraft_launcher${NC}"
echo ""
