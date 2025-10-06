# Maintainer: Berke Oruç <berke3oruc@gmail.com>
pkgname=berkemc
pkgver=2.4.0
pkgrel=1
pkgdesc="Advanced Minecraft launcher with mod support, skin management, and performance monitoring"
arch=('any')
url="https://github.com/BerkeOruc/BerkeMinecraftLuncher"
license=('MIT')
depends=('python>=3.8' 'java-runtime>=17' 'python-requests' 'python-rich' 'python-colorama' 'python-psutil')
makedepends=('python-setuptools')
source=("berkemc-$pkgver.tar.gz::https://github.com/BerkeOruc/BerkeMinecraftLuncher/archive/v$pkgver.tar.gz")
sha256sums=('4ea5dd7cc3fbfcc214d1b960b951c50a302566e209dadd51d5e91c853e013995')

package() {
    cd "$srcdir/BerkeMinecraftLuncher-$pkgver"
    
    # Install Python package
    python setup.py install --root="$pkgdir" --optimize=1
    
    # Install launcher script
    install -Dm755 berke_minecraft_launcher.py "$pkgdir/usr/bin/berke-minecraft-launcher"
    install -Dm755 berkemc "$pkgdir/usr/bin/berkemc"
    
    # Install desktop file
    install -Dm644 berke-minecraft-launcher.desktop "$pkgdir/usr/share/applications/berke-minecraft-launcher.desktop"
    
    # Install icon
    install -Dm644 bmc_logo.png "$pkgdir/usr/share/pixmaps/berkemc.png"
    
    # Install license
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    
    # Install documentation
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
