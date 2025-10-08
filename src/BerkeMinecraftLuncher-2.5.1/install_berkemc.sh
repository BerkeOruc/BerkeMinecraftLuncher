#!/bin/bash

# Berke Minecraft Launcher - Kolay Kurulum Scripti
# Bu script berkemc'yi sisteminize kurar

set -e

echo "🚀 Berke Minecraft Launcher - Kolay Kurulum"
echo "============================================="

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Sistem kontrolü
echo "🔍 Sistem kontrolü yapılıyor..."

if ! command -v git &> /dev/null; then
    print_error "Git bulunamadı! Lütfen git'i kurun: sudo pacman -S git"
    exit 1
fi

if ! command -v makepkg &> /dev/null; then
    print_error "makepkg bulunamadı! Bu script sadece Arch Linux'ta çalışır."
    exit 1
fi

print_success "Sistem uyumlu"

# Kurulum seçenekleri
echo ""
echo "📋 Kurulum seçenekleri:"
echo "1. AUR'dan kur (önerilen)"
echo "2. GitHub'dan manuel kur"
echo "3. Mevcut paketi güncelle"
echo ""

read -p "Seçiminizi yapın (1-3): " choice

case $choice in
    1)
        print_info "AUR'dan kurulum başlatılıyor..."
        
        # Geçici dizin oluştur
        TEMP_DIR="/tmp/berkemc_install_$$"
        mkdir -p "$TEMP_DIR"
        cd "$TEMP_DIR"
        
        # AUR repository'sini klonla
        print_info "AUR repository'si klonlanıyor..."
        git clone https://aur.archlinux.org/berkemc.git
        cd berkemc
        
        # Paketi kur
        print_info "Paket kuruluyor..."
        makepkg -si
        
        # Temizlik
        cd /home
        rm -rf "$TEMP_DIR"
        
        print_success "AUR'dan kurulum tamamlandı!"
        ;;
        
    2)
        print_info "GitHub'dan manuel kurulum başlatılıyor..."
        
        # Geçici dizin oluştur
        TEMP_DIR="/tmp/berkemc_github_$$"
        mkdir -p "$TEMP_DIR"
        cd "$TEMP_DIR"
        
        # GitHub repository'sini klonla
        print_info "GitHub repository'si klonlanıyor..."
        git clone https://github.com/BerkeOruc/BerkeMinecraftLuncher.git
        cd BerkeMinecraftLuncher
        
        # Python bağımlılıklarını kur
        print_info "Python bağımlılıkları kuruluyor..."
        pip install -r requirements.txt
        
        # Executable'ı sisteme kopyala
        print_info "Executable dosyalar kopyalanıyor..."
        sudo cp berke_minecraft_launcher.py /usr/local/bin/berkemc
        sudo cp berkemc /usr/local/bin/berkemc
        sudo chmod +x /usr/local/bin/berkemc
        
        # Desktop dosyasını kopyala
        if [ -f "berke-minecraft-launcher.desktop" ]; then
            sudo cp berke-minecraft-launcher.desktop /usr/share/applications/
            print_success "Desktop dosyası kopyalandı"
        fi
        
        # Temizlik
        cd /home
        rm -rf "$TEMP_DIR"
        
        print_success "GitHub'dan kurulum tamamlandı!"
        ;;
        
    3)
        print_info "Mevcut paket güncelleniyor..."
        
        # Geçici dizin oluştur
        TEMP_DIR="/tmp/berkemc_update_$$"
        mkdir -p "$TEMP_DIR"
        cd "$TEMP_DIR"
        
        # AUR repository'sini klonla
        git clone https://aur.archlinux.org/berkemc.git
        cd berkemc
        
        # Paketi güncelle ve kur
        makepkg -si
        
        # Temizlik
        cd /home
        rm -rf "$TEMP_DIR"
        
        print_success "Paket güncellendi!"
        ;;
        
    *)
        print_error "Geçersiz seçim!"
        exit 1
        ;;
esac

echo ""
print_success "🎉 Kurulum tamamlandı!"
echo ""
print_info "🚀 Kullanım:"
echo "   berkemc"
echo ""
print_info "📋 Paket bilgileri:"
pacman -Q berkemc 2>/dev/null || echo "   Paket pacman'da görünmüyor (manuel kurulum)"
echo ""
print_info "🔗 AUR sayfası: https://aur.archlinux.org/packages/berkemc"
print_info "🔗 GitHub: https://github.com/BerkeOruc/BerkeMinecraftLuncher"
echo ""
print_success "Minecraft launcher'ınız hazır! 🎮"
