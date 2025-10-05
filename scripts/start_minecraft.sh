#!/bin/bash

# Güçlü Minecraft Başlatma Scripti
# Tüm sorunları çözer ve detaylı hata mesajları verir

echo "🎮 Berke Minecraft Launcher - Güçlü Başlatma"
echo "============================================="

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Hata yakalama
set -e

# Fonksiyonlar
check_java() {
    echo -e "${BLUE}☕ Java kontrolü...${NC}"
    if ! command -v java &> /dev/null; then
        echo -e "${RED}❌ Java bulunamadı!${NC}"
        echo -e "${YELLOW}📥 Java yükleniyor...${NC}"
        sudo pacman -S --noconfirm jdk21-openjdk
    else
        echo -e "${GREEN}✅ Java bulundu: $(java -version 2>&1 | head -n1)${NC}"
    fi
}

check_xwayland() {
    echo -e "${BLUE}🖥️  XWayland kontrolü...${NC}"
    if ! command -v Xwayland &> /dev/null; then
        echo -e "${YELLOW}⚠️  XWayland bulunamadı, yükleniyor...${NC}"
        sudo pacman -S --noconfirm xorg-server-xwayland
    else
        echo -e "${GREEN}✅ XWayland mevcut${NC}"
    fi
}

setup_environment() {
    echo -e "${BLUE}🌍 Environment ayarları...${NC}"
    
    # Wayland/X11 ayarları
    export GDK_BACKEND=x11
    export QT_QPA_PLATFORM=xcb
    export SDL_VIDEODRIVER=x11
    export _JAVA_AWT_WM_NONREPARENTING=1
    export AWT_TOOLKIT=MToolkit
    export DISPLAY=:0
    export WAYLAND_DISPLAY=""
    export GDK_SYNCHRONIZE=1
    
    # MESA ayarları
    export MESA_GL_VERSION_OVERRIDE=3.3
    export MESA_GLSL_VERSION_OVERRIDE=330
    export LIBGL_ALWAYS_SOFTWARE=0
    export LIBGL_ALWAYS_INDIRECT=0
    
    # Java ayarları
    export JAVA_TOOL_OPTIONS="-Djava.awt.headless=false"
    
    echo -e "${GREEN}✅ Environment değişkenleri ayarlandı${NC}"
}

check_dependencies() {
    echo -e "${BLUE}📦 Bağımlılık kontrolü...${NC}"
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment bulunamadı, oluşturuluyor...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    if ! python3 -c "import rich" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Python bağımlılıkları eksik, yükleniyor...${NC}"
        pip install -r requirements.txt
    fi
    
    echo -e "${GREEN}✅ Bağımlılıklar kontrol edildi${NC}"
}

create_directories() {
    echo -e "${BLUE}📁 Dizin kontrolü...${NC}"
    
    mkdir -p ~/.minecraft
    mkdir -p ~/.berke_minecraft_launcher/versions
    mkdir -p ~/.berke_minecraft_launcher/skins
    
    echo -e "${GREEN}✅ Dizinler hazır${NC}"
}

test_java_gui() {
    echo -e "${BLUE}🧪 Java GUI testi...${NC}"
    
    cat > /tmp/JavaGUITest.java << 'EOF'
import javax.swing.*;
import java.awt.*;

public class JavaGUITest {
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
            
            // 2 saniye bekle
            Thread.sleep(2000);
            frame.dispose();
            
        } catch (Exception e) {
            System.err.println("❌ Java GUI hatası: " + e.getMessage());
            System.exit(1);
        }
    }
}
EOF

    cd /tmp
    javac JavaGUITest.java
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Java GUI testi derlendi${NC}"
        java JavaGUITest
        echo -e "${GREEN}✅ Java GUI testi başarılı${NC}"
    else
        echo -e "${RED}❌ Java GUI testi başarısız${NC}"
    fi
    
    # Temizlik
    rm -f JavaGUITest.java JavaGUITest.class
    cd - > /dev/null
}

# Ana işlemler
echo -e "${BLUE}🚀 Başlatma işlemleri başlıyor...${NC}"

check_java
check_xwayland
setup_environment
check_dependencies
create_directories
test_java_gui

echo -e "${GREEN}🎉 Tüm kontroller tamamlandı!${NC}"
echo -e "${BLUE}🚀 Minecraft Launcher başlatılıyor...${NC}"

# Launcher'ı başlat
source venv/bin/activate
python3 berke_minecraft_launcher.py
