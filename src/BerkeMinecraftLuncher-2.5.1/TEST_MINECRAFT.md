# 🎮 Minecraft Başlatma Test Rehberi

## ✅ Düzeltilen Sorunlar

### 1. Java 25 Deprecated Uyarısı
```
❌ ÖNCE: UseCompressedClassPointers deprecated uyarısı
✅ SONRA: Uyarı kaldırıldı, kod güncellendi
```

### 2. JNA Restricted Method Uyarısı
```
❌ ÖNCE: WARNING: java.lang.System::load has been called
✅ SONRA: --enable-native-access=ALL-UNNAMED eklendi
```

### 3. JAVA_TOOL_OPTIONS Çakışması
```
❌ ÖNCE: Picked up JAVA_TOOL_OPTIONS: -Djava.awt.headless=false
✅ SONRA: Environment'tan silindi, kod içinde yönetiliyor
```

### 4. SSL Sertifika Hatası
```
✅ SSL bypass argümanları mevcut
✅ verify=False requests için
```

## 🧪 Test Adımları

### 1. Yeni Terminal Aç
```bash
# Fish shell için environment'ı yenile
source ~/.config/fish/config.fish

# Veya yeni terminal penceresi aç
```

### 2. Launcher'ı Başlat
```bash
python /home/berke0/BerkeMinecraftLuncher/berke_minecraft_launcher.py
```

### 3. Minecraft Başlat
```
Ana Menü → 1 (Minecraft Başlat)
Sürüm: 1.21.9
```

### 4. Kontrol Et
```
✅ Mojang logo açıldı mı?
✅ Ana menü geldi mi?
✅ Log'da HATA yok mu?
```

## 📋 Beklenen Çıktı

### Doğru Başlatma:
```
🚀 Minecraft başlatılıyor...

┌─ MINECRAFT YÜKLEME ─────────────┐
│ 🎮 Sürüm: 1.21.9                │
│ ☕ Java: OpenJDK 25              │
│ 🧠 RAM: 4 GB                    │
└─────────────────────────────────┘

🎮 Minecraft başlatıldı!
📊 Kaynak İzleme Başladı...

┌─ MINECRAFT MONITOR ─────────────┐
│ ⚡ CPU: 45%                      │
│ 🧠 RAM: 2.4/4.0 GB              │
│ 🎮 GPU: 60%                     │
│ ⏱️  Uptime: 00:00:15            │
└─────────────────────────────────┘
```

### Hatalı Başlatma:
```
❌ MINECRAFT BAŞLATMA HATASI

🔍 Tespit Edilen Hatalar:
  • ClassNotFoundException
  • SSL Sertifika Hatası
  • Assets eksik
```

## 🐛 Hala Hata Alıyorsanız

### 1. Log Kontrol
```bash
tail -50 ~/.berke_minecraft_launcher/logs/minecraft_*.log
```

### 2. Assets Kontrol
```bash
ls -la ~/.minecraft/assets/objects/ | wc -l
# 4000+ olmalı
```

### 3. Sürümü Yeniden İndir
```
Ana Menü → 3 (Sürümlerim) → Sürüm Yönet → Sil
Ana Menü → 2 (Sürüm İndir) → 1.21.9 → İndir
```

### 4. Java Değiştir
```
Ana Menü → 6 (Ayarlar) → 2 (Java Yönetimi) → Java Seç
# Java 21 veya 17 dene
```

## 📊 Performans Beklentileri

### Başlatma Süresi
- İlk başlatma: ~30 saniye
- Sonraki: ~10 saniye

### RAM Kullanımı
- İlk yükleme: ~1-2 GB
- Oyunda: ~2-4 GB

### Log Mesajları
```
✅ NORMAL:
[Datafixer Bootstrap/INFO]: 278 Datafixer optimizations
[Render thread/INFO]: Environment: authHost='...'
[Render thread/INFO]: Setting user: Player123

❌ HATA:
[Render thread/ERROR]: Failed to load...
Exception in thread "main"
ClassNotFoundException
```

## ✨ Başarı Kriterleri

✅ Minecraft penceresi açıldı
✅ Mojang logo göründü
✅ Ana menü yüklendi
✅ Log'da sadece INFO/WARN var (ERROR yok)
✅ Monitor ekranı açıldı

## 🎉 Başarılı Test Sonrası

```bash
# GitHub'a yükle
cd /home/berke0/BerkeMinecraftLuncher
./publish.sh

# AUR'a yükle
# PKGBUILD ve .SRCINFO hazır!
```

---
**Test tarihi:** $(date)
**Launcher sürüm:** 2.4.0

