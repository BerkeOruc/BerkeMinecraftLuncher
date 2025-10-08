# 🎮 Berke Minecraft Launcher - Kurulum Rehberi

## 📦 Arch Linux Kurulumu (AUR)

### Otomatik Kurulum
```bash
yay -S berkemc
```

### İlk Çalıştırma
```bash
berkemc
```

Launcher ilk kez başlatıldığında **Kurulum Sihirbazı** otomatik açılacak:

1. **Java Kontrolü** ✓
   - Java otomatik tespit edilir
   - Yoksa Java 21 otomatik kurulur

2. **Kullanıcı Adı** ✓
   - Minecraft kullanıcı adınızı girin

3. **RAM Ayarı** ✓
   - Otomatik önerilir veya manuel seçin

4. **Desktop Entry** ✓
   - Uygulama menüsüne eklenir

5. **İlk Sürüm** ✓
   - İsterseniz ilk Minecraft sürümünü indirir

## 🗑️ Kaldırma

```bash
berkemc --uninstall
```

Veya:
```bash
yay -R berkemc
```

## 🔧 Manuel Kurulum

```bash
git clone https://github.com/berke0/BerkeMinecraftLuncher.git
cd BerkeMinecraftLuncher
pip install -r requirements.txt
python berke_minecraft_launcher.py
```

## ✨ Özellikler

- ✅ Otomatik Java yönetimi
- ✅ Hyprland/Wayland desteği
- ✅ Forge/Fabric kurulumu
- ✅ Mod arama ve kurulum
- ✅ Skin yönetimi
- ✅ Performans izleme
- ✅ Otomatik güncelleme
- ✅ Desktop entegrasyon

---
**Geliştirici:** Berke Oruç (2009)

