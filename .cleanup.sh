#!/bin/bash
# Gereksiz dosyaları temizle ve düzenle

# Gereksiz txt ve md dosyalarını docs'a taşı
mv ADIMLAR.txt BASLATMA.txt SISTEM_KURULUM.txt YENILIKLER.txt docs/ 2>/dev/null
mv FINAL_FEATURES.md FINAL_SUMMARY.md GITHUB_READY.md UI_IMPROVEMENTS.md YENILIKLER_V2.3.txt docs/ 2>/dev/null
mv OPTIMIZASYONLAR.md QUICKSTART.md docs/ 2>/dev/null

# Script dosyalarını scripts'e taşı
mv *.sh scripts/ 2>/dev/null
mv scripts/.cleanup.sh . 2>/dev/null
mv scripts/start.sh scripts/install_system.sh scripts/uninstall_system.sh . 2>/dev/null

echo "Temizlik tamamlandi!"
