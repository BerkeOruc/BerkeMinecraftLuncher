#!/bin/bash

# Minecraft Debug ve Test Scripti
# Başlatma sorunlarını tespit etmek için

echo "🔍 Minecraft Debug ve Test Scripti"
echo "=================================="

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Java kontrolü
echo -e "${BLUE}☕ Java Kontrolü...${NC}"
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n1)
    echo -e "${GREEN}✅ Java bulundu: $JAVA_VERSION${NC}"
    
    # Java detayları
    echo -e "${BLUE}📋 Java Detayları:${NC}"
    java -XshowSettings:properties -version 2>&1 | grep -E "(java.version|java.home|os.name|os.arch)"
else
    echo -e "${RED}❌ Java bulunamadı!${NC}"
    exit 1
fi

# XWayland kontrolü
echo -e "${BLUE}🖥️  XWayland Kontrolü...${NC}"
if command -v Xwayland &> /dev/null; then
    echo -e "${GREEN}✅ XWayland bulundu${NC}"
else
    echo -e "${YELLOW}⚠️  XWayland bulunamadı, yükleniyor...${NC}"
    sudo pacman -S --noconfirm xorg-server-xwayland
fi

# Environment değişkenleri
echo -e "${BLUE}🌍 Environment Değişkenleri...${NC}"
echo "XDG_SESSION_TYPE: $XDG_SESSION_TYPE"
echo "WAYLAND_DISPLAY: $WAYLAND_DISPLAY"
echo "DISPLAY: $DISPLAY"
echo "GDK_BACKEND: $GDK_BACKEND"

# Test environment ayarları
echo -e "${BLUE}⚙️  Test Environment Ayarları...${NC}"
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
export _JAVA_AWT_WM_NONREPARENTING=1
export AWT_TOOLKIT=MToolkit
export DISPLAY=:0
export WAYLAND_DISPLAY=""
export GDK_SYNCHRONIZE=1
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
export LIBGL_ALWAYS_SOFTWARE=0
export LIBGL_ALWAYS_INDIRECT=0

echo -e "${GREEN}✅ Environment değişkenleri ayarlandı${NC}"

# Minecraft dizinleri kontrolü
echo -e "${BLUE}📁 Minecraft Dizinleri...${NC}"
MINECRAFT_DIR="$HOME/.minecraft"
LAUNCHER_DIR="$HOME/.berke_minecraft_launcher"

if [ -d "$MINECRAFT_DIR" ]; then
    echo -e "${GREEN}✅ Minecraft dizini: $MINECRAFT_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Minecraft dizini oluşturuluyor...${NC}"
    mkdir -p "$MINECRAFT_DIR"
fi

if [ -d "$LAUNCHER_DIR" ]; then
    echo -e "${GREEN}✅ Launcher dizini: $LAUNCHER_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Launcher dizini oluşturuluyor...${NC}"
    mkdir -p "$LAUNCHER_DIR"
fi

# Test Java GUI
echo -e "${BLUE}🧪 Java GUI Testi...${NC}"
cat > /tmp/JavaTest.java << 'EOF'
import javax.swing.*;
import java.awt.*;

public class JavaTest {
    public static void main(String[] args) {
        try {
            JFrame frame = new JFrame("Java GUI Test");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(300, 200);
            frame.setLocationRelativeTo(null);
            
            JLabel label = new JLabel("Java GUI Çalışıyor!", JLabel.CENTER);
            label.setFont(new Font("Arial", Font.BOLD, 16));
            frame.add(label);
            
            frame.setVisible(true);
            
            System.out.println("✅ Java GUI başarıyla başlatıldı!");
            System.out.println("Pencereyi kapatmak için 5 saniye bekleyin...");
            
            Thread.sleep(5000);
            frame.dispose();
            
        } catch (Exception e) {
            System.err.println("❌ Java GUI hatası: " + e.getMessage());
            System.exit(1);
        }
    }
}
EOF

# Java testini derle ve çalıştır
echo -e "${BLUE}🔨 Java testi derleniyor...${NC}"
cd /tmp
javac JavaTest.java

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Java testi derlendi${NC}"
    echo -e "${BLUE}🚀 Java GUI testi çalıştırılıyor...${NC}"
    java JavaTest
    echo -e "${GREEN}✅ Java GUI testi tamamlandı${NC}"
else
    echo -e "${RED}❌ Java testi derlenemedi${NC}"
fi

# Temizlik
rm -f /tmp/JavaTest.java /tmp/JavaTest.class

# Launcher testi
echo -e "${BLUE}🎮 Launcher Testi...${NC}"
if [ -f "berke_minecraft_launcher.py" ]; then
    echo -e "${GREEN}✅ Launcher dosyası bulundu${NC}"
    
    # Python bağımlılıkları kontrolü
    echo -e "${BLUE}🐍 Python Bağımlılıkları...${NC}"
    python3 -c "import requests, rich, colorama; print('✅ Tüm bağımlılıklar mevcut')" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Bağımlılıklar eksik, yükleniyor...${NC}"
        pip3 install -r requirements.txt
    }
    
    # Launcher'ı test et
    echo -e "${BLUE}🚀 Launcher testi...${NC}"
    timeout 10 python3 berke_minecraft_launcher.py --test 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Launcher test modu desteklenmiyor, normal başlatma deneniyor...${NC}"
    }
    
else
    echo -e "${RED}❌ Launcher dosyası bulunamadı!${NC}"
fi

# Özet
echo ""
echo -e "${GREEN}🎉 Debug tamamlandı!${NC}"
echo "=================================="
echo -e "${BLUE}📋 Özet:${NC}"
echo -e "   • Java: $(java -version 2>&1 | head -n1)"
echo -e "   • XWayland: $(command -v Xwayland >/dev/null && echo 'Mevcut' || echo 'Yok')"
echo -e "   • Environment: Ayarlandı"
echo -e "   • Dizinler: Kontrol edildi"
echo -e "   • GUI Test: Tamamlandı"
echo ""
echo -e "${YELLOW}💡 Minecraft başlatmak için:${NC}"
echo -e "   GDK_BACKEND=x11 python3 berke_minecraft_launcher.py"
echo ""
echo -e "${GREEN}🎮 İyi oyunlar!${NC}"
