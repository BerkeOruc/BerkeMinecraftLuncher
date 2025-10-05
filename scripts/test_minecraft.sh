#!/bin/bash

# Minecraft Test Scripti
echo "🧪 Minecraft Launcher Test Scripti"
echo "=================================="

# Environment ayarları
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
export JAVA_TOOL_OPTIONS="-Djava.awt.headless=false"

echo "✅ Environment değişkenleri ayarlandı"

# Virtual environment kontrolü
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment bulunamadı!"
    exit 1
fi

# Bağımlılık kontrolü
source venv/bin/activate
if ! python3 -c "import rich" 2>/dev/null; then
    echo "❌ Python bağımlılıkları eksik!"
    exit 1
fi

echo "✅ Bağımlılıklar kontrol edildi"

# Java kontrolü
if ! java -version 2>/dev/null; then
    echo "❌ Java bulunamadı!"
    exit 1
fi

echo "✅ Java kontrol edildi"

# Minecraft dizini kontrolü
if [ ! -d "$HOME/.minecraft" ]; then
    echo "📁 Minecraft dizini oluşturuluyor..."
    mkdir -p "$HOME/.minecraft"
fi

echo "✅ Minecraft dizini hazır"

# Launcher'ı başlat
echo "🚀 Launcher başlatılıyor..."
echo "💡 Test için '1' seçeneğini seçin ve Minecraft'ı başlatmayı deneyin"
echo "⏰ 30 saniye sonra test otomatik olarak sonlanacak"

timeout 30 python3 berke_minecraft_launcher.py || echo "⏰ Test süresi doldu"

echo "✅ Test tamamlandı"
