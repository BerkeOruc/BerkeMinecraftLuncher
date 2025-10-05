#!/bin/bash

# Minecraft Launcher Test Scripti
# Hızlı test için

echo "🧪 Minecraft Launcher Test"
echo "========================="

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

# Launcher'ı test et
echo "🚀 Launcher başlatılıyor..."
timeout 10 python3 berke_minecraft_launcher.py || echo "⏰ Test süresi doldu"

echo "✅ Test tamamlandı"
