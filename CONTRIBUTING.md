# 🤝 Katkıda Bulunma Rehberi

Berke Minecraft Launcher'a katkıda bulunmak istediğiniz için teşekkürler! Bu belge, projeye nasıl katkıda bulunabileceğinizi açıklar.

## 📋 İçindekiler

- [Davranış Kuralları](#davranış-kuralları)
- [Nasıl Katkıda Bulunabilirim?](#nasıl-katkıda-bulunabilirim)
- [Geliştirme Ortamı](#geliştirme-ortamı)
- [Kod Standartları](#kod-standartları)
- [Commit Mesajları](#commit-mesajları)
- [Pull Request Süreci](#pull-request-süreci)

---

## 📜 Davranış Kuralları

Bu proje ve topluluğu, herkes için açık ve misafirperver bir ortam sağlamayı taahhüt eder. Lütfen:

- ✅ Saygılı ve yapıcı olun
- ✅ Farklı bakış açılarını kabul edin
- ✅ Yapıcı eleştiri kabul edin
- ✅ Topluluk odaklı düşünün
- ❌ Taciz edici dil veya davranışlardan kaçının
- ❌ Kişisel saldırılardan kaçının

---

## 🚀 Nasıl Katkıda Bulunabilirim?

### 🐛 Hata Bildirimi

Bir hata buldunuz mu? Lütfen bir issue açın:

1. [Issues](https://github.com/berke0/BerkeMinecraftLuncher/issues) sayfasına gidin
2. "New Issue" butonuna tıklayın
3. Şu bilgileri ekleyin:
   - **Hata Açıklaması**: Ne oldu?
   - **Beklenen Davranış**: Ne olmalıydı?
   - **Adımlar**: Hatayı nasıl tekrarlayabiliriz?
   - **Sistem Bilgileri**: OS, Python versiyonu, Java versiyonu
   - **Ekran Görüntüleri**: Varsa ekleyin
   - **Log Dosyaları**: `~/.berke_minecraft_launcher/logs/` dizininden

### 💡 Özellik Önerisi

Yeni bir özellik mi istiyorsunuz?

1. Önce [Issues](https://github.com/berke0/BerkeMinecraftLuncher/issues) sayfasında arayın
2. Yoksa yeni bir issue açın
3. Şunları ekleyin:
   - **Özellik Açıklaması**: Ne istiyorsunuz?
   - **Motivasyon**: Neden gerekli?
   - **Alternatifler**: Başka çözümler düşündünüz mü?
   - **Ek Bilgiler**: Mockup, örnek kod, vb.

### 🔧 Kod Katkısı

Kod katkısı yapmak istiyorsanız:

1. Repository'yi fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi yapın
4. Test edin
5. Pull Request açın

---

## 💻 Geliştirme Ortamı

### Gereksinimler

- Python 3.10+
- Git
- Java 21+
- Arch Linux (önerilir)

### Kurulum

```bash
# Repository'yi fork edin ve klonlayın
git clone https://github.com/KULLANICI_ADINIZ/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher

# Virtual environment oluşturun
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirme modunda çalıştırın
python3 berke_minecraft_launcher.py
```

### Test Etme

```bash
# Launcher'ı test edin
./start.sh

# Belirli bir özelliği test edin
# (Örnek: Mod sistemi)
# Menü 6 → Seçenek 1

# Log dosyalarını kontrol edin
tail -f ~/.berke_minecraft_launcher/logs/minecraft_*.log
```

---

## 📝 Kod Standartları

### Python Stil Rehberi

- **PEP 8** standartlarını takip edin
- **Type hints** kullanın
- **Docstrings** ekleyin (Google style)
- **Anlamlı değişken isimleri** kullanın

**Örnek:**

```python
def _download_mod_from_modrinth(self, mod_data: dict, mc_version: str) -> bool:
    """
    Modrinth'ten mod indir.
    
    Args:
        mod_data: Mod bilgileri (Modrinth API'den)
        mc_version: Minecraft sürümü (örn: "1.20.1")
    
    Returns:
        bool: İndirme başarılı ise True
    
    Raises:
        RequestException: API hatası durumunda
    """
    # Kod...
```

### Kod Organizasyonu

```
berke_minecraft_launcher.py
├── Imports
├── MinecraftLauncher class
│   ├── __init__
│   ├── Private methods (_method_name)
│   └── Public methods (method_name)
└── main()
```

### Commit Mesajları

Commit mesajları şu formatı takip etmelidir:

```
<tip>: <kısa açıklama>

<detaylı açıklama (opsiyonel)>

<footer (opsiyonel)>
```

**Tipler:**
- `feat`: Yeni özellik
- `fix`: Hata düzeltme
- `docs`: Dokümantasyon
- `style`: Kod formatı (işlevsellik değişmez)
- `refactor`: Kod yeniden yapılandırma
- `perf`: Performans iyileştirme
- `test`: Test ekleme/düzeltme
- `chore`: Bakım işleri

**Örnekler:**

```bash
feat: Add Modrinth API integration for mod downloading

- Implement mod search functionality
- Add mod download with progress bar
- Support Minecraft version filtering

Closes #42
```

```bash
fix: Resolve Java version detection issue on Arch Linux

The launcher was not detecting Java 25 correctly.
Updated _find_java() to include new Java paths.

Fixes #38
```

---

## 🔄 Pull Request Süreci

### 1. Branch Oluşturma

```bash
# Feature branch
git checkout -b feature/amazing-feature

# Bugfix branch
git checkout -b fix/bug-description

# Documentation branch
git checkout -b docs/update-readme
```

### 2. Değişiklikleri Yapma

```bash
# Değişikliklerinizi yapın
# Test edin
# Commit yapın

git add .
git commit -m "feat: Add amazing feature"
```

### 3. Push ve PR

```bash
# Fork'unuza push edin
git push origin feature/amazing-feature

# GitHub'da Pull Request açın
```

### 4. PR Şablonu

Pull Request açarken şunları ekleyin:

```markdown
## Açıklama
Bu PR'ın amacını kısaca açıklayın.

## Değişiklikler
- [ ] Değişiklik 1
- [ ] Değişiklik 2
- [ ] Değişiklik 3

## Test Edildi mi?
- [ ] Evet, şu şekilde test ettim: ...
- [ ] Hayır, çünkü: ...

## Ekran Görüntüleri
(Varsa ekleyin)

## İlgili Issue'lar
Closes #123
Fixes #456
```

### 5. Code Review

- Maintainer'lar kodunuzu inceleyecek
- Geri bildirim gelirse düzeltme yapın
- Onaylandıktan sonra merge edilecek

---

## 🎯 Öncelikli Alanlar

Şu alanlarda katkı özellikle değerlidir:

### Yüksek Öncelik
- 🐛 Hata düzeltmeleri
- 📝 Dokümantasyon iyileştirmeleri
- 🌐 Çeviri (İngilizce, Türkçe)
- 🎨 UI/UX iyileştirmeleri

### Orta Öncelik
- ⚡ Performans optimizasyonları
- 🔧 Yeni mod platformları (CurseForge)
- 📊 Daha detaylı istatistikler
- 🎮 Forge/Fabric otomatik kurulum

### Düşük Öncelik
- 🎨 Tema sistemi
- 🔌 Plugin sistemi
- 🌍 Dil desteği genişletme

---

## 📞 İletişim

Sorularınız mı var?

- **GitHub Issues**: Teknik sorular için
- **GitHub Discussions**: Genel tartışmalar için
- **Pull Requests**: Kod incelemeleri için

---

## 🙏 Teşekkürler!

Katkılarınız için teşekkür ederiz! Her katkı, projeyi daha iyi hale getirir.

**Mutlu kodlamalar!** 🎮✨
