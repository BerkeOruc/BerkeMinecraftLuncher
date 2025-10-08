#!/usr/bin/env python3
"""
Berke Minecraft Launcher - Internationalization (i18n)
Multi-language support system
"""

import json
from pathlib import Path
from typing import Dict, Optional

class I18n:
    """Çoklu dil desteği sınıfı"""
    
    def __init__(self, lang: str = "tr"):
        self.lang = lang
        self.translations: Dict[str, Dict[str, str]] = {
            "tr": self._get_turkish(),
            "en": self._get_english()
        }
    
    def t(self, key: str, **kwargs) -> str:
        """
        Çeviri al
        
        Args:
            key: Çeviri anahtarı (örn: "menu.start")
            **kwargs: Format parametreleri
        
        Returns:
            Çevrilmiş metin
        """
        keys = key.split(".")
        translation = self.translations.get(self.lang, self.translations["en"])
        
        for k in keys:
            if isinstance(translation, dict):
                translation = translation.get(k, key)
            else:
                break
        
        if isinstance(translation, str) and kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError:
                return translation
        
        return translation if isinstance(translation, str) else key
    
    def set_language(self, lang: str):
        """Dil değiştir"""
        if lang in self.translations:
            self.lang = lang
    
    def get_available_languages(self) -> Dict[str, str]:
        """Mevcut dilleri döndür"""
        return {
            "tr": "🇹🇷 Türkçe",
            "en": "🇬🇧 English"
        }
    
    def _get_turkish(self) -> dict:
        """Türkçe çeviriler"""
        return {
            "app": {
                "name": "Berke Minecraft Launcher",
                "version": "v{version}",
                "subtitle": "Terminal Tabanlı & Optimize",
                "developer": "Geliştirici: Berke Oruç (2009)"
            },
            "menu": {
                "main": "Ana Menü",
                "start": "Minecraft Başlat",
                "download": "Sürüm İndir",
                "versions": "İndirilen Sürümler",
                "skins": "Skin Yönetimi",
                "settings": "Ayarlar",
                "mods": "Mod Yönetimi",
                "performance": "Performans Monitörü",
                "system": "Sistem Bilgileri",
                "about": "Hakkında",
                "exit": "Çıkış",
                "back": "Geri"
            },
            "status": {
                "ready": "Hazır",
                "loading": "Yükleniyor",
                "downloading": "İndiriliyor",
                "installing": "Kuruluyor",
                "running": "Çalışıyor",
                "error": "Hata",
                "success": "Başarılı",
                "online": "Çevrimiçi",
                "offline": "Çevrimdışı"
            },
            "version": {
                "title": "Minecraft Sürümleri",
                "search": "Sürüm Ara",
                "filter": "Filtrele",
                "all": "Tümü",
                "release": "Kararlı",
                "snapshot": "Snapshot",
                "beta": "Beta",
                "alpha": "Alpha",
                "installed": "Kurulu",
                "available": "Mevcut",
                "details": "Detaylar",
                "download": "İndir",
                "delete": "Sil",
                "launch": "Başlat"
            },
            "mod": {
                "title": "Mod Yönetimi",
                "search": "Mod Ara ve İndir",
                "installed": "Yüklü Modlar",
                "popular": "Popüler Modlar",
                "upload": "Yerel Mod Yükle",
                "delete": "Mod Sil",
                "folder": "Mod Klasörünü Aç",
                "searching": "'{query}' aranıyor...",
                "no_results": "Sonuç bulunamadı",
                "select_version": "Minecraft sürümü seçin",
                "enter_name": "Mod adı girin"
            },
            "skin": {
                "title": "Skin Yönetimi",
                "current": "Mevcut Skin",
                "gallery": "Popüler Skinler",
                "upload": "URL'den İndir",
                "local": "Yerel Dosya",
                "backup": "Yedekle",
                "restore": "Geri Yükle",
                "apply": "Uygula"
            },
            "settings": {
                "title": "Ayarlar",
                "general": "Genel Ayarlar",
                "advanced": "Gelişmiş Ayarlar",
                "language": "Dil",
                "username": "Kullanıcı Adı",
                "memory": "Bellek (RAM)",
                "java": "Java Yolu",
                "minecraft_dir": "Minecraft Dizini",
                "graphics": "Grafik Optimizasyonu",
                "fullscreen": "Tam Ekran",
                "debug": "Debug Modu",
                "fast_start": "Hızlı Başlatma",
                "auto_update": "Otomatik Güncelleme",
                "save": "Kaydet",
                "reset": "Sıfırla"
            },
            "performance": {
                "title": "Performans Monitörü",
                "cpu": "CPU Kullanımı",
                "ram": "RAM Kullanımı",
                "disk": "Disk Kullanımı",
                "fps": "Tahmini FPS",
                "processes": "Minecraft Process'leri",
                "optimization": "Optimizasyon Önerileri",
                "good": "İyi",
                "medium": "Orta",
                "high": "Yüksek"
            },
            "system": {
                "title": "Sistem Bilgileri",
                "os": "İşletim Sistemi",
                "kernel": "Kernel",
                "cpu": "İşlemci",
                "ram": "RAM",
                "gpu": "Ekran Kartı",
                "java": "Java Sürümü",
                "python": "Python Sürümü",
                "display": "Ekran Sunucusu"
            },
            "about": {
                "title": "Hakkında",
                "developer": "Geliştirici",
                "birth_year": "Doğum Yılı",
                "age": "Yaş",
                "expertise": "Uzmanlık",
                "project": "Proje",
                "platform": "Platform",
                "license": "Lisans",
                "features": "Özellikler",
                "statistics": "İstatistikler",
                "thanks": "Teşekkürler"
            },
            "messages": {
                "confirm": "Onaylıyor musunuz?",
                "success": "İşlem başarılı!",
                "error": "Bir hata oluştu!",
                "loading": "Lütfen bekleyin...",
                "press_enter": "Devam etmek için Enter'a basın...",
                "select_option": "Seçiminizi yapın",
                "invalid_choice": "Geçersiz seçim!",
                "invalid_input": "Geçersiz giriş!",
                "not_found": "Bulunamadı!",
                "already_exists": "Zaten mevcut!",
                "download_complete": "İndirme tamamlandı!",
                "install_complete": "Kurulum tamamlandı!",
                "delete_confirm": "{name} silinsin mi?",
                "java_not_found": "Java bulunamadı!",
                "java_old_version": "Java {version} çok eski! Java 21+ gerekli.",
                "update_available": "Yeni sürüm mevcut: {version}",
                "no_versions": "Henüz sürüm indirilmemiş!",
                "no_mods": "Henüz mod yüklenmemiş!"
            },
            "errors": {
                "title": "Hata Raporu",
                "java_vm": "Java Virtual Machine oluşturulamadı",
                "java_version": "Java sürümü uyumsuz",
                "network": "İnternet bağlantısı hatası",
                "permission": "İzin hatası",
                "not_found": "Dosya bulunamadı",
                "corrupted": "Dosya bozuk",
                "unknown": "Bilinmeyen hata"
            }
        }
    
    def _get_english(self) -> dict:
        """English translations"""
        return {
            "app": {
                "name": "Berke Minecraft Launcher",
                "version": "v{version}",
                "subtitle": "Terminal-Based & Optimized",
                "developer": "Developer: Berke Oruç (2009)"
            },
            "menu": {
                "main": "Main Menu",
                "start": "Start Minecraft",
                "download": "Download Version",
                "versions": "Installed Versions",
                "skins": "Skin Management",
                "settings": "Settings",
                "mods": "Mod Management",
                "performance": "Performance Monitor",
                "system": "System Information",
                "about": "About",
                "exit": "Exit",
                "back": "Back"
            },
            "status": {
                "ready": "Ready",
                "loading": "Loading",
                "downloading": "Downloading",
                "installing": "Installing",
                "running": "Running",
                "error": "Error",
                "success": "Success",
                "online": "Online",
                "offline": "Offline"
            },
            "version": {
                "title": "Minecraft Versions",
                "search": "Search Version",
                "filter": "Filter",
                "all": "All",
                "release": "Release",
                "snapshot": "Snapshot",
                "beta": "Beta",
                "alpha": "Alpha",
                "installed": "Installed",
                "available": "Available",
                "details": "Details",
                "download": "Download",
                "delete": "Delete",
                "launch": "Launch"
            },
            "mod": {
                "title": "Mod Management",
                "search": "Search and Download Mods",
                "installed": "Installed Mods",
                "popular": "Popular Mods",
                "upload": "Upload Local Mod",
                "delete": "Delete Mod",
                "folder": "Open Mods Folder",
                "searching": "Searching for '{query}'...",
                "no_results": "No results found",
                "select_version": "Select Minecraft version",
                "enter_name": "Enter mod name"
            },
            "skin": {
                "title": "Skin Management",
                "current": "Current Skin",
                "gallery": "Popular Skins",
                "upload": "Download from URL",
                "local": "Local File",
                "backup": "Backup",
                "restore": "Restore",
                "apply": "Apply"
            },
            "settings": {
                "title": "Settings",
                "general": "General Settings",
                "advanced": "Advanced Settings",
                "language": "Language",
                "username": "Username",
                "memory": "Memory (RAM)",
                "java": "Java Path",
                "minecraft_dir": "Minecraft Directory",
                "graphics": "Graphics Optimization",
                "fullscreen": "Fullscreen",
                "debug": "Debug Mode",
                "fast_start": "Fast Start",
                "auto_update": "Auto Update",
                "save": "Save",
                "reset": "Reset"
            },
            "performance": {
                "title": "Performance Monitor",
                "cpu": "CPU Usage",
                "ram": "RAM Usage",
                "disk": "Disk Usage",
                "fps": "Estimated FPS",
                "processes": "Minecraft Processes",
                "optimization": "Optimization Tips",
                "good": "Good",
                "medium": "Medium",
                "high": "High"
            },
            "system": {
                "title": "System Information",
                "os": "Operating System",
                "kernel": "Kernel",
                "cpu": "Processor",
                "ram": "RAM",
                "gpu": "Graphics Card",
                "java": "Java Version",
                "python": "Python Version",
                "display": "Display Server"
            },
            "about": {
                "title": "About",
                "developer": "Developer",
                "birth_year": "Birth Year",
                "age": "Age",
                "expertise": "Expertise",
                "project": "Project",
                "platform": "Platform",
                "license": "License",
                "features": "Features",
                "statistics": "Statistics",
                "thanks": "Thanks"
            },
            "messages": {
                "confirm": "Are you sure?",
                "success": "Operation successful!",
                "error": "An error occurred!",
                "loading": "Please wait...",
                "press_enter": "Press Enter to continue...",
                "select_option": "Select your choice",
                "invalid_choice": "Invalid choice!",
                "invalid_input": "Invalid input!",
                "not_found": "Not found!",
                "already_exists": "Already exists!",
                "download_complete": "Download complete!",
                "install_complete": "Installation complete!",
                "delete_confirm": "Delete {name}?",
                "java_not_found": "Java not found!",
                "java_old_version": "Java {version} is too old! Java 21+ required.",
                "update_available": "New version available: {version}",
                "no_versions": "No versions downloaded yet!",
                "no_mods": "No mods installed yet!"
            },
            "errors": {
                "title": "Error Report",
                "java_vm": "Could not create Java Virtual Machine",
                "java_version": "Java version incompatible",
                "network": "Internet connection error",
                "permission": "Permission error",
                "not_found": "File not found",
                "corrupted": "File corrupted",
                "unknown": "Unknown error"
            }
        }

# Global instance
_i18n = I18n()

def t(key: str, **kwargs) -> str:
    """Global çeviri fonksiyonu"""
    return _i18n.t(key, **kwargs)

def set_language(lang: str):
    """Global dil değiştirme"""
    _i18n.set_language(lang)

def get_available_languages() -> Dict[str, str]:
    """Mevcut dilleri al"""
    return _i18n.get_available_languages()

def get_current_language() -> str:
    """Mevcut dili al"""
    return _i18n.lang

if __name__ == "__main__":
    # Test
    print("Turkish:")
    set_language("tr")
    print(t("app.name"))
    print(t("menu.start"))
    print(t("messages.delete_confirm", name="Test"))
    
    print("\nEnglish:")
    set_language("en")
    print(t("app.name"))
    print(t("menu.start"))
    print(t("messages.delete_confirm", name="Test"))
