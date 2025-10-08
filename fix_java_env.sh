#!/bin/bash
# JAVA_TOOL_OPTIONS temizleme scripti

echo "🔧 Java Environment Temizleme"
echo "═══════════════════════════════════════"

# Kontrol et
if [ ! -z "$JAVA_TOOL_OPTIONS" ]; then
    echo "⚠️  JAVA_TOOL_OPTIONS bulundu: $JAVA_TOOL_OPTIONS"
else
    echo "✅ JAVA_TOOL_OPTIONS yok"
fi

if [ ! -z "$_JAVA_OPTIONS" ]; then
    echo "⚠️  _JAVA_OPTIONS bulundu: $_JAVA_OPTIONS"
else
    echo "✅ _JAVA_OPTIONS yok"
fi

echo ""
echo "🧹 Temizleme..."

# Fish shell için
if [ -f ~/.config/fish/config.fish ]; then
    echo "📝 Fish config temizleniyor..."
    sed -i '/JAVA_TOOL_OPTIONS/d' ~/.config/fish/config.fish
    sed -i '/_JAVA_OPTIONS/d' ~/.config/fish/config.fish
    sed -i '/JDK_JAVA_OPTIONS/d' ~/.config/fish/config.fish
fi

# Bash/Zsh için
for file in ~/.bashrc ~/.zshrc ~/.profile ~/.bash_profile; do
    if [ -f "$file" ]; then
        echo "📝 $file temizleniyor..."
        sed -i '/JAVA_TOOL_OPTIONS/d' "$file"
        sed -i '/_JAVA_OPTIONS/d' "$file"
        sed -i '/JDK_JAVA_OPTIONS/d' "$file"
    fi
done

# /etc/environment
if grep -q "JAVA_TOOL_OPTIONS" /etc/environment 2>/dev/null; then
    echo "⚠️  /etc/environment içinde JAVA_TOOL_OPTIONS var!"
    echo "   Kaldırmak için: sudo sed -i '/JAVA_TOOL_OPTIONS/d' /etc/environment"
fi

echo ""
echo "✅ Temizleme tamamlandı!"
echo ""
echo "📝 Değişikliklerin aktif olması için:"
echo "   • Terminal'i yeniden başlatın"
echo "   • Veya: source ~/.config/fish/config.fish"
echo ""

