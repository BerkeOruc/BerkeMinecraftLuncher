# Maintainer: Berke Oruc <berke3oruc@gmail.com>
pkgname=berkemc
pkgver=2.3.1
pkgrel=1
pkgdesc="Ultra-fast terminal-based Minecraft launcher optimized for Arch Linux"
arch=('any')
url="https://github.com/berke0/BerkeMinecraftLuncher"
license=('MIT')
depends=(
    'python>=3.10'
    'python-requests'
    'python-rich'
    'python-colorama'
    'python-psutil'
    'jdk-openjdk'
)
optdepends=(
    'hyprland: Wayland compositor support'
    'xorg-server: X11 support'
)
makedepends=('git')
source=("git+https://github.com/berke0/BerkeMinecraftLuncher.git")
sha256sums=('SKIP')

package() {
    cd "$srcdir/BerkeMinecraftLuncher"
    
    # Ana dizini oluştur
    install -dm755 "$pkgdir/opt/$pkgname"
    install -dm755 "$pkgdir/usr/bin"
    install -dm755 "$pkgdir/usr/share/applications"
    install -dm755 "$pkgdir/usr/share/pixmaps"
    install -dm755 "$pkgdir/usr/share/doc/$pkgname"
    
    # Python scriptini kopyala
    install -Dm755 berke_minecraft_launcher.py "$pkgdir/opt/$pkgname/berke_minecraft_launcher.py"
    
    # Başlatma scriptini kopyala
    install -Dm755 start.sh "$pkgdir/opt/$pkgname/start.sh"
    
    # Sistem komutu oluştur
    cat > "$pkgdir/usr/bin/berkemc" << 'EOF'
#!/bin/bash
cd /opt/berke-minecraft-launcher
exec ./start.sh "$@"
EOF
    chmod +x "$pkgdir/usr/bin/berkemc"
    
    # Desktop entry
    cat > "$pkgdir/usr/share/applications/$pkgname.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BerkeMC
Comment=Ultra-Fast Minecraft Launcher for Arch Linux
Exec=berkemc
Icon=berkemc
Terminal=true
Categories=Game;
Keywords=minecraft;launcher;game;bmc;berkemc;
StartupNotify=true
EOF
    
    # Logo
    if [ -f "bmc_logo.png" ]; then
        install -Dm644 bmc_logo.png "$pkgdir/usr/share/pixmaps/$pkgname.png"
    fi
    
    # Dokümantasyon
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    
    if [ -f "ULTRA_OPTIMIZATION_GUIDE.md" ]; then
        install -Dm644 ULTRA_OPTIMIZATION_GUIDE.md "$pkgdir/usr/share/doc/$pkgname/ULTRA_OPTIMIZATION_GUIDE.md"
    fi
    
    if [ -f "GITHUB_GUIDE.md" ]; then
        install -Dm644 GITHUB_GUIDE.md "$pkgdir/usr/share/doc/$pkgname/GITHUB_GUIDE.md"
    fi
    
    # Scripts dizini
    if [ -d "scripts" ]; then
        install -dm755 "$pkgdir/opt/$pkgname/scripts"
        install -Dm755 scripts/*.sh "$pkgdir/opt/$pkgname/scripts/" 2>/dev/null || true
    fi
}