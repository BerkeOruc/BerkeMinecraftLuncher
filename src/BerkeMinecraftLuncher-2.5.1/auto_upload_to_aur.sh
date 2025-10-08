#!/bin/bash

# Berke Minecraft Launcher - Automatic AUR Upload Script
# This script automatically uploads the package to AUR

set -e

echo "🚀 Berke Minecraft Launcher - Automatic AUR Upload"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "PKGBUILD" ]; then
    echo "❌ PKGBUILD not found! Please run this script from the project root."
    exit 1
fi

# Check if SSH key exists
if [ ! -f "aur_key" ]; then
    echo "❌ SSH key not found! Please generate it first."
    exit 1
fi

# Set SSH key for this session
export GIT_SSH_COMMAND="ssh -i $(pwd)/aur_key -o StrictHostKeyChecking=no"

echo "📦 Preparing AUR upload..."

# Create temporary directory
TEMP_DIR="/tmp/aur_upload_$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo "🔗 Cloning AUR repository..."
git clone ssh://aur@aur.archlinux.org/berkemc.git
cd berkemc

echo "📋 Copying package files..."
cp /home/berke0/BerkeMinecraftLuncher/PKGBUILD .
cp /home/berke0/BerkeMinecraftLuncher/.SRCINFO .
cp /home/berke0/BerkeMinecraftLuncher/berke-minecraft-launcher.desktop .
cp /home/berke0/BerkeMinecraftLuncher/setup.py .

echo "✅ Files copied successfully!"
echo ""
echo "📋 Files to be uploaded:"
ls -la PKGBUILD .SRCINFO berke-minecraft-launcher.desktop setup.py

echo ""
echo "📝 Commit message: Initial release v2.3.0"
echo "🚀 Uploading to AUR..."

# Add files and commit
git add .
git commit -m "Initial release v2.3.0

- Advanced Minecraft launcher with mod support
- Skin management and performance monitoring
- LWJGL native library fixes
- SSL certificate handling improvements
- Enhanced version selection and management
- AUR package ready for pacman/yay installation"

# Push to AUR
git push

echo ""
echo "✅ Successfully uploaded to AUR!"
echo ""
echo "🎉 Your package is now available at:"
echo "   https://aur.archlinux.org/packages/berkemc"
echo ""
echo "📦 Install with:"
echo "   yay -S berkemc"
echo "   # or"
echo "   pacman -S berkemc"
echo ""
echo "🔧 Cleanup..."
cd /home/berke0/BerkeMinecraftLuncher
rm -rf "$TEMP_DIR"

echo "✅ Upload complete!"
