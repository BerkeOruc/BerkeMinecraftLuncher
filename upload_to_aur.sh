#!/bin/bash

# Berke Minecraft Launcher - AUR Upload Script
# This script helps upload the package to AUR

set -e

echo "🚀 Berke Minecraft Launcher - AUR Upload Script"
echo "================================================"

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

echo "📋 Current files for AUR:"
ls -la PKGBUILD .SRCINFO berke-minecraft-launcher.desktop setup.py

echo ""
echo "🔑 SSH Public Key (add this to your AUR account):"
echo "================================================"
cat aur_key.pub
echo "================================================"
echo ""
echo "📝 Instructions:"
echo "1. Go to https://aur.archlinux.org/account/"
echo "2. Add the SSH key above to your account"
echo "3. Clone the AUR repository:"
echo "   git clone ssh://aur@aur.archlinux.org/berke-minecraft-launcher.git"
echo "4. Copy the files to the cloned repository"
echo "5. Commit and push"
echo ""
echo "🔧 Alternative: Manual upload steps:"
echo "1. Create AUR account if you don't have one"
echo "2. Add SSH key to your account"
echo "3. Clone: git clone ssh://aur@aur.archlinux.org/berke-minecraft-launcher.git"
echo "4. Copy files: cp PKGBUILD .SRCINFO berke-minecraft-launcher.desktop setup.py berke-minecraft-launcher/"
echo "5. Commit: cd berke-minecraft-launcher && git add . && git commit -m 'Initial release' && git push"
echo ""
echo "🚀 After adding SSH key, run this command to auto-upload:"
echo "   ./auto_upload_to_aur.sh"
echo ""
echo "✅ Setup complete! Follow the instructions above to upload to AUR."
