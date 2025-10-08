# 🎮 Berke Minecraft Launcher v2.5.0 - Release Notes

**Tarih:** 8 Ekim 2025  
**Geliştirici:** Berke Oruç (2009)

---

## 🎉 BÜYÜK GÜNCELLEME!

Berke Minecraft Launcher'ın en kapsamlı güncellemesi! 8 yeni özellik, 15+ yeni fonksiyon ve 7,500+ satır kod.

---

## ✨ YENİ ÖZELLİKLER

### 1. 🔥🧵 Otomatik Mod Loader Kurulumu
```
• Forge - API'den otomatik sürüm algılama ve kurulum
• Fabric - Meta API ile hızlı kurulum  
• OptiFine - Manuel kurulum rehberi
```

**Kullanım:**
```
Ana Menü → Mod Yönetimi → Mod Loader Kur
→ Sürüm seç → Forge/Fabric seç → Otomatik kurulum!
```

### 2. 🔍 Gelişmiş Mod Arama ve Kurulum
```
3 Aşamalı Sistem:
1. Mod Loader seçimi (Forge/Fabric/Quilt)
2. Minecraft sürümü seçimi
3. Kategori seçimi:
   - ✅ Uyumlu Modlar (önerilen)
   - 📦 Tüm Modlar (uyumsuz uyarılı)
   - 🔍 Mod Arama (isim ile)
```

**Uyumluluk Kontrolü:**
- Uyumsuz modlar: [red]⚠️[/red] ile işaretlenir
- Kurulum öncesi detaylı uyarı
- "Yine de kur" seçeneği

### 3. 🔄 Otomatik Güncelleme Sistemi
```
• AUR'dan otomatik kontrol
• 3 seçenek:
  1. Şimdi güncelle
  2. Daha sonra
  3. Bir daha sorma
• Ayarlardan "Otomatik Güncelleme" aktif edilebilir
```

### 4. 🗑️ Launcher Tamamen Silme
```
Ayarlar → Launcher'ı Tamamen Sil
• Çift onay sistemi
• Kayıtlar korunur
• Paket kaldırma seçeneği
```

### 5. 🎨 Gelişmiş İlk Kurulum
```
6 Adımlı Kurulum Sihirbazı:
1. Java kontrolü ve otomatik kurulum
2. Kullanıcı adı ayarı
3. RAM konfigürasyonu
4. Desktop entry oluşturma
5. İlk Minecraft sürümü indirme
6. Tamamlandı ekranı
```

### 6. 🖥️ Desktop Entegrasyonu
```
• Otomatik .desktop dosyası oluşturma
• Uygulama menüsüne ekleme
• İkon desteği
• Terminal başlatma
```

---

## 🔧 İYİLEŞTİRMELER

### Modrinth API
- Tam entegrasyon
- Popüler modlar listesi
- Mod arama sistemi
- Otomatik indirme

### Java Yönetimi
- Java 25 desteği
- Uyarı mesajları kaldırıldı
- --enable-native-access=ALL-UNNAMED
- Deprecated flag'ler temizlendi

### Assets Sistemi
- Paralel indirme (16 thread)
- Hata toleranslı sistem
- Doğrulama ile indirme
- Bad PNG hatası çözüldü

---

## 🐛 HATA DÜZELTMELERİ

### Kritik Hatalar
1. ✅ **Bad PNG Signature** - Assets yeniden indirme sistemi
2. ✅ **libflite.so eksik** - flite paketi kurulumu eklendi
3. ✅ **Java 25 uyarıları** - Deprecated flagler kaldırıldı
4. ✅ **JAVA_TOOL_OPTIONS çakışması** - Environment temizlendi

### Performans
- Minecraft başlatma hızlandırıldı
- Asset indirme optimize edildi
- Mod arama hızlandırıldı

---

## 📊 İSTATİSTİKLER

| Metrik | Değer |
|--------|-------|
| **Toplam Kod** | 7,534 satır |
| **Yeni Fonksiyon** | 15+ |
| **Yeni Özellik** | 8 |
| **Hata Düzeltmesi** | 10+ |
| **API Entegrasyonu** | Modrinth, Forge, Fabric |

---

## 🚀 KURULUM

### Arch Linux (AUR)
```bash
yay -S berkemc
```

### Manuel
```bash
git clone https://github.com/berke0/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher
pip install -r requirements.txt
python berke_minecraft_launcher.py
```

---

## 📝 SONRAKİ SÜRÜM (v2.6.0) İÇİN PLANLANAN

- [ ] Profil sistemi
- [ ] Performans presetleri (Potato/Ultra)
- [ ] Backup ve restore
- [ ] Shader yönetimi
- [ ] Modpack kurulumu

---

## 🙏 TEŞEKKÜRLER

- Minecraft Community
- Modrinth API
- Forge & Fabric Teams
- Arch Linux Community

---

## 📞 İLETİŞİM

- **GitHub:** https://github.com/berke0/BerkeMinecraftLuncher
- **Email:** berke3oruc@gmail.com
- **AUR:** https://aur.archlinux.org/packages/berkemc

---

**⭐ Star'lamayı unutmayın!**  
**🐛 Bug bulursanız issue açın!**  
**🎮 İyi oyunlar!**

---

*Berke Minecraft Launcher - The Best Minecraft Launcher for Arch Linux + Hyprland*

