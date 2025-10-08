#!/bin/bash
# Berke Minecraft Launcher - GitHub ve AUR'a Otomatik Yükleme
set -e

VERSION=$(python3 -c "import version; print(version.__version__)")
echo "🚀 Berke Minecraft Launcher v${VERSION} Yayınlanıyor..."
echo "="* 70

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 1. Git Kontrolü
echo -e "${CYAN}📋 1/6: Git durumu kontrol ediliyor...${NC}"
git status --short

if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Değişiklikler var!${NC}"
    echo "Değişiklikler:"
    git status --short
    
    read -p "Commit yapmak ister misiniz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Commit mesajı: " commit_msg
        git add .
        git commit -m "$commit_msg"
        echo -e "${GREEN}✅ Commit yapıldı${NC}"
    fi
fi

# 2. Tag oluştur
echo -e "\n${CYAN}📋 2/6: Git tag oluşturuluyor...${NC}"
if git tag | grep -q "v${VERSION}"; then
    echo -e "${YELLOW}⚠️  v${VERSION} tag'i zaten mevcut!${NC}"
    read -p "Tag'i güncellemek ister misiniz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "v${VERSION}"
        git push origin ":refs/tags/v${VERSION}" 2>/dev/null || true
    else
        echo "Tag güncellenmedi"
    fi
fi

git tag -a "v${VERSION}" -m "Release v${VERSION}"
echo -e "${GREEN}✅ Tag oluşturuldu: v${VERSION}${NC}"

# 3. GitHub'a push
echo -e "\n${CYAN}📋 3/6: GitHub'a push yapılıyor...${NC}"
read -p "GitHub'a push yapmak ister misiniz? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    git push origin main
    git push origin "v${VERSION}"
    echo -e "${GREEN}✅ GitHub'a yüklendi!${NC}"
    echo -e "${GREEN}   https://github.com/berke0/BerkeMinecraftLuncher/releases/tag/v${VERSION}${NC}"
fi

# 4. Tarball oluştur
echo -e "\n${CYAN}📋 4/6: Tarball oluşturuluyor...${NC}"
tar_name="berkemc-${VERSION}.tar.gz"
git archive --format=tar.gz --prefix="BerkeMinecraftLuncher-${VERSION}/" -o "$tar_name" "v${VERSION}"
echo -e "${GREEN}✅ Tarball oluşturuldu: ${tar_name}${NC}"

# 5. PKGBUILD güncelle
echo -e "\n${CYAN}📋 5/6: PKGBUILD güncelleniyor...${NC}"

# SHA256 hesapla
SHA256=$(sha256sum "$tar_name" | awk '{print $1}')
echo "SHA256: $SHA256"

# PKGBUILD'i güncelle
sed -i "s/^pkgver=.*/pkgver=${VERSION}/" PKGBUILD
sed -i "s/^sha256sums=.*/sha256sums=('${SHA256}')/" PKGBUILD

echo -e "${GREEN}✅ PKGBUILD güncellendi${NC}"

# 6. .SRCINFO güncelle
echo -e "\n${CYAN}📋 6/6: .SRCINFO güncelleniyor...${NC}"
makepkg --printsrcinfo > .SRCINFO
echo -e "${GREEN}✅ .SRCINFO güncellendi${NC}"

# Özet
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 YAYINLAMA TAMAMLANDI! 🎉              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📊 Özet:${NC}"
echo -e "   Sürüm:    v${VERSION}"
echo -e "   Tarball:  ${tar_name}"
echo -e "   SHA256:   ${SHA256:0:16}..."
echo -e "   GitHub:   https://github.com/berke0/BerkeMinecraftLuncher"
echo ""
echo -e "${YELLOW}📝 Sonraki Adımlar:${NC}"
echo -e "   1. GitHub Release oluştur:"
echo -e "      ${CYAN}https://github.com/berke0/BerkeMinecraftLuncher/releases/new${NC}"
echo -e ""
echo -e "   2. AUR'a push:"
echo -e "      ${CYAN}git add PKGBUILD .SRCINFO${NC}"
echo -e "      ${CYAN}git commit -m 'Update to v${VERSION}'${NC}"
echo -e "      ${CYAN}git push${NC}"
echo ""
echo -e "${GREEN}✅ Launcher yayınlanmaya hazır!${NC}"

