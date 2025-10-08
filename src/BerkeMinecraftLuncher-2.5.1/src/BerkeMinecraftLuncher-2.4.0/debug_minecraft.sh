#!/bin/bash

# Minecraft Debug Script - Wayland/Hyprland Fix
echo "🔧 Minecraft Debug Script - Wayland/Hyprland Fix"
echo ""

# Environment variables
export GDK_BACKEND=x11
export QT_QPA_PLATFORM=xcb
export SDL_VIDEODRIVER=x11
export MOZ_ENABLE_WAYLAND=0
export _JAVA_AWT_WM_NONREPARENTING=1
export AWT_TOOLKIT=MToolkit
export JAVA_TOOL_OPTIONS="-Djava.awt.headless=false"
export DISPLAY=${DISPLAY:-:0}
export WAYLAND_DISPLAY=""
export HYPRLAND_INSTANCE_SIGNATURE=""
export GDK_SYNCHRONIZE=1
export LIBGL_ALWAYS_SOFTWARE=0
export LIBGL_ALWAYS_INDIRECT=0
export MESA_GL_VERSION_OVERRIDE=4.5
export MESA_GLSL_VERSION_OVERRIDE=450
export vblank_mode=0
export __GL_THREADED_OPTIMIZATIONS=1
export MESA_NO_ERROR=1
export DRI_PRIME=1

echo "🌍 Environment Variables:"
echo "DISPLAY: $DISPLAY"
echo "GDK_BACKEND: $GDK_BACKEND"
echo "QT_QPA_PLATFORM: $QT_QPA_PLATFORM"
echo "SDL_VIDEODRIVER: $SDL_VIDEODRIVER"
echo ""

# Check XWayland
echo "🔍 Checking XWayland:"
if pgrep -f "Xwayland" > /dev/null; then
    echo "✅ XWayland is running"
else
    echo "❌ XWayland is not running"
fi

# Check X11 display
echo "🔍 Checking X11 Display:"
if xdpyinfo > /dev/null 2>&1; then
    echo "✅ X11 display is working"
    xdpyinfo | grep -E "(name of display|version number|screen number)"
else
    echo "❌ X11 display is not working"
fi

echo ""
echo "🚀 Starting Minecraft with debug info..."

# Start Minecraft with debug
cd /home/berke0/BerkeMinecraftLuncher
python3 berke_minecraft_launcher.py
