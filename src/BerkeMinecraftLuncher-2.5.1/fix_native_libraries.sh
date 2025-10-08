#!/bin/bash

# Berke Minecraft Launcher - Native Libraries Fix Script
# This script extracts native libraries for all downloaded versions

echo "🔧 Fixing native libraries for Berke Minecraft Launcher..."

LAUNCHER_DIR="$HOME/.berke_minecraft_launcher"
LIBRARIES_DIR="$LAUNCHER_DIR/libraries"
NATIVES_DIR="$LIBRARIES_DIR/natives/linux/x64"

# Create natives directory
mkdir -p "$NATIVES_DIR"

echo "📦 Extracting native libraries..."

# Extract all Linux native JAR files
cd "$LIBRARIES_DIR"
for jar in org/lwjgl/*/3.3.3/*-natives-linux.jar org/lwjgl/*/3.2.2/*-natives-linux.jar org/lwjgl/*/3.2.1/*-natives-linux.jar; do
    if [ -f "$jar" ]; then
        echo "  Extracting: $jar"
        unzip -q -o "$jar" -d natives/ 2>/dev/null || true
    fi
done

# Also extract from older LWJGL versions if they exist
for jar in org/lwjgl/lwjgl/lwjgl/*/*.jar; do
    if [ -f "$jar" ] && [[ "$jar" == *"natives"* ]]; then
        echo "  Extracting (legacy): $jar"
        unzip -q -o "$jar" -d natives/ 2>/dev/null || true
    fi
done

echo "✅ Native libraries extracted successfully!"

# Check if we have the main LWJGL library
if [ -f "$NATIVES_DIR/org/lwjgl/liblwjgl.so" ]; then
    echo "✅ Main LWJGL library found: $NATIVES_DIR/org/lwjgl/liblwjgl.so"
else
    echo "❌ Main LWJGL library not found!"
    echo "🔍 Available .so files:"
    find "$NATIVES_DIR" -name "*.so" 2>/dev/null || echo "  No .so files found"
fi

echo ""
echo "🎮 You can now try launching Minecraft again!"
echo "💡 If you still have issues, try:"
echo "   - Restart the launcher"
echo "   - Check Java version: java -version"
echo "   - Ensure you have Java 17+ installed"
