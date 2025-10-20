#!/bin/bash

# BerkeMC v3.3.0 Release Script
# Bu script GitHub ve AUR için gerekli dosyaları hazırlar

set -e

echo "🚀 BerkeMC v3.3.0 Release Hazırlığı Başlıyor..."

# Versiyon kontrolü
VERSION="3.3.0"
echo "📦 Versiyon: $VERSION"

# Git durumunu kontrol et
if ! git diff --quiet; then
    echo "⚠️  Uncommitted changes detected. Committing changes..."
    git add .
    git commit -m "feat: v3.3.0 - Improved UI, functional mod management, enhanced skin system"
fi

# Git tag oluştur
echo "🏷️  Git tag oluşturuluyor..."
git tag -a "v$VERSION" -m "BerkeMC v$VERSION - Major UI improvements and functional mod management"

# GitHub'a push
echo "📤 GitHub'a push ediliyor..."
git push origin main
git push origin "v$VERSION"

# AUR paketi hazırla
echo "📦 AUR paketi hazırlanıyor..."

# Source tarball oluştur
TARBALL_NAME="berkemc-$VERSION.tar.gz"
echo "📁 Source tarball oluşturuluyor: $TARBALL_NAME"

# Geçici dizin oluştur
TEMP_DIR=$(mktemp -d)
REPO_NAME="BerkeMinecraftLuncher-$VERSION"

# Repo'yu kopyala
cp -r . "$TEMP_DIR/$REPO_NAME"

# Gereksiz dosyaları temizle
cd "$TEMP_DIR/$REPO_NAME"
rm -rf .git
rm -rf __pycache__
rm -rf venv
rm -rf logs/*
rm -rf pkg
rm -rf src/BerkeMinecraftLuncher-*
rm -f *.log
rm -f hs_err_pid*.log

# Tarball oluştur
cd "$TEMP_DIR"
tar -czf "$TARBALL_NAME" "$REPO_NAME"

# Tarball'ı ana dizine kopyala
cp "$TARBALL_NAME" "$HOME/BerkeMinecraftLuncher/"

# Geçici dizini temizle
rm -rf "$TEMP_DIR"

echo "✅ AUR paketi hazırlandı: $TARBALL_NAME"

# SHA256 hash hesapla
echo "🔐 SHA256 hash hesaplanıyor..."
SHA256_HASH=$(sha256sum "$TARBALL_NAME" | cut -d' ' -f1)
echo "SHA256: $SHA256_HASH"

# PKGBUILD'ı güncelle
echo "📝 PKGBUILD güncelleniyor..."
sed -i "s/sha256sums=('SKIP')/sha256sums=('$SHA256_HASH')/" PKGBUILD

echo ""
echo "🎉 Release hazırlığı tamamlandı!"
echo ""
echo "📋 Yapılacaklar:"
echo "1. GitHub Release oluştur: https://github.com/BerkeOruc/BerkeMinecraftLuncher/releases/new"
echo "2. Tag: v$VERSION"
echo "3. Title: BerkeMC v$VERSION"
echo "4. Description: CHANGELOG_v3.3.0.md içeriğini kullan"
echo "5. Asset olarak $TARBALL_NAME yükle"
echo ""
echo "📦 AUR için:"
echo "1. AUR repository'yi clone et"
echo "2. PKGBUILD ve $TARBALL_NAME dosyalarını kopyala"
echo "3. makepkg --printsrcinfo > .SRCINFO"
echo "4. git add . && git commit -m 'update to $VERSION'"
echo "5. git push"
echo ""
echo "🔗 Dosyalar:"
echo "- Tarball: $TARBALL_NAME"
echo "- PKGBUILD: PKGBUILD"
echo "- Changelog: docs/changelog/CHANGELOG_v3.3.0.md"
echo ""
echo "✨ İyi şanslar!"
