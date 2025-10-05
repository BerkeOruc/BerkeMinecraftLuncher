# Changelog

Tüm önemli değişiklikler bu dosyada belgelenecektir.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardını takip eder,
ve bu proje [Semantic Versioning](https://semver.org/spec/v2.0.0.html) kullanır.

## [2.3.0] - 2025-10-04

### Eklenenler
- ✨ Tam fonksiyonel mod sistemi (Modrinth API)
- ✨ Mod arama ve indirme özelliği
- ✨ Popüler modlar listesi (Top 20)
- ✨ Yerel mod yükleme (.jar dosyası)
- ✨ Mod yönetimi (listeleme, silme, klasör açma)
- ✨ Direkt başlatma scripti (`start.sh`)
- ✨ Otomatik Java kontrolü ve kurulum
- ✨ Progress bar ile mod indirme
- ✨ Hız göstergesi (download speed)

### Değiştirildi
- 🔄 Ana menü 9 seçeneğe güncellendi
- 🔄 Mod menüsü tamamen yenilendi
- 🔄 Başlatma scripti optimize edildi

### Düzeltildi
- 🐛 Mod indirme hataları düzeltildi
- 🐛 Minecraft sürüm filtreleme iyileştirildi

## [2.2.0] - 2025-10-04

### Eklenenler
- ✨ Java otomatik güncelleme sistemi
- ✨ Detaylı sürüm sayfaları (Minecraft API entegrasyonu)
- ✨ Her sürüm için özel detay sayfası
- ✨ Sürüm sayfasından direkt indirme/başlatma/silme
- ✨ Hakkında bölümü (geliştirici bilgileri)
- ✨ Launcher istatistikleri (kod satırı, cache, vb.)
- ✨ Gelişmiş sürüm menüsü (detay sayfasına yönlendirme)

### Değiştirildi
- 🔄 Ana menü 10 seçeneğe güncellendi
- 🔄 Ayarlar menüsü 23 seçeneğe çıkarıldı
- 🔄 Sürüm menüsü kullanıcı deneyimi iyileştirildi

### Düzeltildi
- 🐛 Sürüm menüsü navigasyon hataları düzeltildi
- 🐛 Java sürüm kontrolü iyileştirildi

## [2.1.0] - 2025-10-04

### Eklenenler
- ✨ Dinamik ekran boyutu desteği
- ✨ Performans monitörü (CPU, RAM, FPS)
- ✨ Paralel indirme sistemi (8 thread)
- ✨ Akıllı cache sistemi
- ✨ Log yönetimi (tarih damgalı)
- ✨ Gelişmiş progress bar (hız göstergesi)
- ✨ Minecraft process izleme
- ✨ FPS tahmini

### Değiştirildi
- 🔄 Banner dinamik boyutlandırma
- 🔄 Başlatma sistemi geliştirildi
- 🔄 Log dosyaları otomatik oluşturuluyor

### Düzeltildi
- 🐛 Yükleme ekranı takılma sorunu çözüldü
- 🐛 PIPE buffer dolma sorunu düzeltildi
- 🐛 Process monitoring iyileştirildi

## [2.0.0] - 2025-10-03

### Eklenenler
- ✨ Skin yönetimi sistemi
- ✨ Popüler skinler galerisi
- ✨ Skin yedekleme/geri yükleme
- ✨ Gelişmiş ayarlar menüsü (22 seçenek)
- ✨ Sürüm arama ve filtreleme
- ✨ Hyprland/Wayland desteği
- ✨ Ultra JVM optimizasyonları
- ✨ Detaylı hata raporlama
- ✨ Sistem testleri
- ✨ Sistem kurulumu (.desktop dosyası)

### Değiştirildi
- 🔄 JVM argümanları Java 25 uyumlu hale getirildi
- 🔄 Kütüphane indirme sistemi eklendi
- 🔄 Classpath otomatik oluşturuluyor

### Düzeltildi
- 🐛 Java 21+ gereksinimi kontrolü
- 🐛 UnsupportedClassVersionError düzeltildi
- 🐛 LinkageError düzeltildi
- 🐛 NoClassDefFoundError düzeltildi
- 🐛 JVM creation error düzeltildi

## [1.0.0] - 2025-10-02

### Eklenenler
- ✨ İlk sürüm
- ✨ Temel Minecraft başlatma
- ✨ Sürüm indirme
- ✨ Basit ayarlar menüsü
- ✨ Terminal tabanlı UI (Rich)
- ✨ Arch Linux desteği

---

## Versiyon Formatı

**[MAJOR.MINOR.PATCH]**

- **MAJOR**: Geriye uyumsuz değişiklikler
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

## Değişiklik Tipleri

- ✨ **Eklenenler**: Yeni özellikler
- 🔄 **Değiştirildi**: Mevcut özelliklerde değişiklikler
- 🐛 **Düzeltildi**: Hata düzeltmeleri
- 🗑️ **Kaldırıldı**: Kaldırılan özellikler
- 🔒 **Güvenlik**: Güvenlik güncellemeleri
- ⚠️ **Deprecated**: Yakında kaldırılacak özellikler
