# 🎮 BERKE MINECRAFT LAUNCHER - HIZLI BAŞLANGIÇ

## ⚡ TEK KOMUTTA KURULUM (ÖNERİLEN!)

```bash
./full_setup.sh
```

Bu komut **HER ŞEYİ** otomatik yapar:
- ✅ Java 21 kurulumu
- ✅ Python bağımlılıkları
- ✅ Wayland/Hyprland ayarları
- ✅ Minecraft dizini

Kurulum sonrası:
```bash
source ~/.bashrc  # veya yeni terminal aç
./run.sh          # Launcher'ı başlat
```

---

## 🔧 SORUN ÇÖZME

### Java Sürüm Hatası
```
Error: UnsupportedClassVersionError
class file version 65.0 (Java 21 gerekli)
```

**Çözüm:**
```bash
./install_java.sh      # Java 21 kur
./setup_java21.sh      # Java 21'i ayarla
source ~/.bashrc       # Yenile
java -version          # Kontrol et (21+ olmalı)
```

### Minecraft Başlamıyor
```bash
./debug_minecraft.sh   # Debug modunda başlat
```

veya

```bash
# Ayarlar menüsünden:
# 1. Debug Modu: Aç
# 2. Hızlı Başlatma: Kapat
# 3. Java Path: /usr/lib/jvm/java-21-openjdk/bin/java
```

---

## 📋 TÜM SCRIPTLER

### Kurulum Scriptleri
- `full_setup.sh` - Tam otomatik kurulum (ÖNERİLEN!)
- `install.sh` - Temel kurulum
- `install_java.sh` - Java 21 kurulumu
- `setup_java21.sh` - Java 21 yolu ayarlama

### Başlatma Scriptleri
- `run.sh` - Normal başlatma
- `start_minecraft.sh` - Güçlü başlatma (kontroller + otomatik düzeltme)
- `debug_minecraft.sh` - Debug modunda başlatma

### Test Scriptleri
- `quick_test.sh` - Hızlı test (15 saniye)
- `test_minecraft.sh` - Minecraft testi (30 saniye)

### Düzeltme Scriptleri
- `fix_hyprland.sh` - Hyprland/Wayland düzeltmeleri

---

## 🚀 İLK KULLANIM

1. **Kurulum Yap:**
   ```bash
   ./full_setup.sh
   source ~/.bashrc
   ```

2. **Launcher'ı Başlat:**
   ```bash
   ./run.sh
   ```

3. **İlk Adımlar:**
   - Ana menüden "2 - Sürüm İndir" seçin
   - İstediğiniz Minecraft sürümünü seçin
   - İndirme tamamlandıktan sonra "1 - Minecraft Başlat" seçin

4. **Java Uyarısı Alırsanız:**
   - Launcher otomatik tespit edecek
   - "Java 21 kurun" önerisi gösterecek
   - `./install_java.sh` ve `./setup_java21.sh` çalıştırın

---

## 💡 ÖNEMLİ NOTLAR

### Java Sürümü
- ⚠️ **Minecraft 1.18+** için **Java 21+** ZORUNLU
- ⚠️ Java 17 ile **ÇALIŞMAZ**
- ✅ Launcher otomatik Java 21 kullanır (kuruluysa)

### Hyprland/Wayland
- Launcher otomatik XWayland kullanır
- Environment değişkenleri otomatik ayarlanır
- Manuel ayar gerekmez

### Performans
- İlk başlatma 5-10 saniye sürer
- JVM optimizasyonları otomatik aktif
- Bellek kullanımı sistem belleğinin %60'ı (max 8GB)

---

## 🎮 İYİ OYUNLAR!

Sorun yaşarsanız:
1. `./debug_minecraft.sh` çalıştırın
2. Hata mesajlarını okuyun
3. Launcher otomatik çözüm önerileri sunacak

Daha fazla bilgi için: `README.md`
