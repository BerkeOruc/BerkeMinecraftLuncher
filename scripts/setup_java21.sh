#!/bin/bash

# Java 21 Yolu Ayarlama Scripti
echo "🔧 Java 21 Yolu Ayarlama"
echo "======================="

# Java 21'i bul
if [ -d "/usr/lib/jvm/java-21-openjdk" ]; then
    JAVA21_PATH="/usr/lib/jvm/java-21-openjdk/bin/java"
    echo "✅ Java 21 bulundu: $JAVA21_PATH"
elif [ -d "/usr/lib/jvm/java-openjdk" ]; then
    JAVA21_PATH="/usr/lib/jvm/java-openjdk/bin/java"
    echo "✅ Java OpenJDK bulundu: $JAVA21_PATH"
else
    echo "❌ Java 21 bulunamadı!"
    echo "💡 Önce Java 21 kurun: sudo pacman -S jdk-openjdk"
    exit 1
fi

# Java sürümünü kontrol et
echo ""
echo "🔍 Java sürümü kontrol ediliyor..."
$JAVA21_PATH -version

# Config dosyasını güncelle
CONFIG_FILE="$HOME/.minecraft_launcher/config.json"
if [ -f "$CONFIG_FILE" ]; then
    echo ""
    echo "📝 Config dosyası güncelleniyor..."
    
    # Java path'i ekle
    if grep -q "java_path" "$CONFIG_FILE"; then
        # Mevcut java_path'i güncelle
        sed -i "s|\"java_path\":.*|\"java_path\": \"$JAVA21_PATH\",|g" "$CONFIG_FILE"
        echo "✅ Config dosyası güncellendi"
    else
        echo "⚠️ Config dosyası manuel güncelleme gerektirir"
        echo "Ayarlar menüsünden Java Path'i ayarlayın: $JAVA21_PATH"
    fi
else
    echo "⚠️ Config dosyası bulunamadı, launcher ilk çalıştırmada oluşturulacak"
fi

# Environment değişkenlerini ayarla
echo ""
echo "🔧 Environment değişkenleri ayarlanıyor..."

# bashrc'ye ekle
if ! grep -q "JAVA_HOME=/usr/lib/jvm/java-21-openjdk" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Minecraft Launcher Java 21" >> ~/.bashrc
    echo "export JAVA_HOME=/usr/lib/jvm/java-21-openjdk" >> ~/.bashrc
    echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~/.bashrc
    echo "✅ .bashrc güncellendi"
fi

# fishrc'ye de ekle (eğer fish kullanılıyorsa)
if [ -f ~/.config/fish/config.fish ]; then
    if ! grep -q "JAVA_HOME /usr/lib/jvm/java-21-openjdk" ~/.config/fish/config.fish; then
        echo "" >> ~/.config/fish/config.fish
        echo "# Minecraft Launcher Java 21" >> ~/.config/fish/config.fish
        echo "set -x JAVA_HOME /usr/lib/jvm/java-21-openjdk" >> ~/.config/fish/config.fish
        echo "set -x PATH \$JAVA_HOME/bin \$PATH" >> ~/.config/fish/config.fish
        echo "✅ fish config güncellendi"
    fi
fi

echo ""
echo "✅ Tüm ayarlar tamamlandı!"
echo ""
echo "📋 Sonraki Adımlar:"
echo "1. Yeni terminal açın veya: source ~/.bashrc"
echo "2. Java sürümünü kontrol edin: java -version"
echo "3. Launcher'ı başlatın: ./run.sh"
echo "4. Ayarlar > Java Path ayarını kontrol edin"
echo ""
echo "💡 Java Path Değeri: $JAVA21_PATH"
