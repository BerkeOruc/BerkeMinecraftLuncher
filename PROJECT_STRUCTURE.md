# 📁 Proje Yapısı

Berke Minecraft Launcher proje dosya yapısı ve açıklamaları.

## 📂 Dizin Yapısı

```
BerkeMinecraftLuncher/
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD
├── venv/                             # Python virtual environment
├── berke_minecraft_launcher.py       # Ana launcher kodu (2700+ satır)
├── version.py                        # Sürüm bilgileri
├── requirements.txt                  # Python bağımlılıkları
├── start.sh                          # Direkt başlatma scripti (ÖNERİLEN)
├── FIX_AND_START.sh                  # Eski başlatma scripti
├── install.sh                        # İlk kurulum scripti
├── install_system.sh                 # Sistem geneli kurulum
├── uninstall_system.sh               # Sistem geneli kaldırma
├── berke-minecraft-launcher.desktop  # Desktop entry dosyası
├── PKGBUILD                          # AUR paketi için
├── README.md                         # Ana dokümantasyon
├── LICENSE                           # MIT lisansı
├── CONTRIBUTING.md                   # Katkıda bulunma rehberi
├── CHANGELOG.md                      # Sürüm geçmişi
├── INSTALL.md                        # Kurulum rehberi
├── PROJECT_STRUCTURE.md              # Bu dosya
├── .gitignore                        # Git ignore kuralları
├── YENILIKLER_V2.3.txt               # Son sürüm notları
└── (Diğer yardımcı scriptler)
```

## 📄 Dosya Açıklamaları

### Ana Dosyalar

#### `berke_minecraft_launcher.py`
**Ana launcher kodu** - 2700+ satır Python kodu
- MinecraftLauncher class
- Tüm özellikler ve fonksiyonlar
- UI/UX yönetimi
- API entegrasyonları

#### `version.py`
**Sürüm bilgileri**
- Sürüm numarası (2.3.0)
- Build bilgileri
- Feature flags
- Geliştirici bilgileri

#### `requirements.txt`
**Python bağımlılıkları**
```
requests>=2.31.0
colorama>=0.4.6
rich>=13.7.0
click>=8.1.7
psutil>=5.9.6
```

### Başlatma Scriptleri

#### `start.sh` ⭐ ÖNERİLEN
**Direkt başlatma scripti**
- Tek komutla başlatma
- Otomatik Python kontrolü
- Otomatik venv oluşturma
- Otomatik bağımlılık kurulumu
- Otomatik Java kontrolü ve kurulum
- Güzel renkli çıktı

#### `FIX_AND_START.sh`
**Eski başlatma scripti**
- Java ortamı düzeltme
- Launcher başlatma
- Geriye dönük uyumluluk için korunuyor

#### `install.sh`
**İlk kurulum scripti**
- Sistem bağımlılıklarını kurar
- Virtual environment oluşturur
- Python paketlerini yükler

### Sistem Kurulum Dosyaları

#### `install_system.sh`
**Sistem geneli kurulum**
- `~/.local/share/berke-minecraft-launcher/` dizinine kurar
- `.desktop` dosyası oluşturur
- Uygulama menüsüne ekler
- İkon ekler

#### `uninstall_system.sh`
**Sistem geneli kaldırma**
- Tüm kurulum dosyalarını siler
- `.desktop` dosyasını kaldırır
- Icon cache'i günceller

#### `berke-minecraft-launcher.desktop`
**Desktop entry dosyası**
- Uygulama menüsü entegrasyonu
- GNOME, KDE, Hyprland, XFCE desteği

### Paket Yönetimi

#### `PKGBUILD`
**AUR paketi için**
- Arch Linux paket tanımı
- Bağımlılıklar
- Kurulum talimatları
- AUR'da yayınlanacak

### Dokümantasyon

#### `README.md`
**Ana dokümantasyon**
- Proje tanıtımı
- Özellikler listesi
- Kurulum talimatları
- Kullanım örnekleri
- Ekran görüntüleri

#### `LICENSE`
**MIT Lisansı**
- Açık kaynak lisansı
- Kullanım hakları
- Sorumluluk reddi

#### `CONTRIBUTING.md`
**Katkıda bulunma rehberi**
- Davranış kuralları
- Geliştirme ortamı kurulumu
- Kod standartları
- Pull request süreci

#### `CHANGELOG.md`
**Sürüm geçmişi**
- Tüm sürüm notları
- Değişiklik logları
- Semantic versioning

#### `INSTALL.md`
**Kurulum rehberi**
- Detaylı kurulum adımları
- Sistem gereksinimleri
- Sorun giderme
- İpuçları

#### `PROJECT_STRUCTURE.md`
**Proje yapısı** (bu dosya)
- Dosya organizasyonu
- Dizin açıklamaları
- Geliştirici notları

### GitHub Entegrasyonu

#### `.github/workflows/ci.yml`
**GitHub Actions CI/CD**
- Otomatik test
- Syntax kontrolü
- Linting
- Multi-version Python test

#### `.gitignore`
**Git ignore kuralları**
- Python cache
- Virtual environment
- Minecraft data
- Config dosyaları
- Log dosyaları

## 🗂️ Runtime Dizinleri

Launcher çalıştırıldığında oluşturulan dizinler:

```
~/.berke_minecraft_launcher/
├── versions/              # İndirilen Minecraft sürümleri
│   └── 1.20.1/
│       ├── 1.20.1.jar
│       └── 1.20.1.json
├── libraries/             # Minecraft kütüphaneleri (cache)
├── skins/                 # Skin dosyaları
├── cache/                 # Genel cache
├── logs/                  # Launcher ve Minecraft logları
│   ├── minecraft_1.20.1_20251004_230145.log
│   └── minecraft_1.19.4_20251004_230230.log
└── config.json            # Launcher ayarları

~/.minecraft/
├── mods/                  # Yüklü modlar
├── saves/                 # Dünyalar
├── resourcepacks/         # Kaynak paketleri
└── screenshots/           # Ekran görüntüleri
```

## 📊 Kod İstatistikleri

### Dosya Boyutları
- `berke_minecraft_launcher.py`: ~2700 satır
- `start.sh`: ~136 satır
- `README.md`: ~500 satır
- `CONTRIBUTING.md`: ~300 satır
- Toplam: ~4000+ satır kod ve dokümantasyon

### Özellik Dağılımı
- **Core Launcher**: 40%
- **Mod Sistemi**: 20%
- **UI/UX**: 15%
- **Skin Yönetimi**: 10%
- **Performans Monitörü**: 10%
- **Yardımcı Fonksiyonlar**: 5%

## 🔧 Geliştirme Notları

### Kod Organizasyonu

**MinecraftLauncher Class:**
```python
class MinecraftLauncher:
    # Initialization
    __init__()
    
    # Core Functions
    _find_java()
    _download_version()
    _launch_minecraft()
    
    # UI Functions
    _create_banner()
    _create_main_menu()
    _show_versions_menu()
    
    # Mod Functions
    _show_mod_menu()
    _search_and_download_mod()
    _download_mod_from_modrinth()
    
    # Skin Functions
    _show_skin_menu()
    _download_skin_from_url()
    
    # Settings Functions
    _show_settings_menu()
    _configure_*()
    
    # Utility Functions
    _get_system_info()
    _check_java_version()
    _auto_update_java()
```

### API Entegrasyonları

1. **Mojang API**
   - Version manifest
   - Version details
   - Asset index
   - Library downloads

2. **Modrinth API**
   - Mod search
   - Mod details
   - Version downloads
   - Popular mods

### Bağımlılıklar

**Python Kütüphaneleri:**
- `requests`: HTTP istekleri
- `rich`: Terminal UI
- `click`: CLI framework
- `psutil`: Sistem bilgileri
- `colorama`: Renkli terminal

**Sistem Bağımlılıkları:**
- Python 3.10+
- Java 21+
- Git
- XWayland (Wayland için)

## 🚀 Deployment

### AUR Paketi

1. PKGBUILD hazır
2. Git tag oluştur: `git tag v2.3.0`
3. AUR'a yükle
4. Paket test et

### GitHub Release

1. Tag oluştur
2. Release notes yaz
3. Binary ekle (opsiyonel)
4. Yayınla

## 📝 Bakım

### Güncelleme Süreci

1. Kod değişiklikleri yap
2. `version.py` güncelle
3. `CHANGELOG.md` güncelle
4. Test et
5. Commit ve push
6. Tag oluştur
7. Release yayınla

### Test Checklist

- [ ] Syntax kontrolü
- [ ] Linting
- [ ] Manuel test (tüm özellikler)
- [ ] Farklı Python versiyonları
- [ ] Farklı Minecraft sürümleri
- [ ] Mod indirme
- [ ] Skin yönetimi
- [ ] Performans monitörü

---

**Son Güncelleme**: 4 Ekim 2025
**Sürüm**: 2.3.0
**Geliştirici**: Berke Oruç
