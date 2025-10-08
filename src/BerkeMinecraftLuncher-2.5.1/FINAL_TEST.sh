#!/bin/bash
# MINECRAFT FINAL TEST

clear
echo "╔════════════════════════════════════════╗"
echo "║  🎮 MINECRAFT FINAL TEST 🎮           ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "✅ Düzeltmeler:"
echo "  1. Assets temizlendi (bozuk PNG'ler silindi)"
echo "  2. Flite kuruldu (narrator çalışacak)"
echo "  3. Java 25 uyarıları düzeltildi"
echo "  4. JAVA_TOOL_OPTIONS temizlendi"
echo ""
echo "📋 Test Adımları:"
echo "  1. Launcher'ı başlat"
echo "  2. Sürüm İndir → 1.21.9 (assets yeniden inecek)"
echo "  3. Minecraft Başlat → 1.21.9"
echo "  4. ✅ Açılmalı!"
echo ""
echo "🚀 Launcher başlatılıyor..."
echo ""

cd /home/berke0/BerkeMinecraftLuncher
python berke_minecraft_launcher.py

