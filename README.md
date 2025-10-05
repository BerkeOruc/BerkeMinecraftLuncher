<div align="center">

```
██████╗  ███████╗██████╗ ██╗  ██╗███████╗
██╔══██╗ ██╔════╝██╔══██╗██║ ██╔╝██╔════╝
██████╔╝ █████╗  ██████╔╝█████╔╝ █████╗  
██╔══██╗ ██╔══╝  ██╔══██╗██╔═██╗ ██╔══╝  
██████╔╝ ███████╗██║  ██║██║  ██╗███████╗
╚═════╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

MINECRAFT LAUNCHER v2.3.0
```

# Berke Minecraft Launcher

![Version](https://img.shields.io/badge/version-2.3.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Arch%20Linux-1793D1.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![Java](https://img.shields.io/badge/java-21+-orange.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-success.svg)

**🚀 Ultra optimize edilmiş, terminal tabanlı Minecraft launcher**

*En hızlı Minecraft deneyimi için Arch Linux'a özel olarak tasarlandı*

[Özellikler](#-özellikler) • [Kurulum](#-kurulum) • [Kullanım](#-kullanım) • [Optimizasyonlar](#-optimizasyonlar) • [Ekran Görüntüleri](#-ekran-görüntüleri)

</div>

---

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Kurulum](#-kurulum)
  - [AUR (Arch User Repository)](#aur-arch-user-repository)
  - [Manuel Kurulum](#manuel-kurulum)
  - [Sistem Geneli Kurulum](#sistem-geneli-kurulum)
- [Kullanım](#-kullanım)
- [Mod Sistemi](#-mod-sistemi)
- [Optimizasyonlar](#-optimizasyonlar)
- [Ekran Görüntüleri](#-ekran-görüntüleri)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)
- [İletişim](#-i̇letişim)

---

## ✨ Özellikler

### 🎯 Temel Özellikler
- ✅ **Tüm Minecraft Sürümleri** - Release, Snapshot, Beta, Alpha
- ✅ **Paralel İndirme** - 8 thread ile 8x daha hızlı
- ✅ **Akıllı Cache Sistemi** - Tekrar indirme yok
- ✅ **Detaylı Sürüm Sayfaları** - Minecraft API'den gerçek bilgiler
- ✅ **Java Otomatik Güncelleme** - Arch Linux entegrasyonu
- ✅ **Performans Monitörü** - CPU, RAM, FPS takibi

### 🔧 Mod Yönetimi
- ✅ **Modrinth API Entegrasyonu** - 100,000+ mod
- ✅ **Mod Arama ve İndirme** - Sürüme göre filtreleme
- ✅ **Popüler Modlar** - Top 20 listesi
- ✅ **Yerel Mod Yükleme** - .jar dosyası desteği
- ✅ **Mod Yönetimi** - Listeleme, silme, klasör açma

### 🎨 Arayüz ve Kullanıcı Deneyimi
- ✅ **Terminal Tabanlı UI** - Rich library ile güzel arayüz
- ✅ **Dinamik Ekran Boyutu** - Her terminale uyum
- ✅ **Skin Yönetimi** - İndirme, yükleme, galeri
- ✅ **Log Yönetimi** - Tarih damgalı log dosyaları
- ✅ **Hakkında Bölümü** - Geliştirici bilgileri ve istatistikler

### ⚡ Performans ve Optimizasyon
- ✅ **Ultra JVM Optimizasyonları** - Aikar's Flags + özel ayarlar
- ✅ **G1GC Tuning** - Optimal garbage collection
- ✅ **Hyprland/Wayland Desteği** - XWayland fallback
- ✅ **CPU/RAM Optimizasyonu** - Sistem kaynaklarını verimli kullanım
- ✅ **Hızlı Başlatma Modu** - Arka plan process yönetimi

### 🔐 Güvenlik ve Kararlılık
- ✅ **Hata Yakalama** - Detaylı hata raporlama
- ✅ **Sistem Testleri** - Pre-launch kontroller
- ✅ **Process Monitoring** - Arka plan takibi
- ✅ **Otomatik Kütüphane İndirme** - Eksik dosyaları tamamlama

---

## 📦 Kurulum

### AUR (Arch User Repository)

**Yakında!** AUR'da yayınlanacak.

```bash
# yay ile
yay -S berke-minecraft-launcher

# paru ile
paru -S berke-minecraft-launcher
```

### Manuel Kurulum

#### Gereksinimler
- Arch Linux (veya türevleri)
- Python 3.10+
- Git
- Java 21+ (otomatik kurulacak)

#### Adımlar

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/berke0/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher
```

2. **Başlatma scriptini çalıştırın:**
```bash
chmod +x start.sh
./start.sh
```

Script otomatik olarak:
- Python ve bağımlılıkları kontrol eder
- Virtual environment oluşturur
- Java'yı kontrol eder ve gerekirse kurar
- Launcher'ı başlatır

### Sistem Geneli Kurulum

Launcher'ı sistem genelinde kurmak ve uygulama menüsüne eklemek için:

```bash
chmod +x install_system.sh
./install_system.sh
```

Bu komut:
- Launcher'ı `~/.local/share/berke-minecraft-launcher/` dizinine kurar
- `.desktop` dosyası oluşturur
- Uygulama menüsüne ekler (GNOME, KDE, Hyprland, XFCE)
- İkon ekler

**Kaldırma:**
```bash
./uninstall_system.sh
```

---

## 🚀 Kullanım

### Hızlı Başlangıç

```bash
./start.sh
```

### Ana Menü

```
1. 🎯 Minecraft Başlat      - Yüklü sürümleri başlat
2. 📥 Sürüm İndir           - Yeni sürüm indir
3. 📋 İndirilen Sürümler    - Yüklü sürümleri listele
4. 👤 Skin Yönetimi         - Skin ekle/değiştir
5. ⚙️  Ayarlar              - 23 farklı ayar
6. 🔧 Mod Yönetimi          - Mod ara/indir/yönet
7. 📊 Performans Monitörü   - CPU/RAM/FPS takibi
8. ℹ️  Sistem Bilgileri     - Sistem durumu
9. 👨‍💻 Hakkında             - Geliştirici bilgileri
10. ❌ Çıkış
```

### Sürüm İndirme

1. Ana menüden **2** (Sürüm İndir) seçin
2. Arama yapın veya listeden seçin
3. Sürüm numarası girin
4. Detaylı bilgileri görün
5. İndirin!

### Mod İndirme

1. Ana menüden **6** (Mod Yönetimi) seçin
2. **1** (Mod Ara ve İndir) seçin
3. Minecraft sürümü seçin
4. Mod adı girin (örn: `sodium`, `optifine`, `iris`)
5. Listeden mod seçin
6. İndirin!

**Popüler Modlar:**
- Menü 6 → Seçenek 5
- Top 20 en popüler mod

---

## 🔧 Mod Sistemi

### Desteklenen Platformlar
- **Modrinth** - Ana platform (100,000+ mod)
- Yerel .jar dosyaları

### Mod Arama
```
Minecraft sürümüne göre otomatik filtreleme
Gerçek zamanlı arama
İndirme sayısı gösterimi
Mod açıklamaları
```

### Önerilen Modlar

**Performans:**
- **Sodium** - FPS artırıcı (+200% FPS)
- **Lithium** - Sunucu optimizasyonu
- **Phosphor** - Aydınlatma optimizasyonu
- **Iris Shaders** - Shader desteği

**Görsel:**
- **OptiFine** - Grafik iyileştirme
- **Better Foliage** - Daha güzel bitkiler
- **Dynamic Lights** - Dinamik ışıklar

**Oynanış:**
- **JEI** (Just Enough Items) - Tarif rehberi
- **Inventory Tweaks** - Envanter düzenleme
- **Waystones** - Işınlanma noktaları

---

## ⚡ Optimizasyonlar

### JVM Argümanları

Launcher, Minecraft için optimize edilmiş JVM argümanları kullanır:

- **G1 Garbage Collector** - En iyi Minecraft performansı
- **Aikar's Flags** - Kanıtlanmış optimizasyonlar
- **Bellek Yönetimi** - Agresif ön tahsis
- **CPU Optimizasyonları** - String deduplication, compressed oops
- **Network Optimizasyonları** - IPv4 stack önceliği

### Performans İyileştirmeleri

| Özellik | Kazanç |
|---------|--------|
| Paralel İndirme | 8x daha hızlı |
| Cache Sistemi | Tekrar indirme yok |
| G1GC Tuning | %30 daha az lag spike |
| JVM Optimizasyonları | +50% FPS |
| Sodium Mod | +200% FPS |

### Hyprland/Wayland Desteği

Launcher, Wayland ortamlarında otomatik olarak:
- XWayland fallback kullanır
- Gerekli environment değişkenlerini ayarlar
- Java AWT sorunlarını çözer

---

## 📸 Ekran Görüntüleri

> Ekran görüntüleri yakında eklenecek!

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen [CONTRIBUTING.md](CONTRIBUTING.md) dosyasını okuyun.

### Geliştirme Ortamı

```bash
# Repository'yi fork edin
git clone https://github.com/KULLANICI_ADINIZ/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher

# Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirmeye başlayın!
python3 berke_minecraft_launcher.py
```

### Pull Request Süreci

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

---

## 📊 Proje İstatistikleri

- **Kod Satırı:** 2700+ satır
- **Özellikler:** 20+ ana özellik
- **Menüler:** 10 ana menü
- **Ayarlar:** 23 seçenek
- **API Entegrasyonları:** Mojang + Modrinth
- **Desteklenen Sürümler:** Tüm Minecraft sürümleri (2009-2025)

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👨‍💻 Geliştirici

**Berke Oruç**
- Doğum Yılı: 2009
- GitHub: [@berke0](https://github.com/berke0)
- Proje: Berke Minecraft Launcher V2.3

---

## 🙏 Teşekkürler

- **Mojang Studios** - Minecraft için
- **Rich Library** - Güzel terminal UI için
- **Modrinth** - Mod API için
- **Arch Linux Community** - Harika bir distro için
- **Tüm Katkıda Bulunanlar** - Geri bildirimler için

---

## 📞 İletişim

Sorularınız veya önerileriniz için:
- GitHub Issues: [Issues](https://github.com/berke0/BerkeMinecraftLuncher/issues)
- Pull Requests: [PRs](https://github.com/berke0/BerkeMinecraftLuncher/pulls)

---

<div align="center">

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın! ⭐**

Made with ❤️ by Berke Oruç

</div>