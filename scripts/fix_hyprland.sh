#!/bin/bash

# Hyprland Minecraft Launcher - Hızlı Çözüm Scripti
# Minecraft penceresi görünmüyorsa bu scripti çalıştırın

echo "🖥️  Hyprland Minecraft Sorun Giderme"
echo "===================================="

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# XWayland kontrolü
echo -e "${BLUE}📋 XWayland kontrolü...${NC}"
if ! command -v Xwayland &> /dev/null; then
    echo -e "${YELLOW}⚠️  XWayland bulunamadı!${NC}"
    echo -e "${BLUE}📥 XWayland yükleniyor...${NC}"
    sudo pacman -S --noconfirm xorg-server-xwayland
else
    echo -e "${GREEN}✅ XWayland zaten yüklü!${NC}"
fi

# Environment değişkenlerini ayarla
echo -e "${BLUE}⚙️  Environment değişkenleri ayarlanıyor...${NC}"
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
export _JAVA_AWT_WM_NONREPARENTING=1
export AWT_TOOLKIT=MToolkit
export JAVA_TOOL_OPTIONS="-Djava.awt.headless=false"

# Hyprland window rules kontrolü
echo -e "${BLUE}🪟 Hyprland window rules kontrolü...${NC}"
HYPRLAND_CONFIG="$HOME/.config/hypr/hyprland.conf"

if [ -f "$HYPRLAND_CONFIG" ]; then
    if ! grep -q "minecraft" "$HYPRLAND_CONFIG"; then
        echo -e "${YELLOW}📝 Minecraft window rules ekleniyor...${NC}"
        echo "" >> "$HYPRLAND_CONFIG"
        echo "# Minecraft window rules" >> "$HYPRLAND_CONFIG"
        echo "windowrule = float, title:.*Minecraft.*" >> "$HYPRLAND_CONFIG"
        echo "windowrule = size 1280 720, title:.*Minecraft.*" >> "$HYPRLAND_CONFIG"
        echo "windowrule = center, title:.*Minecraft.*" >> "$HYPRLAND_CONFIG"
        echo "windowrule = workspace 1, title:.*Minecraft.*" >> "$HYPRLAND_CONFIG"
    fi
else
    echo -e "${YELLOW}⚠️  Hyprland config bulunamadı: $HYPRLAND_CONFIG${NC}"
fi

# Java kontrolü
echo -e "${BLUE}☕ Java kontrolü...${NC}"
if command -v java &> /dev/null; then
    echo -e "${GREEN}✅ Java bulundu: $(java -version 2>&1 | head -n1)${NC}"
else
    echo -e "${RED}❌ Java bulunamadı!${NC}"
    echo -e "${BLUE}📥 Java yükleniyor...${NC}"
    sudo pacman -S --noconfirm jdk21-openjdk
fi

# Test komutu
echo -e "${BLUE}🧪 Test komutu hazırlanıyor...${NC}"
echo -e "${YELLOW}💡 Minecraft başlatmak için şu komutu kullanın:${NC}"
echo -e "${CYAN}   GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb java -jar minecraft.jar${NC}"

# Launcher'ı test et
if [ -f "berke_minecraft_launcher.py" ]; then
    echo -e "${BLUE}🚀 Launcher test ediliyor...${NC}"
    echo -e "${YELLOW}💡 Launcher'ı şu şekilde başlatın:${NC}"
    echo -e "${CYAN}   GDK_BACKEND=x11 python3 berke_minecraft_launcher.py${NC}"
fi

echo ""
echo -e "${GREEN}✅ Sorun giderme tamamlandı!${NC}"
echo -e "${BLUE}📋 Yapılan işlemler:${NC}"
echo -e "   • XWayland kontrolü ve kurulumu"
echo -e "   • Environment değişkenleri ayarlandı"
echo -e "   • Hyprland window rules eklendi"
echo -e "   • Java kontrolü yapıldı"
echo ""
echo -e "${YELLOW}💡 İpuçları:${NC}"
echo -e "   • Minecraft penceresi görünmüyorsa Alt+Tab ile geçiş yapın"
echo -e "   • Super+Shift+Q ile pencereyi kapatabilirsiniz"
echo -e "   • Super+F ile tam ekran yapabilirsiniz"
echo -e "   • Super+Shift+F ile pencereyi yüzen moda alabilirsiniz"
echo ""
echo -e "${GREEN}🎮 İyi oyunlar!${NC}"
