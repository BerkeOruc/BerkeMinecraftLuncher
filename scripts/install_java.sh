#!/bin/bash

# Java Kurulum Scripti
echo "☕ Java Kurulum Scripti"
echo "======================"

# Mevcut Java sürümünü kontrol et
echo "🔍 Mevcut Java sürümü kontrol ediliyor..."
if command -v java &> /dev/null; then
    java_version=$(java -version 2>&1 | head -n 1 | cut -d '"' -f 2 | cut -d '.' -f 1)
    echo "📋 Mevcut Java sürümü: $java_version"
    
    if [ "$java_version" -ge 21 ]; then
        echo "✅ Java sürümü uygun (21+)"
        exit 0
    else
        echo "⚠️ Java sürümü eski ($java_version), Java 21+ gerekli"
    fi
else
    echo "❌ Java bulunamadı"
fi

echo ""
echo "📦 Java 21 OpenJDK kuruluyor..."

# Java 21 OpenJDK kur
if sudo pacman -S --noconfirm jdk-openjdk; then
    echo "✅ Java 21 OpenJDK başarıyla kuruldu"
    
    # JAVA_HOME ayarla
    echo "🔧 JAVA_HOME ayarlanıyor..."
    echo 'export JAVA_HOME=/usr/lib/jvm/java-21-openjdk' >> ~/.bashrc
    echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc
    
    echo "✅ JAVA_HOME ayarlandı"
    echo "🔄 Yeni terminal açın veya 'source ~/.bashrc' çalıştırın"
    
    # Yeni Java sürümünü kontrol et
    echo ""
    echo "🔍 Yeni Java sürümü kontrol ediliyor..."
    /usr/lib/jvm/java-21-openjdk/bin/java -version
    
else
    echo "❌ Java kurulumu başarısız!"
    echo "💡 Manuel kurulum için:"
    echo "   sudo pacman -S jdk-openjdk"
    exit 1
fi

echo ""
echo "🎮 Artık Minecraft'ı başlatabilirsiniz!"
