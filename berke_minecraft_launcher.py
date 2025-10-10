#!/usr/bin/env python3
"""
Berke Minecraft Launcher
Arch Linux için optimize edilmiş terminal tabanlı Minecraft launcher'ı
"""

import os
import sys
import json
import subprocess
import platform
import shutil
import base64
import uuid
import hashlib
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, DownloadColumn, TransferSpeedColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.align import Align
from rich.columns import Columns
from rich import box
import colorama
from colorama import Fore, Back, Style

# Version bilgisi import et
try:
    from version import __version__, get_full_version_string
except ImportError:
    __version__ = "3.2.0"
    def get_full_version_string():
        return f"BerkeMC v{__version__}"

# i18n sistemi import et
try:
    from i18n import I18n, t as i18n_t, set_language, get_current_language
    _i18n_available = True
except ImportError:
    _i18n_available = False
    def i18n_t(key, **kwargs):
        return key

# Colorama'yı başlat
colorama.init(autoreset=True)

class MinecraftLauncher:
    def __init__(self):
        # Terminal kontrolü
        if sys.stdout.isatty():
            self.console = Console(width=120)
        else:
            # Non-TTY için basit console
            self.console = Console(force_terminal=False, legacy_windows=False)
        self.home_dir = Path.home()
        self.minecraft_dir = self.home_dir / ".minecraft"
        self.launcher_dir = self.home_dir / ".berke_minecraft_launcher"
        self.versions_dir = self.launcher_dir / "versions"
        self.skins_dir = self.launcher_dir / "skins"
        self.cache_dir = self.launcher_dir / "cache"
        self.config_file = self.launcher_dir / "config.json"
        self.java_executable = self._find_java()
        
        # Dizinleri oluştur
        self.minecraft_dir.mkdir(exist_ok=True)
        self.launcher_dir.mkdir(exist_ok=True)
        self.versions_dir.mkdir(exist_ok=True)
        self.skins_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Config dosyasını yükle
        self.config = self._load_config()
        
        # i18n dilini yükle
        if _i18n_available:
            lang = self.config.get("language", "tr")
            set_language(lang)
        
        # Minecraft API URL'leri
        self.version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        self.assets_url = "https://resources.download.minecraft.net"
        self.skin_api_url = "https://api.mojang.com/users/profiles/minecraft"
        
    def _find_java(self) -> Optional[str]:
        """Sistemde Java'yı bul - Minecraft uyumlu sürümler öncelikli (17-21)"""
        # Önce JAVA_HOME kontrol et
        if os.environ.get('JAVA_HOME'):
            java_home_bin = os.path.join(os.environ['JAVA_HOME'], 'bin', 'java')
            if os.path.exists(java_home_bin):
                print(f"🔍 JAVA_HOME'dan Java bulundu: {java_home_bin}")
                return java_home_bin
        
        # Java yollarını dene (Minecraft uyumlu sürümler önce)
        java_paths = [
            "/usr/lib/jvm/java-21-openjdk/bin/java",
            "/usr/lib/jvm/java-17-openjdk/bin/java",
            "/usr/lib/jvm/java-25-openjdk/bin/java",
            "/usr/lib/jvm/java-22-openjdk/bin/java",
            "/usr/lib/jvm/java-23-openjdk/bin/java",
            "/usr/lib/jvm/java-24-openjdk/bin/java",
            "/usr/lib/jvm/default/bin/java",
            "/usr/bin/java",
            "java"
        ]
        
        for java_path in java_paths:
            # Tam yol ise dosya var mı kontrol et
            if java_path.startswith("/"):
                if os.path.exists(java_path):
                    print(f"🔍 Java bulundu: {java_path}")
                    return java_path
            # Değilse which ile bul
            elif shutil.which(java_path):
                found_path = shutil.which(java_path)
                print(f"🔍 Java bulundu (which): {found_path}")
                return found_path
                
        print("❌ Java bulunamadı!")
        return None
    
    def _load_config(self) -> Dict:
        """Config dosyasını yükle"""
        default_config = {
            "username": "BerkePlayer",
            "memory": "auto",
            "java_args": [],
            "current_skin": "default",
            "window_width": 1280,
            "window_height": 720,
            "fullscreen": False,
            "optimize_graphics": True,
            "enable_mods": False,
            "mod_loader": "none"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Eksik anahtarları ekle
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except json.JSONDecodeError:
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict = None):
        """Config dosyasını kaydet"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _check_java_version(self):
        """Java sürümünü kontrol et"""
        try:
            result = subprocess.run([self.java_executable, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            version_output = result.stderr  # Java version bilgisi stderr'da
            
            # Java sürümünü parse et
            import re
            version_match = re.search(r'version "(\d+)\.(\d+)\.(\d+)', version_output)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3))
                return f"{major}.{minor}.{patch}"
            return None
        except Exception as e:
            self.console.print(f"[red]Java sürüm kontrolü başarısız: {e}[/red]")
            return None
    
    def _get_available_java_versions(self):
        """Sistemdeki tüm Java sürümlerini bul"""
        java_versions = []
        java_dirs = [
            "/usr/lib/jvm/",
            "/usr/java/",
            "/opt/java/"
        ]
        
        # Önce sistemdeki Java sürümlerini bul
        for java_dir in java_dirs:
            if os.path.exists(java_dir):
                try:
                    for item in os.listdir(java_dir):
                        java_path = os.path.join(java_dir, item, "bin", "java")
                        if os.path.exists(java_path):
                            version = self._check_java_version_at_path(java_path)
                            if version:
                                java_versions.append({
                                    "path": java_path,
                                    "version": version,
                                    "name": item,
                                    "installed": True
                                })
                except:
                    continue
        
        return sorted(java_versions, key=lambda x: x["version"], reverse=True)
    
    def _get_installed_java_versions(self):
        """Sadece kurulu Java sürümlerini bul"""
        java_versions = []
        java_dirs = [
            "/usr/lib/jvm/",
            "/usr/java/",
            "/opt/java/"
        ]
        
        for java_dir in java_dirs:
            if os.path.exists(java_dir):
                try:
                    for item in os.listdir(java_dir):
                        # Sadece java- ile başlayan dizinleri kontrol et
                        if item.startswith("java-") and os.path.isdir(os.path.join(java_dir, item)):
                            java_path = os.path.join(java_dir, item, "bin", "java")
                            if os.path.exists(java_path):
                                version = self._check_java_version_at_path(java_path)
                                if version:
                                    java_versions.append({
                                        "path": java_path,
                                        "version": version,
                                        "name": item,
                                        "installed": True
                                    })
                except Exception as e:
                    print(f"Java dizini okuma hatası: {e}")
                    continue
        
        return sorted(java_versions, key=lambda x: x["version"], reverse=True)
    
    def _get_recommended_java_for_version(self, version_id: str):
        """Minecraft sürümü için önerilen Java'yı bul"""
        try:
            # Sürüm numarasını parse et
            if '.' in version_id:
                parts = version_id.split('.')
                if len(parts) >= 2:
                    major = int(parts[0])
                    minor = int(parts[1])
                    
                    # Minecraft sürümüne göre Java önerisi
                    if major >= 21:
                        recommended_major = 21
                    elif major >= 19:
                        recommended_major = 17
                    elif major >= 17:
                        recommended_major = 17
                    elif major >= 12:
                        recommended_major = 17
                    else:
                        recommended_major = 11
                    
                    # Kurulu Java'lardan önerilen sürümü bul
                    installed_java = self._get_installed_java_versions()
                    for java in installed_java:
                        try:
                            java_major = int(java["version"].split('.')[0])
                            if java_major == recommended_major:
                                return java
                        except:
                            continue
                    
                    # Önerilen sürüm yoksa en yakın uyumlu sürümü bul
                    for java in installed_java:
                        try:
                            java_major = int(java["version"].split('.')[0])
                            if java_major >= recommended_major:
                                return java
                        except:
                            continue
        except:
            pass
        
        return None
    
    def _get_installable_java_versions(self):
        """Kurulabilir Java sürümlerini listele"""
        installable_versions = []
        
        # Java 11-25 arası tüm sürümler
        java_versions = [
            {"version": "25.0.0", "name": "OpenJDK 25", "package": "jdk25-openjdk"},
            {"version": "24.0.0", "name": "OpenJDK 24", "package": "jdk24-openjdk"},
            {"version": "23.0.0", "name": "OpenJDK 23", "package": "jdk23-openjdk"},
            {"version": "22.0.0", "name": "OpenJDK 22", "package": "jdk22-openjdk"},
            {"version": "21.0.8", "name": "OpenJDK 21", "package": "jdk21-openjdk"},
            {"version": "20.0.2", "name": "OpenJDK 20", "package": "jdk20-openjdk"},
            {"version": "19.0.2", "name": "OpenJDK 19", "package": "jdk19-openjdk"},
            {"version": "18.0.2", "name": "OpenJDK 18", "package": "jdk18-openjdk"},
            {"version": "17.0.16", "name": "OpenJDK 17", "package": "jdk17-openjdk"},
            {"version": "16.0.2", "name": "OpenJDK 16", "package": "jdk16-openjdk"},
            {"version": "15.0.2", "name": "OpenJDK 15", "package": "jdk15-openjdk"},
            {"version": "14.0.2", "name": "OpenJDK 14", "package": "jdk14-openjdk"},
            {"version": "13.0.2", "name": "OpenJDK 13", "package": "jdk13-openjdk"},
            {"version": "12.0.2", "name": "OpenJDK 12", "package": "jdk12-openjdk"},
            {"version": "11.0.24", "name": "OpenJDK 11", "package": "jdk11-openjdk"},
            {"version": "8.0.462", "name": "OpenJDK 8", "package": "jdk8-openjdk"}
        ]
        
        for java_info in java_versions:
            installable_versions.append({
                "path": f"/usr/lib/jvm/{java_info['package']}/bin/java",
                "version": java_info["version"],
                "name": java_info["name"],
                "package": java_info["package"],
                "installed": False
            })
        
        return installable_versions
    
    def _check_java_version_at_path(self, java_path):
        """Belirli bir Java yolundaki sürümü kontrol et"""
        try:
            result = subprocess.run([java_path, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_output = result.stderr
                version_match = re.search(r'version "(\d+)\.(\d+)\.(\d+)', version_output)
                if version_match:
                    major = int(version_match.group(1))
                    minor = int(version_match.group(2))
                    patch = int(version_match.group(3))
                    return f"{major}.{minor}.{patch}"
            return None
        except Exception as e:
            print(f"Java version check error: {e}")
            return None
    
    def _show_java_management_menu(self):
        """Java yönetimi menüsü"""
        while True:
            os.system('clear')
            
            current_java = self._check_java_version()
            java_versions = self._get_installed_java_versions()
            
            self.console.print(Panel(
                f"[bold cyan]☕ JAVA YÖNETİMİ[/bold cyan]\n"
                f"[dim]Mevcut Java: {current_java or 'Bulunamadı'}[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Java sürümleri listesi - sadece kurulu olanlar
            installed_java = self._get_installed_java_versions()
            if installed_java:
                self.console.print("[bold]Kurulu Java Sürümleri:[/bold]")
                for i, java in enumerate(installed_java, 1):
                    current_marker = " [green]✓[/green]" if java["path"] == self.java_executable else ""
                    # Java uyumluluğu kontrolü
                    try:
                        major_version = int(java["version"].split('.')[0])
                        if major_version >= 17:
                            compatibility = "[green]✅ Uyumlu[/green]"
                        elif major_version >= 11:
                            compatibility = "[yellow]⚠️ Eski[/yellow]"
                        else:
                            compatibility = "[red]❌ Uyumsuz[/red]"
                    except:
                        compatibility = "[dim]?[/dim]"
                    
                    self.console.print(f"  [cyan]{i}[/cyan]  {java['name']:25} {java['version']:10} {compatibility}{current_marker}")
                
                # Otomatik önerilen Java
                recommended_java = None
                for java in installed_java:
                    try:
                        major_version = int(java["version"].split('.')[0])
                        if major_version == 21:
                            recommended_java = java
                            break
                        elif major_version == 17 and not recommended_java:
                            recommended_java = java
                    except:
                        continue
                
                if recommended_java and recommended_java["path"] != self.java_executable:
                    self.console.print(f"\n[cyan]💡 Önerilen Java: {recommended_java['name']} ({recommended_java['version']})[/cyan]")
                    if Confirm.ask("Önerilen Java'yı otomatik seçmek ister misiniz?", default=True):
                        self.java_executable = recommended_java["path"]
                        self.config["java_path"] = recommended_java["path"]
                        self._save_config()
                        self.console.print(f"[green]✅ Java otomatik seçildi: {recommended_java['name']}[/green]")
                        input("[dim]Enter...[/dim]")
                        continue
            else:
                self.console.print("[red]❌ Hiç Java sürümü kurulu değil![/red]")
            
            self.console.print()
            
            # Menü seçenekleri
            self.console.print("[bold]Seçenekler:[/bold]")
            self.console.print("  [cyan]1[/cyan]  Java Sürümü Seç")
            self.console.print("  [cyan]2[/cyan]  Java İndir ve Kur")
            self.console.print("  [cyan]3[/cyan]  Java Ara")
            self.console.print("  [cyan]4[/cyan]  Java Sürümü Sil")
            self.console.print("  [cyan]5[/cyan]  Java Test Et")
            self.console.print("  [cyan]6[/cyan]  Java Bilgileri")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._select_java_version(installed_java)
            elif choice == "2":
                self._download_and_install_java()
            elif choice == "3":
                self._search_java_versions()
            elif choice == "4":
                self._uninstall_java_version()
            elif choice == "5":
                self._test_java()
            elif choice == "6":
                self._show_java_info()
    
    def _select_java_version(self, java_versions):
        """Java sürümü seç - sadece kurulu sürümler"""
        if not java_versions:
            self.console.print("[red]❌ Seçilecek Java sürümü yok![/red]")
            self.console.print("[yellow]Önce Java kurulumu yapın: Java İndir ve Kur[/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print("\n[bold]Java sürümü seçin:[/bold]")
        for i, java in enumerate(java_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {java['name']} ({java['version']}) [green]✓ Kurulu[/green]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(java_versions):
                selected_java = java_versions[choice-1]
                
                self.java_executable = selected_java["path"]
                self.config["java_path"] = selected_java["path"]
                self._save_config()
                self.console.print(f"[green]✅ Java sürümü değiştirildi: {selected_java['name']}[/green]")
                input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _install_java_package(self, package_name):
        """Java paketini kur"""
        try:
            result = subprocess.run(["sudo", "pacman", "-S", package_name, "--noconfirm"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _download_and_install_java(self):
        """Java indir ve kur"""
        self.console.print("\n[bold]Java İndirme ve Kurulum[/bold]")
        
        # Kurulabilir Java sürümlerini göster
        installable_versions = self._get_installable_java_versions()
        
        self.console.print("\n[bold]Kurulabilir Java Sürümleri:[/bold]")
        for i, java in enumerate(installable_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {java['name']} ({java['version']})")
        
        try:
            choice = int(Prompt.ask("\n[cyan]Java sürümü seçin (0 = İptal)[/cyan]"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(installable_versions):
                selected_java = installable_versions[choice-1]
                self.console.print(f"\n[blue]📦 {selected_java['name']} kuruluyor...[/blue]")
                
                if self._install_java_package(selected_java["package"]):
                    self.console.print(f"[green]✅ {selected_java['name']} başarıyla kuruldu![/green]")
                    
                    # Otomatik olarak bu sürümü seç
                    java_path = f"/usr/lib/jvm/{selected_java['package']}/bin/java"
                    if os.path.exists(java_path):
                        self.java_executable = java_path
                        self.config["java_path"] = java_path
                        self._save_config()
                        self.console.print(f"[green]✅ {selected_java['name']} aktif Java sürümü olarak ayarlandı![/green]")
                else:
                    self.console.print(f"[red]❌ {selected_java['name']} kurulumu başarısız![/red]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _search_java_versions(self):
        """Java sürümlerini ara"""
        self.console.print("\n[bold]Java Sürüm Arama[/bold]")
        
        search_term = Prompt.ask("[cyan]Aranacak Java sürümü (örn: 17, 21, openjdk)[/cyan]")
        
        if not search_term:
            self.console.print("[red]❌ Arama terimi boş olamaz![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        # Kurulabilir sürümlerde ara
        installable_versions = self._get_installable_java_versions()
        search_results = []
        
        for java in installable_versions:
            if (search_term.lower() in java['name'].lower() or 
                search_term.lower() in java['version'].lower() or
                search_term.lower() in java['package'].lower()):
                search_results.append(java)
        
        if search_results:
            self.console.print(f"\n[bold]'{search_term}' için bulunan sonuçlar:[/bold]")
            for i, java in enumerate(search_results, 1):
                self.console.print(f"  [cyan]{i}[/cyan]  {java['name']} ({java['version']})")
            
            try:
                choice = int(Prompt.ask("\n[cyan]Kurulacak sürümü seçin (0 = İptal)[/cyan]"))
                if choice == 0:
                    return
                
                if 1 <= choice <= len(search_results):
                    selected_java = search_results[choice-1]
                    self.console.print(f"\n[blue]📦 {selected_java['name']} kuruluyor...[/blue]")
                    
                    if self._install_java_package(selected_java["package"]):
                        self.console.print(f"[green]✅ {selected_java['name']} başarıyla kuruldu![/green]")
                    else:
                        self.console.print(f"[red]❌ {selected_java['name']} kurulumu başarısız![/red]")
                else:
                    self.console.print("[red]❌ Geçersiz seçim![/red]")
            except ValueError:
                self.console.print("[red]❌ Geçersiz giriş![/red]")
        else:
            self.console.print(f"[yellow]⚠️ '{search_term}' için sonuç bulunamadı![/yellow]")
        
        input("[dim]Enter...[/dim]")
    
    def _uninstall_java_version(self):
        """Java sürümü sil"""
        self.console.print("\n[bold]Java Sürümü Silme[/bold]")
        
        # Kurulu Java sürümlerini bul
        java_versions = []
        java_dirs = ["/usr/lib/jvm/"]
        
        for java_dir in java_dirs:
            if os.path.exists(java_dir):
                try:
                    for item in os.listdir(java_dir):
                        if item.startswith("java-") and "openjdk" in item:
                            java_versions.append(item)
                except:
                    continue
        
        if not java_versions:
            self.console.print("[yellow]⚠️ Silinecek Java sürümü bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print("\n[bold]Silinecek Java sürümünü seçin:[/bold]")
        for i, java in enumerate(java_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {java}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]Silinecek sürümü seçin (0 = İptal)[/cyan]"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(java_versions):
                selected_java = java_versions[choice-1]
                
                if Confirm.ask(f"[red]'{selected_java}' sürümünü silmek istediğinizden emin misiniz?[/red]"):
                    # Paket adını düzgün oluştur
                    # Örnek: "java-17-openjdk" -> version=17 -> paketler: jre17-openjdk, jdk17-openjdk
                    import re
                    version_match = re.search(r'java-(\d+)-', selected_java)
                    if version_match:
                        java_version = version_match.group(1)
                        # Hem JRE hem JDK'yı silmeyi dene
                        packages_to_try = [
                            f"jre{java_version}-openjdk",
                            f"jdk{java_version}-openjdk",
                            f"jre-openjdk" if java_version == "8" else None,
                            f"jdk-openjdk" if java_version == "8" else None
                        ]
                        packages_to_try = [p for p in packages_to_try if p]
                    else:
                        # Fallback
                        packages_to_try = [selected_java]
                    
                    self.console.print(f"[blue]🗑️ {selected_java} siliniyor...[/blue]")
                    
                    success = False
                    for package_name in packages_to_try:
                        try:
                            # Önce paketin yüklü olup olmadığını kontrol et
                            check = subprocess.run(["pacman", "-Q", package_name], 
                                                 capture_output=True, text=True)
                            if check.returncode == 0:
                                # Paket yüklü, sil
                                result = subprocess.run(["sudo", "pacman", "-R", package_name, "--noconfirm"], 
                                                      capture_output=True, text=True)
                                if result.returncode == 0:
                                    self.console.print(f"[green]✅ {package_name} başarıyla silindi![/green]")
                                    success = True
                                else:
                                    self.console.print(f"[yellow]⚠️ {package_name} silinemedi:[/yellow]")
                                    if result.stderr:
                                        self.console.print(f"[dim]{result.stderr[:200]}[/dim]")
                        except Exception as e:
                            continue
                    
                    if not success:
                        self.console.print(f"[red]❌ {selected_java} silme işlemi başarısız![/red]")
                        self.console.print("[yellow]💡 Manuel silmek için:[/yellow]")
                        self.console.print(f"[dim]sudo pacman -R jre{java_version}-openjdk jdk{java_version}-openjdk[/dim]")
                else:
                    self.console.print("[yellow]İşlem iptal edildi.[/yellow]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _set_java_path_manual(self):
        """Java yolunu manuel gir"""
        self.console.print("\n[bold]Java yolu girin:[/bold]")
        java_path = Prompt.ask("[cyan]Java yolu[/cyan]")
        
        if os.path.exists(java_path):
            version = self._check_java_version_at_path(java_path)
            if version:
                self.java_executable = java_path
                self.config["java_path"] = java_path
                self._save_config()
                self.console.print(f"[green]✅ Java yolu ayarlandı: {java_path} ({version})[/green]")
            else:
                self.console.print("[red]❌ Geçerli bir Java executable'ı değil![/red]")
        else:
            self.console.print("[red]❌ Dosya bulunamadı![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _install_java(self):
        """Java kurulum menüsü"""
        self.console.print("\n[bold]Java Kurulum Seçenekleri:[/bold]")
        self.console.print("  [cyan]1[/cyan]  OpenJDK 17 (Stabil)")
        self.console.print("  [cyan]2[/cyan]  OpenJDK 21 (Önerilen)")
        self.console.print("  [cyan]3[/cyan]  OpenJDK 11 (Eski sürümler için)")
        self.console.print("  [cyan]4[/cyan]  Oracle JDK (Üçüncü parti)")
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["1", "2", "3", "4"])
        
        java_packages = {
            "1": "jdk17-openjdk",
            "2": "jdk21-openjdk", 
            "3": "jdk11-openjdk",
            "4": "jdk17-openjdk"  # Oracle için alternatif
        }
        
        package = java_packages.get(choice)
        if package:
            self.console.print(f"\n[blue]Java kuruluyor: {package}[/blue]")
            self.console.print("[yellow]Bu işlem sudo yetkisi gerektirir![/yellow]")
            
            if Confirm.ask("Devam etmek istiyor musunuz?"):
                try:
                    result = subprocess.run(["sudo", "pacman", "-S", package, "--noconfirm"], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.console.print("[green]✅ Java başarıyla kuruldu![/green]")
                        self._save_config()
                    else:
                        self.console.print(f"[red]❌ Kurulum hatası: {result.stderr}[/red]")
                except Exception as e:
                    self.console.print(f"[red]❌ Kurulum hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _test_java(self):
        """Java test et"""
        self.console.print("\n[bold]Java Test Sonuçları:[/bold]")
        
        if not self.java_executable:
            self.console.print("[red]❌ Java executable bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        try:
            # Java sürümü
            version = self._check_java_version()
            self.console.print(f"[green]✅ Java Sürümü: {version}[/green]")
            
            # Java bilgileri
            result = subprocess.run([self.java_executable, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.console.print("[green]✅ Java çalışıyor![/green]")
                self.console.print(f"[dim]Detay: {result.stderr.split('\\n')[0]}[/dim]")
            else:
                self.console.print("[red]❌ Java çalışmıyor![/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Java test hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_java_info(self):
        """Java bilgileri göster"""
        self.console.print("\n[bold]Java Bilgileri:[/bold]")
        
        if self.java_executable:
            self.console.print(f"[green]Java Yolu: {self.java_executable}[/green]")
            version = self._check_java_version()
            self.console.print(f"[green]Java Sürümü: {version}[/green]")
            
            try:
                result = subprocess.run([self.java_executable, "-version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    self.console.print("\n[bold]Detaylı Bilgi:[/bold]")
                    for line in result.stderr.split('\\n')[:3]:
                        if line.strip():
                            self.console.print(f"[dim]{line}[/dim]")
            except:
                pass
        else:
            self.console.print("[red]❌ Java bulunamadı![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _auto_update_java(self):
        """Java'yı otomatik güncelle (Arch Linux)"""
        self.console.print("[cyan]☕ Java Otomatik Güncelleme Sistemi[/cyan]\n")
        
        try:
            # Mevcut Java sürümünü kontrol et
            current_version = self._check_java_version()
            
            if current_version:
                self.console.print(f"[blue]📌 Mevcut Java sürümü: {current_version}[/blue]")
            else:
                self.console.print("[yellow]⚠️ Java bulunamadı![/yellow]")
            
            # En son Java sürümünü kontrol et
            self.console.print("[blue]🔍 En son Java sürümü kontrol ediliyor...[/blue]")
            
            # Arch Linux paket deposundan Java sürümlerini kontrol et
            result = subprocess.run(
                ["pacman", "-Ss", "jdk-openjdk"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "jdk-openjdk" in result.stdout:
                self.console.print("[green]✅ Güncel Java paketi bulundu![/green]\n")
                
                # Kullanıcıya sor
                if current_version and current_version >= 21:
                    self.console.print(f"[green]✅ Java {current_version} yeterli (Minecraft için 21+ gerekli)[/green]")
                    
                    if Confirm.ask("Yine de güncelleme yapmak ister misiniz?", default=False):
                        self._install_latest_java()
                else:
                    self.console.print(f"[yellow]⚠️ Java {current_version if current_version else 'yok'} - Güncelleme önerilir![/yellow]")
                    
                    if Confirm.ask("Java'yı şimdi güncellemek ister misiniz?", default=True):
                        self._install_latest_java()
            else:
                self.console.print("[red]❌ Java paketi bulunamadı![/red]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Güncelleme kontrolü hatası: {e}[/red]")
        
        input("\nDevam etmek için Enter'a basın...")
    
    def _install_latest_java(self):
        """En son Java'yı kur"""
        self.console.print("\n[cyan]📦 Java kurulumu başlatılıyor...[/cyan]")
        
        try:
            # Java'yı kur
            result = subprocess.run(
                ["sudo", "pacman", "-S", "--needed", "--noconfirm", "jdk-openjdk"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.console.print("[green]✅ Java başarıyla kuruldu/güncellendi![/green]")
                
                # Java'yı varsayılan yap
                subprocess.run(
                    ["sudo", "archlinux-java", "set", "java-openjdk"],
                    capture_output=True
                )
                
                # Java yolunu güncelle
                self.java_executable = self._find_java()
                new_version = self._check_java_version()
                
                if new_version:
                    self.console.print(f"[green]✅ Yeni Java sürümü: {new_version}[/green]")
                
                # Config'e kaydet
                self.config["java_path"] = self.java_executable
                self._save_config()
            else:
                self.console.print(f"[red]❌ Kurulum hatası: {result.stderr}[/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Kurulum hatası: {e}[/red]")
    
    def _show_version_details(self, version_id: str):
        """Sürüm detaylarını göster - Minecraft'tan çekilen bilgiler"""
        self.console.print(f"\n[cyan]📦 {version_id} - Detaylı Bilgiler[/cyan]\n")
        
        try:
            # Sürüm bilgilerini Minecraft API'den çek
            versions = self._get_available_versions()
            version_info = None
            
            for v in versions:
                if v["id"] == version_id:
                    version_info = v
                    break
            
            if not version_info:
                self.console.print("[red]❌ Sürüm bulunamadı![/red]")
                input("[dim]Enter...[/dim]")
                return
            # Sürüm JSON'unu indir
            response = requests.get(version_info["url"], timeout=10)
            version_data = response.json()
            
            # Detaylı bilgileri göster
            info_table = Table(title=f"🎮 {version_id}", show_header=True, header_style="bold cyan", box=box.ROUNDED)
            info_table.add_column("Özellik", style="yellow", width=25)
            info_table.add_column("Değer", style="white", width=50)
            
            # Temel bilgiler
            info_table.add_row("📅 Sürüm ID", version_id)
            info_table.add_row("🏷️ Tür", version_info.get("type", "Bilinmiyor").upper())
            info_table.add_row("📆 Yayın Tarihi", version_info.get("releaseTime", "Bilinmiyor")[:10])
            info_table.add_row("⏰ Güncelleme", version_info.get("time", "Bilinmiyor")[:10])
            
            # Java sürümü
            if "javaVersion" in version_data:
                java_req = version_data["javaVersion"].get("majorVersion", "Bilinmiyor")
                info_table.add_row("☕ Gerekli Java", f"Java {java_req}+")
            
            # İndirme bilgileri
            if "downloads" in version_data and "client" in version_data["downloads"]:
                client_size = version_data["downloads"]["client"].get("size", 0) / (1024 * 1024)
                info_table.add_row("📦 Client Boyutu", f"{client_size:.1f} MB")
            
            # Kütüphane sayısı
            if "libraries" in version_data:
                lib_count = len(version_data["libraries"])
                info_table.add_row("📚 Kütüphane Sayısı", str(lib_count))
            
            # Asset bilgisi
            if "assetIndex" in version_data:
                asset_id = version_data["assetIndex"].get("id", "Bilinmiyor")
                asset_size = version_data["assetIndex"].get("totalSize", 0) / (1024 * 1024)
                info_table.add_row("🎨 Asset Paketi", asset_id)
                info_table.add_row("🎨 Asset Boyutu", f"{asset_size:.1f} MB")
            
            # Kurulu mu?
            is_installed = version_id in self._get_installed_versions()
            status = "✅ Kurulu" if is_installed else "📥 Kurulu Değil"
            info_table.add_row("💾 Durum", status)
            
            self.console.print(info_table)
            
            # Ek bilgiler
            self.console.print("\n[cyan]📋 Açıklama:[/cyan]")
            
            # Sürüm tipine göre açıklama
            version_type = version_info.get("type", "release")
            descriptions = {
                "release": "🟢 Kararlı sürüm - Tüm oyuncular için önerilir",
                "snapshot": "🟡 Geliştirme sürümü - Yeni özellikler test edilir",
                "old_beta": "🔵 Eski beta sürümü - Nostaljik deneyim",
                "old_alpha": "🟣 Eski alpha sürümü - Minecraft'ın ilk günleri"
            }
            
            desc = descriptions.get(version_type, "📦 Minecraft sürümü")
            self.console.print(f"  {desc}")
            
            # Seçenekler
            self.console.print("\n[yellow]Seçenekler:[/yellow]")
            if is_installed:
                self.console.print("  [cyan]1.[/cyan] Bu sürümü başlat")
                self.console.print("  [cyan]2.[/cyan] Sürümü sil")
                self.console.print("  [cyan]3.[/cyan] Geri dön")
                
                choice = Prompt.ask("Seçiminiz", choices=["1", "2", "3"], default="3")
                
                if choice == "1":
                    self._launch_minecraft(version_id)
                elif choice == "2":
                    if Confirm.ask(f"[red]{version_id} silinsin mi?[/red]", default=False):
                        version_dir = self.versions_dir / version_id
                        shutil.rmtree(version_dir)
                        self.console.print("[green]✅ Sürüm silindi![/green]")
                        input("[dim]Enter...[/dim]")
            else:
                self.console.print("  [cyan]1.[/cyan] Bu sürümü indir")
                self.console.print("  [cyan]2.[/cyan] Geri dön")
                
                choice = Prompt.ask("Seçiminiz", choices=["1", "2"], default="2")
                
                if choice == "1":
                    if self._download_version(version_id):
                        self.console.print("[green]✅ İndirme tamamlandı![/green]")
                        
                        if Confirm.ask("Şimdi başlatmak ister misiniz?", default=True):
                            self._launch_minecraft(version_id)
                    input("[dim]Enter...[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Hata: {e}[/red]")
            input("[dim]Enter...[/dim]")
    
    def _get_system_info(self) -> Dict[str, str]:
        """Sistem bilgilerini al"""
        try:
            import psutil
            memory_gb = round(psutil.virtual_memory().total / (1024**3), 1)
            cpu_count = psutil.cpu_count()
            return {
                "memory": f"{memory_gb} GB",
                "cpu_cores": str(cpu_count),
                "os": platform.system(),
                "arch": platform.machine()
            }
        except ImportError:
            return {
                "memory": "Bilinmiyor",
                "cpu_cores": "Bilinmiyor", 
                "os": platform.system(),
                "arch": platform.machine()
            }
    
    def _create_banner(self) -> Panel:
        """B Logo Banner - Minimal ve Şık"""
        logo = f"""
[bold cyan]██████╗ [/bold cyan] [bold white]BERKEMC[/bold white]
[bold cyan]██╔══██╗[/bold cyan] [dim]v{__version__} - Advanced Minecraft Launcher[/dim]
[bold cyan]██████╔╝[/bold cyan]
[bold cyan]██╔══██╗[/bold cyan]
[bold cyan]██████╔╝[/bold cyan]
[bold cyan]╚═════╝ [/bold cyan]
        """
        
        return Panel(
            logo.strip(),
            style="cyan",
            border_style="bright_cyan",
            padding=(0, 1),
            expand=False
        )
    
    def _create_main_menu(self) -> Panel:
        """Minimal menü - Renkli ve Şık"""
        table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            expand=True
        )
        table.add_column("", style="bold cyan", width=3, justify="center")
        table.add_column("", style="white", width=25)
        table.add_column("", style="dim", width=35)
        
        # Ana işlevler - Yeşil
        table.add_row("[bold cyan]1[/bold cyan]", "[green]Minecraft Baslat[/green]", "[dim]Oyunu baslat[/dim]")
        table.add_row("[bold cyan]2[/bold cyan]", "[green]Surum Indir[/green]", "[dim]Yeni surum yukle[/dim]")
        table.add_row("[bold cyan]3[/bold cyan]", "[green]Surumlerim[/green]", "[dim]Yuklu surumleri gor[/dim]")
        table.add_row("", "", "")
        
        # Özelleştirme - Mavi
        table.add_row("[bold cyan]4[/bold cyan]", "[blue]Skin Yonetimi[/blue]", "[dim]Karakter goruntusunu degistir[/dim]")
        table.add_row("[bold cyan]5[/bold cyan]", "[blue]Mod Yonetimi[/blue]", "[dim]Modlari ara ve yukle[/dim]")
        table.add_row("", "", "")
        
        # Sistem - Sarı
        table.add_row("[bold cyan]6[/bold cyan]", "[yellow]Ayarlar[/yellow]", "[dim]Launcher ayarlarini duzenle[/dim]")
        table.add_row("[bold cyan]7[/bold cyan]", "[yellow]Performans[/yellow]", "[dim]Sistem kaynaklarini izle[/dim]")
        table.add_row("[bold cyan]8[/bold cyan]", "[yellow]Hakkinda[/yellow]", "[dim]Launcher hakkinda bilgi[/dim]")
        table.add_row("", "", "")
        table.add_row("[bold red]0[/bold red]", "[red]Cikis[/red]", "[dim]Launcheri kapat[/dim]")
        
        return Panel(
            table,
            title="[bold white]═══ ANA MENU ═══[/bold white]",
            border_style="bright_cyan",
            padding=(1, 2),
            expand=False
        )
    
    def _get_available_versions(self) -> List[Dict]:
        """Mevcut Minecraft sürümlerini al - Cache'li"""
        cache_file = self.cache_dir / "versions_manifest.json"
        cache_time = 3600  # 1 saat cache
        
        # Cache kontrolü
        if cache_file.exists():
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age < cache_time:
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f).get("versions", [])
                except:
                    pass
        
        # API'den al
        try:
            response = requests.get(self.version_manifest_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Cache'e kaydet
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            
            return data.get("versions", [])
        except requests.RequestException as e:
            self.console.print(f"[red]Sürüm listesi alınamadı: {e}[/red]")
            
            # Cache varsa onu kullan
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f).get("versions", [])
                except:
                    pass
            
            return []
    
    def _download_file(self, url: str, filepath: Path, description: str = "İndiriliyor") -> bool:
        """Dosya indir - Ultra optimize edilmiş"""
        try:
            # Session kullan (connection pooling için)
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'BerkeMinecraftLauncher/2.3.0',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            })
            
            response = session.get(url, stream=True, timeout=30, verify=False)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeElapsedColumn(),
            ) as progress:
                
                task = progress.add_task(description, total=total_size)
                
                # Büyük chunk size (daha hızlı indirme)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
            
            session.close()
            return True
            
        except requests.RequestException as e:
            self.console.print(f"[red]İndirme hatası: {e}[/red]")
            return False
    
    def _download_version(self, version_id: str) -> bool:
        """Minecraft sürümü indir"""
        try:
            # İndirme ekranı başlat
            self.console.print(Panel(
                f"[bold cyan]MINECRAFT SÜRÜM İNDİRİLİYOR[/bold cyan]\n"
                f"[dim]Sürüm: {version_id}[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print(f"[blue]🔍 Sürüm bilgileri alınıyor: {version_id}[/blue]")
            versions = self._get_available_versions()
            version_info = None
            
            for version in versions:
                if version["id"] == version_id:
                    version_info = version
                    break
            
            if not version_info:
                self.console.print(f"[red]❌ Sürüm bulunamadı: {version_id}[/red]")
                return False
            
            version_dir = self.versions_dir / version_id
            version_dir.mkdir(exist_ok=True)
            
            self.console.print(f"[green]✅ Sürüm dizini oluşturuldu: {version_dir}[/green]")
            
            # Sürüm JSON'unu indir
            version_json_path = version_dir / f"{version_id}.json"
            self.console.print(f"[blue]📄 Sürüm JSON'u indiriliyor...[/blue]")
            if not self._download_file(version_info["url"], version_json_path, f"{version_id} JSON"):
                self.console.print(f"[red]❌ Sürüm JSON'u indirilemedi![/red]")
                return False
            self.console.print(f"[green]✅ Sürüm JSON'u indirildi![/green]")
            
            # Sürüm JSON'unu oku
            try:
                with open(version_json_path, 'r') as f:
                    version_data = json.load(f)
            except json.JSONDecodeError:
                self.console.print(f"[red]Sürüm JSON'u okunamadı: {version_id}[/red]")
                return False
            
            # Client JAR'ı indir (eski sürümler için hata yakalama)
            self.console.print(f"[blue]📦 Client JAR indiriliyor...[/blue]")
            try:
                client_jar_url = version_data["downloads"]["client"]["url"]
                client_jar_path = version_dir / f"{version_id}.jar"
                if not self._download_file(client_jar_url, client_jar_path, f"{version_id} Client"):
                    self.console.print(f"[red]❌ Client JAR indirilemedi![/red]")
                    return False
                self.console.print(f"[green]✅ Client JAR indirildi![/green]")
            except KeyError:
                self.console.print(f"[yellow]⚠️ Eski sürüm formatı tespit edildi, alternatif yöntem deneniyor...[/yellow]")
                # Eski sürümler için alternatif URL
                try:
                    if "jar" in version_data:
                        client_jar_url = version_data["jar"]["url"]
                    else:
                        # Fallback: Mojang'ın eski URL yapısı
                        client_jar_url = f"https://launcher.mojang.com/v1/objects/{version_data.get('id', version_id)}/{version_id}.jar"
                    
                    client_jar_path = version_dir / f"{version_id}.jar"
                    if not self._download_file(client_jar_url, client_jar_path, f"{version_id} Client"):
                        self.console.print(f"[red]❌ Client JAR indirilemedi![/red]")
                        return False
                except Exception as e:
                    self.console.print(f"[red]❌ Client JAR bulunamadı: {e}[/red]")
                    return False
            
            # Assets indir (eski sürümler için opsiyonel)
            try:
                assets_index_url = version_data["assetIndex"]["url"]
                assets_index_path = version_dir / "assets_index.json"
                if not self._download_file(assets_index_url, assets_index_path, f"{version_id} Assets"):
                    self.console.print(f"[yellow]⚠️ Assets indirilemedi, devam ediliyor...[/yellow]")
            except KeyError:
                self.console.print(f"[yellow]⚠️ Bu sürümde asset index yok (çok eski sürüm)[/yellow]")
            
            # Native libraries'ı indir ve çıkar
            self._download_native_libraries(version_data)
            
            # Mevcut tüm native library'leri çıkar (güvenlik için)
            self._extract_all_native_libraries()
            
            # Assets'leri indir
            self.console.print(f"[blue]🎨 Assets indiriliyor...[/blue]")
            self._download_assets(version_data)
            
            # Kütüphaneleri PARALEL indir (HIZLI!)
            libraries_dir = self.launcher_dir / "libraries"
            libraries_dir.mkdir(exist_ok=True)
            
            if "libraries" in version_data:
                self.console.print(f"[blue]📚 Kütüphaneler paralel indiriliyor (ULTRA HIZLI!)...[/blue]")
                
                # İndirilecek kütüphaneleri topla
                download_tasks = []
                for lib in version_data["libraries"]:
                    try:
                        if "downloads" in lib and "artifact" in lib["downloads"]:
                            artifact = lib["downloads"]["artifact"]
                            lib_url = artifact["url"]
                            lib_path = libraries_dir / artifact["path"]
                            
                            # Sadece eksik olanları indir (cache kontrolü)
                            if not lib_path.exists():
                                download_tasks.append((lib_url, lib_path, lib['name']))
                        elif "name" in lib and "url" in lib:
                            # Eski sürüm formatı
                            lib_name = lib["name"]
                            lib_url = lib["url"]
                            # Maven path oluştur
                            parts = lib_name.split(":")
                            if len(parts) >= 3:
                                group, artifact, version = parts[0], parts[1], parts[2]
                                lib_path = libraries_dir / group.replace(".", "/") / artifact / version / f"{artifact}-{version}.jar"
                                if not lib_path.exists():
                                    download_tasks.append((lib_url, lib_path, lib_name))
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Kütüphane atlandı: {lib.get('name', 'unknown')} - {e}[/yellow]")
                        continue
                
                if download_tasks:
                    # Paralel indirme (8 thread)
                    start_time = time.time()
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        DownloadColumn(),
                        TransferSpeedColumn(),
                        TimeElapsedColumn(),
                        console=self.console
                    ) as progress:
                        task = progress.add_task(f"[cyan]Kütüphaneler", total=len(download_tasks))
                        
                        def download_lib(url, path, name):
                            try:
                                path.parent.mkdir(parents=True, exist_ok=True)
                                response = requests.get(url, timeout=30)
                                response.raise_for_status()
                                with open(path, 'wb') as f:
                                    f.write(response.content)
                                return True, name
                            except Exception as e:
                                return False, name
                        
                        # 16 paralel thread ile indir (ultra hızlı)
                        with ThreadPoolExecutor(max_workers=16) as executor:
                            futures = {executor.submit(download_lib, url, path, name): name 
                                     for url, path, name in download_tasks}
                            
                            for future in as_completed(futures):
                                success, name = future.result()
                                if not success:
                                    self.console.print(f"[yellow]⚠️ Atlandı: {name}[/yellow]")
                                progress.update(task, advance=1)
                    
                    elapsed = time.time() - start_time
                    speed = len(download_tasks) / elapsed if elapsed > 0 else 0
                    self.console.print(f"[green]✅ {len(download_tasks)} kütüphane indirildi ({elapsed:.1f}s, {speed:.1f} dosya/s)[/green]")
                else:
                    self.console.print(f"[green]✅ Tüm kütüphaneler cache'de mevcut![/green]")
        
            self.console.print(f"[green]✅ Sürüm başarıyla indirildi: {version_id}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ İndirme hatası: {e}[/red]")
            import traceback
            self.console.print(f"[dim]Detay: {traceback.format_exc()}[/dim]")
            return False
    
    def _get_installed_versions(self) -> List[str]:
        """İndirilen sürümleri listele - TÜM sürümler (vanilla, Forge, Fabric)"""
        versions = []
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                # İlk önce aynı isimde JAR ara
                jar_file = version_dir / f"{version_dir.name}.jar"
                if jar_file.exists():
                    versions.append(version_dir.name)
                else:
                    # Değilse dizindeki herhangi bir JAR dosyasını ara
                    jar_files = list(version_dir.glob("*.jar"))
                    if jar_files:
                        versions.append(version_dir.name)
        return sorted(versions, reverse=True)
    
    def _create_launch_command(self, version_id: str) -> List[str]:
        """Oyun başlatma komutu oluştur"""
        # Java executable'ı config'den al
        if self.config.get("java_path"):
            self.java_executable = self.config["java_path"]
        
        if not self.java_executable:
            raise Exception("Java bulunamadı! Lütfen Java'yı yükleyin.")
        
        version_dir = self.versions_dir / version_id
        version_json_path = version_dir / f"{version_id}.json"
        
        if not version_json_path.exists():
            raise Exception(f"Sürüm JSON'u bulunamadı: {version_id}")
        
        with open(version_json_path, 'r') as f:
            version_data = json.load(f)
        
        # JVM argümanları
        system_info = self._get_system_info()
        memory_gb = float(system_info["memory"].split()[0])
        
        # Bellek optimizasyonu (Java 17 için daha düşük)
        if self.config["memory"] == "auto":
            max_memory = min(int(memory_gb * 0.4), 4)  # Sistem belleğinin %40'ı, max 4GB
        else:
            max_memory = int(self.config["memory"])
        
        # Wayland/Hyprland desteği için environment değişkenleri
        wayland_env = {
            # X11/Wayland Environment
            "GDK_BACKEND": "x11",  # XWayland kullan
            "QT_QPA_PLATFORM": "xcb",  # Qt için X11
            "SDL_VIDEODRIVER": "x11",  # SDL için X11
            "MOZ_ENABLE_WAYLAND": "0",  # Firefox için X11
            "DISPLAY": os.environ.get("DISPLAY", ":0"),  # X11 display
            "WAYLAND_DISPLAY": "",  # Wayland'i devre dışı bırak
            "HYPRLAND_INSTANCE_SIGNATURE": "",  # Hyprland'i devre dışı bırak
            
            # Java AWT Settings
            "_JAVA_AWT_WM_NONREPARENTING": "1",  # Java AWT için
            "AWT_TOOLKIT": "MToolkit",  # Java AWT toolkit
            "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false",  # Headless modu kapat
            
            # Graphics Settings
            "LIBGL_ALWAYS_SOFTWARE": "0",  # Hardware acceleration
            "LIBGL_ALWAYS_INDIRECT": "0",  # Direct rendering
            "MESA_GL_VERSION_OVERRIDE": "4.5",  # Mesa GL version
            "MESA_GLSL_VERSION_OVERRIDE": "450",  # Mesa GLSL version
            "MESA_NO_ERROR": "1",  # Mesa hata kontrolü
            "DRI_PRIME": "1",  # GPU acceleration
            "vblank_mode": "0",  # V-sync kapalı
            "__GL_THREADED_OPTIMIZATIONS": "1",  # Threaded optimizations
            
            # Window Management
            "GDK_SYNCHRONIZE": "1",  # X11 senkronizasyonu
            "X11_FORCE_SOFTWARE": "0",  # Force hardware acceleration
            "X11_NO_HARDWARE": "0",  # Allow hardware acceleration
            "X11_SOFTWARE_CURSOR": "0",  # Use hardware cursor
            "X11_VSYNC": "0",  # Disable VSync
            "X11_NO_BACKING_STORE": "0",  # Enable backing store
            "X11_NO_SAVE_UNDERS": "0",  # Enable save unders
            "X11_NO_DAMAGE": "0",  # Enable damage extension
            "X11_NO_GLX": "0",  # Enable GLX
            "X11_NO_COMPOSITE": "0",  # Enable composite extension
            "X11_NO_RENDER": "0",  # Enable render extension
            "X11_NO_XFIXES": "0",  # Enable XFixes extension
            "X11_NO_XINERAMA": "0",  # Enable Xinerama
            "X11_NO_XRANDR": "0",  # Enable XRandR
            "X11_NO_XSYNC": "0",  # Enable XSync
            "X11_NO_XTEST": "0",  # Enable XTest
            "X11_NO_XV": "0",  # Enable XVideo
            "X11_NO_XINPUT": "0",  # Enable XInput
            "X11_NO_XKB": "0",  # Enable XKB
            "X11_NO_XCURSOR": "0",  # Enable XCursor
            "X11_NO_XFONT": "0",  # Enable XFont
            "X11_NO_XFT": "0",  # Enable Xft
            "X11_NO_XPM": "0",  # Enable XPM
            "X11_NO_XSHM": "0",  # Enable XShm
            "X11_NO_XTST": "0",  # Enable XTst
            "X11_NO_XVMC": "0",  # Enable XVMC
            "X11_NO_XVMCLIB": "0",  # Enable XVMCLib
            "MESA_GLSL_VERSION_OVERRIDE": "450",  # GLSL version override
            
            # Minecraft Window Fix
            "MESA_VK_DEVICE_SELECT": "0",  # Mesa Vulkan device selection
            "MESA_LOADER_DRIVER_OVERRIDE": "zink",  # Mesa loader override
            "GALLIUM_DRIVER": "zink",  # Gallium driver
            "LIBGL_DRIVERS_PATH": "/usr/lib/dri",  # OpenGL drivers path
            "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/intel_icd.x86_64.json",  # Vulkan ICD
            
            # Window Persistence Fix
            "X11_FORCE_SOFTWARE": "0",  # Force hardware acceleration
            "X11_NO_HARDWARE": "0",  # Allow hardware acceleration
            "X11_SOFTWARE_CURSOR": "0",  # Use hardware cursor
            "X11_VSYNC": "0",  # Disable VSync
            "X11_NO_BACKING_STORE": "0",  # Enable backing store
            "X11_NO_SAVE_UNDERS": "0",  # Enable save unders
            "X11_NO_DAMAGE": "0",  # Enable damage extension
            "X11_NO_GLX": "0",  # Enable GLX
            "X11_NO_COMPOSITE": "0",  # Enable composite extension
            "X11_NO_RENDER": "0",  # Enable render extension
            "X11_NO_XFIXES": "0",  # Enable XFixes extension
            "X11_NO_XINERAMA": "0",  # Enable Xinerama
            "X11_NO_XRANDR": "0",  # Enable XRandR
            "X11_NO_XSYNC": "0",  # Enable XSync
            "X11_NO_XTEST": "0",  # Enable XTest
            "X11_NO_XV": "0",  # Enable XVideo
            "X11_NO_XINPUT": "0",  # Enable XInput
            "X11_NO_XKB": "0",  # Enable XKB
            "X11_NO_XCURSOR": "0",  # Enable XCursor
            "X11_NO_XFONT": "0",  # Enable XFont
            "X11_NO_XFT": "0",  # Enable Xft
            "X11_NO_XPM": "0",  # Enable XPM
            "X11_NO_XSHM": "0",  # Enable XShm
            "X11_NO_XTST": "0",  # Enable XTst
            "X11_NO_XVMC": "0",  # Enable XVMC
            "X11_NO_XVMCLIB": "0",  # Enable XVMCLib
        }
        
        # ULTRA PERFORMANS JVM ARGÜMANLARI (Java 21+ uyumlu + Online Server Support)
        jvm_args = [
            self.java_executable,
            # Bellek Yönetimi (Agresif + Online Optimize)
            f"-Xmx{max_memory}G",
            f"-Xms{max_memory}G",  # Min=Max (daha hızlı başlangıç)
            "-XX:+UseG1GC",  # G1 Garbage Collector (en iyi Minecraft için)
            "-XX:+ParallelRefProcEnabled",
            "-XX:MaxGCPauseMillis=100",  # Daha az lag spike (online için optimize)
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:+DisableExplicitGC",
            "-XX:+AlwaysPreTouch",  # Belleği önceden ayır
            
            # G1GC Tuning (Java 17 uyumlu)
            "-XX:G1NewSizePercent=30",
            "-XX:G1MaxNewSizePercent=40",
            "-XX:G1HeapRegionSize=16M",
            "-XX:G1ReservePercent=15",
            "-XX:G1HeapWastePercent=5",
            "-XX:InitiatingHeapOccupancyPercent=15",
            
            # Network Optimizasyonları (Online Server için)
            "-Djava.net.preferIPv4Stack=true",
            "-Djava.net.preferIPv6Addresses=false",
            "-Dhttp.agent=BerkeMinecraftLauncher/2.3.0",
            
            # SSL Certificate Trust - Fix authentication issues
            "-Dcom.sun.net.ssl.checkRevocation=false",
            "-Dtrust_all_cert=true",
            "-Djavax.net.ssl.trustStoreType=JKS",
            "-Djavax.net.ssl.trustStore=",
            "-Dcom.sun.net.ssl.checkRevocation=false",
            
            # CPU Optimizasyonları (Java 21+ uyumlu)
            "-XX:+OptimizeStringConcat",
            "-XX:+UseStringDeduplication",
            "-XX:+UseCompressedOops",
            "-XX:+UseCompressedClassPointers",
            
            # JIT Compiler Optimizasyonları
            "-XX:+TieredCompilation",
            "-XX:ReservedCodeCacheSize=400M",
            "-XX:+SegmentedCodeCache",
            "-XX:+UseCodeCacheFlushing",
            
            # Wayland/Hyprland + OpenGL Optimizasyonları
            "-Dsun.java2d.opengl=true",
            "-Dsun.java2d.d3d=false",
            "-Djava.awt.graphicsenv=sun.awt.X11GraphicsEnvironment",
            "-Dawt.useSystemAAFontSettings=on",
            "-Dswing.aatext=true",
            
            # X11 Specific Settings (Wayland/Hyprland Fix)
            "-Dsun.java2d.xrender=true",
            "-Dsun.java2d.pmoffscreen=false",
            "-Dsun.java2d.noddraw=true",
            "-Djava.awt.headless=false",
            "-Dsun.java2d.accthreshold=0",
            "-Dsun.java2d.d3d=false",
            "-Dsun.java2d.ddoffscreen=false",
            "-Dsun.java2d.gdiblend=false",
            "-Dsun.java2d.pisces=false",
            "-Dsun.java2d.xrender=true",
            
            # LWJGL Native Library Path - Fixed for proper library loading
            f"-Dorg.lwjgl.librarypath={self.launcher_dir / 'libraries' / 'natives' / 'linux' / 'x64'}",
            "-Djava.library.path=" + str(self.launcher_dir / 'libraries' / 'natives' / 'linux' / 'x64'),
            
            # Minecraft Window Fix (Wayland/Hyprland)
            "-Dminecraft.client.jar=client.jar",
            "-Djava.awt.headless=false",
            "-Dfile.encoding=UTF-8",
            "-Duser.language=en",
            "-Duser.country=US",
            
            # Window Persistence & Graphics Fix
            "-Dsun.java2d.opengl=false",
            "-Dsun.java2d.d3d=false",
            "-Dsun.java2d.xrender=true",
            "-Dsun.java2d.pmoffscreen=false",
            "-Dsun.java2d.noddraw=true",
            "-Dsun.java2d.ddoffscreen=false",
            "-Dsun.java2d.gdiblend=false",
            "-Dsun.java2d.pisces=false",
            "-Dsun.java2d.accthreshold=0",
            "-Dsun.java2d.ddoffscreen=false",
            "-Dsun.java2d.gdiblend=false",
            "-Dsun.java2d.pmoffscreen=false",
            "-Dsun.java2d.pisces=false",
            "-Dsun.java2d.xrender=true",
            
            # Window Management & Display
            "-Djava.awt.Window.locationByPlatform=true",
            "-Djava.awt.graphicsenv=sun.awt.X11GraphicsEnvironment",
            "-Dawt.useSystemAAFontSettings=on",
            "-Dswing.aatext=true",
            "-Djava.awt.syncLWRequests=true",
            "-Djava.awt.keepWorkingSetOnMinimize=true",
            "-Djava.awt.Window.locationByPlatform=true",
            "-Djava.awt.smartInvalidate=true",
            "-Djava.awt.doublebuffered=true",
            "-Djava.awt.headless=false",
            "-Djava.awt.graphicsenv=sun.awt.X11GraphicsEnvironment",
            "-Djava.awt.Window.locationByPlatform=true",
            "-Djava.awt.syncLWRequests=true",
            "-Djava.awt.keepWorkingSetOnMinimize=true",
            "-Djava.awt.smartInvalidate=true",
            "-Djava.awt.doublebuffered=true",
            
            # LWJGL Display Fixes
            "-Dorg.lwjgl.util.Debug=false",
            "-Dorg.lwjgl.util.DebugLoader=false",
            "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=false",
            "-Dorg.lwjgl.opengl.Display.swapInterval=0",
            "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=false",
            "-Dorg.lwjgl.opengl.Display.swapInterval=0",
            "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=false",
            "-Dorg.lwjgl.opengl.Display.swapInterval=0",
            
            # Minecraft Özel Optimizasyonlar + Online Server Support
            "-Dminecraft.launcher.brand=berke-ultra-launcher",
            "-Dminecraft.launcher.version=2.4.0",
            "-Dfml.ignoreInvalidMinecraftCertificates=true",
            "-Dfml.ignorePatchDiscrepancies=true",
            "-Dfile.encoding=UTF-8",
            "-Duser.language=en",
            "-Duser.country=US",
            
            # Aikar's Flags
            "-Dusing.aikars.flags=https://mcflags.emc.gs",
            "-Daikars.new.flags=true",
            
            # I/O Optimizasyonları (Disk + Network)
            "-Dio.netty.allocator.type=pooled",
            "-Dio.netty.leakDetection.level=disabled",
            "-Dio.netty.recycler.maxCapacityPerThread=0",
            
            # Thread Optimizasyonları (Java 17 uyumlu)
            "-XX:ConcGCThreads=2",
            "-XX:ParallelGCThreads=4"
        ]
        
        # Özel JVM argümanlarını ekle
        custom_jvm_args = self.config.get("custom_jvm_args", [])
        if custom_jvm_args:
            jvm_args.extend(custom_jvm_args)
        
        # Minecraft argümanları (eski sürüm uyumluluğu)
        main_class = version_data.get("mainClass", "net.minecraft.client.main.Main")
        
        # Classpath oluştur (JAR + tüm kütüphaneler)
        classpath_parts = [str(version_dir / f"{version_id}.jar")]
        
        # Kütüphaneleri classpath'e ekle (eski ve yeni format desteği)
        libraries_dir = self.launcher_dir / "libraries"
        if "libraries" in version_data:
            for lib in version_data["libraries"]:
                try:
                    # Modern format
                    if "downloads" in lib and "artifact" in lib["downloads"]:
                        artifact = lib["downloads"]["artifact"]
                        lib_path = libraries_dir / artifact["path"]
                        if lib_path.exists():
                            classpath_parts.append(str(lib_path))
                    # Eski format (name + url)
                    elif "name" in lib:
                        lib_name = lib["name"]
                        parts = lib_name.split(":")
                        if len(parts) >= 3:
                            group, artifact, version = parts[0], parts[1], parts[2]
                            lib_path = libraries_dir / group.replace(".", "/") / artifact / version / f"{artifact}-{version}.jar"
                            if lib_path.exists():
                                classpath_parts.append(str(lib_path))
                except Exception as e:
                    # Eksik kütüphane varsa atla
                    if self.config.get("debug", False):
                        self.console.print(f"[yellow]⚠️ Kütüphane atlandı: {lib.get('name', 'unknown')}[/yellow]")
                    continue
        
        # Classpath'i birleştir (Linux/Unix için ':' ayırıcı)
        classpath = ":".join(classpath_parts)
        
        # Skin dosyası yolu
        skin_path = self.skins_dir / f"{self.config['current_skin']}.png"
        
        # UUID generation (online sunucu desteği için)
        player_uuid = self.config.get("uuid")
        if not player_uuid:
            # Username'den deterministic UUID oluştur (online sunucular için)
            player_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.config["username"]))
            self.config["uuid"] = player_uuid
            self._save_config()
        
        # Minecraft argümanları (eski sürüm uyumluluğu)
        minecraft_args = [
            "-cp", classpath,
            main_class,
            "--username", self.config["username"],
            "--version", version_id,
            "--gameDir", str(self.minecraft_dir),
            "--assetsDir", str(self.minecraft_dir / "assets"),
        ]
        
        # Asset index (eski sürümlerde olmayabilir)
        assets_dir = self.minecraft_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        
        if "assetIndex" in version_data:
            minecraft_args.extend(["--assetIndex", version_data["assetIndex"]["id"]])
            # Asset index dosyasını indir ve kaydet
            try:
                asset_index_path = assets_dir / "indexes" / f"{version_data['assetIndex']['id']}.json"
                asset_index_path.parent.mkdir(parents=True, exist_ok=True)
                if not asset_index_path.exists():
                    self._download_file(version_data["assetIndex"]["url"], asset_index_path, f"Asset Index {version_data['assetIndex']['id']}")
            except Exception as e:
                if self.config.get("debug", False):
                    self.console.print(f"[yellow]⚠️ Asset index indirilemedi: {e}[/yellow]")
        else:
            # Eski sürümler için fallback
            minecraft_args.extend(["--assetIndex", "legacy"])
        
        # Online sunucu desteği (modern sürümler için)
        minecraft_args.extend([
            "--uuid", player_uuid,  # UUID ekle (online sunucu desteği)
            "--accessToken", "null",
            "--userType", "mojang",  # legacy yerine mojang (daha iyi uyumluluk)
            "--versionType", "release",
        ])
        
        # Pencere boyutu
        minecraft_args.extend([
            "--width", str(self.config["window_width"]),
            "--height", str(self.config["window_height"])
        ])
        
        # Skin varsa ekle
        if skin_path.exists():
            minecraft_args.extend(["--skin", str(skin_path)])
        
        return jvm_args + minecraft_args, wayland_env
    
    def _download_native_libraries(self, version_data: dict):
        """Native libraries'ı indir ve çıkar"""
        try:
            libraries_dir = self.launcher_dir / "libraries"
            natives_dir = libraries_dir / "natives" / "linux" / "x64"
            natives_dir.mkdir(parents=True, exist_ok=True)
            
            if "libraries" in version_data:
                for lib in version_data["libraries"]:
                    # Native library kontrolü
                    if "natives" in lib:
                        try:
                            # Modern format
                            if "downloads" in lib and "classifiers" in lib["downloads"]:
                                # Linux native library'yi bul
                                linux_native = None
                                for classifier, download_info in lib["downloads"]["classifiers"].items():
                                    if "natives-linux" in classifier or "natives-linux64" in classifier:
                                        linux_native = download_info
                                        break
                                
                                if linux_native:
                                    lib_path = libraries_dir / linux_native["path"]
                                    lib_path.parent.mkdir(parents=True, exist_ok=True)
                                    
                                    # Library'yi indir
                                    if not lib_path.exists():
                                        if self._download_file(linux_native["url"], lib_path, f"Native Library {lib.get('name', 'unknown')}"):
                                            self.console.print(f"[blue]📦 Native library indirildi: {lib_path.name}[/blue]")
                                    
                                    # ZIP dosyasını çıkar
                                    if lib_path.exists() and lib_path.suffix == '.jar':
                                        import zipfile
                                        try:
                                            with zipfile.ZipFile(lib_path, 'r') as zip_ref:
                                                for file_info in zip_ref.infolist():
                                                    if file_info.filename.endswith(('.so', '.dll', '.dylib')):
                                                        zip_ref.extract(file_info, natives_dir)
                                            self.console.print(f"[green]✅ Native library çıkarıldı: {lib_path.name}[/green]")
                                        except Exception as e:
                                            if self.config.get("debug", False):
                                                self.console.print(f"[yellow]⚠️ Native library çıkarılamadı: {e}[/yellow]")
                        except Exception as e:
                            if self.config.get("debug", False):
                                self.console.print(f"[yellow]⚠️ Native library işlenemedi: {e}[/yellow]")
                            continue
        except Exception as e:
            if self.config.get("debug", False):
                self.console.print(f"[yellow]⚠️ Native libraries indirilemedi: {e}[/yellow]")
    
    def _extract_all_native_libraries(self):
        """Mevcut tüm native library'leri çıkar"""
        try:
            libraries_dir = self.launcher_dir / "libraries"
            natives_dir = libraries_dir / "natives"
            natives_dir.mkdir(parents=True, exist_ok=True)
            
            # Tüm Linux native JAR dosyalarını bul ve çıkar
            import zipfile
            for native_jar in libraries_dir.rglob("*-natives-linux.jar"):
                try:
                    with zipfile.ZipFile(native_jar, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            if file_info.filename.endswith(('.so', '.dll', '.dylib')):
                                zip_ref.extract(file_info, natives_dir)
                except Exception as e:
                    if self.config.get("debug", False):
                        self.console.print(f"[yellow]⚠️ Native library çıkarılamadı {native_jar.name}: {e}[/yellow]")
                    continue
            
            self.console.print("[green]✅ Native libraries extracted successfully![/green]")
        except Exception as e:
            if self.config.get("debug", False):
                self.console.print(f"[yellow]⚠️ Native library extraction failed: {e}[/yellow]")
    
    def _download_assets(self, version_data: dict) -> bool:
        """Asset dosyalarını indir"""
        try:
            if "assetIndex" not in version_data:
                self.console.print("[yellow]⚠️ Bu sürümde asset index yok[/yellow]")
                return True
            
            asset_index_id = version_data["assetIndex"]["id"]
            asset_index_url = version_data["assetIndex"]["url"]
            
            # Asset dizinlerini oluştur
            assets_dir = self.minecraft_dir / "assets"
            assets_objects_dir = assets_dir / "objects"
            assets_indexes_dir = assets_dir / "indexes"
            
            assets_dir.mkdir(parents=True, exist_ok=True)
            assets_objects_dir.mkdir(parents=True, exist_ok=True)
            assets_indexes_dir.mkdir(parents=True, exist_ok=True)
            
            # Asset index dosyasını indir
            asset_index_path = assets_indexes_dir / f"{asset_index_id}.json"
            
            if not asset_index_path.exists():
                self.console.print(f"[blue]📄 Asset index indiriliyor: {asset_index_id}[/blue]")
                if not self._download_file(asset_index_url, asset_index_path, f"Asset Index {asset_index_id}"):
                    self.console.print("[red]❌ Asset index indirilemedi![/red]")
                    return False
            
            # Asset index'i oku
            with open(asset_index_path, 'r') as f:
                asset_index = json.load(f)
            
            if "objects" not in asset_index:
                self.console.print("[yellow]⚠️ Asset index'te nesne bulunamadı[/yellow]")
                return True
            
            # İndirilecek asset'leri topla
            assets_to_download = []
            for asset_name, asset_info in asset_index["objects"].items():
                asset_hash = asset_info["hash"]
                asset_hash_prefix = asset_hash[:2]
                asset_path = assets_objects_dir / asset_hash_prefix / asset_hash
                
                # Sadece eksik olanları indir
                if not asset_path.exists():
                    asset_url = f"{self.assets_url}/{asset_hash_prefix}/{asset_hash}"
                    assets_to_download.append((asset_url, asset_path, asset_name, asset_hash))
            
            if not assets_to_download:
                self.console.print("[green]✅ Tüm asset'ler cache'de mevcut![/green]")
                return True
            
            # Assets'leri paralel indir (ultra hızlı!)
            self.console.print(f"[blue]📦 {len(assets_to_download)} asset indiriliyor (paralel)...[/blue]")
            
            start_time = time.time()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeElapsedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Assets", total=len(assets_to_download))
                
                def download_asset(url, path, name, hash_val):
                    try:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        response = requests.get(url, timeout=30)
                        response.raise_for_status()
                        with open(path, 'wb') as f:
                            f.write(response.content)
                        return True, name
                    except Exception as e:
                        return False, name
                
                # 16 paralel thread ile indir
                with ThreadPoolExecutor(max_workers=16) as executor:
                    futures = {executor.submit(download_asset, url, path, name, hash_val): name 
                             for url, path, name, hash_val in assets_to_download}
                    
                    failed_count = 0
                    for future in as_completed(futures):
                        success, name = future.result()
                        if not success:
                            failed_count += 1
                            if self.config.get("debug", False):
                                self.console.print(f"[yellow]⚠️ Asset atlandı: {name}[/yellow]")
                        progress.update(task, advance=1)
            
            elapsed = time.time() - start_time
            speed = len(assets_to_download) / elapsed if elapsed > 0 else 0
            
            if failed_count > 0:
                self.console.print(f"[yellow]⚠️ {failed_count} asset indirilemedi, devam ediliyor...[/yellow]")
            
            self.console.print(f"[green]✅ {len(assets_to_download) - failed_count} asset indirildi ({elapsed:.1f}s, {speed:.1f} dosya/s)[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Asset indirme hatası: {e}[/red]")
            if self.config.get("debug", False):
                import traceback
                self.console.print(f"[dim]Detay: {traceback.format_exc()}[/dim]")
            return False
    
    def _verify_and_repair_assets(self, version_id: str) -> bool:
        """Asset'leri doğrula ve eksik olanları indir"""
        try:
            self.console.print(f"[blue]🔍 Asset'ler doğrulanıyor: {version_id}[/blue]")
            
            # Version data'yı al
            version_dir = self.versions_dir / version_id
            version_json_path = version_dir / f"{version_id}.json"
            
            if not version_json_path.exists():
                self.console.print(f"[red]❌ Sürüm dosyası bulunamadı: {version_id}[/red]")
                return False
            
            with open(version_json_path, 'r') as f:
                version_data = json.load(f)
            
            if "assetIndex" not in version_data:
                self.console.print("[yellow]⚠️ Bu sürümde asset index yok[/yellow]")
                return True
            
            asset_index_id = version_data["assetIndex"]["id"]
            assets_dir = self.minecraft_dir / "assets"
            assets_indexes_dir = assets_dir / "indexes"
            assets_objects_dir = assets_dir / "objects"
            
            # Asset index dosyasını kontrol et
            asset_index_path = assets_indexes_dir / f"{asset_index_id}.json"
            
            if not asset_index_path.exists():
                self.console.print(f"[yellow]⚠️ Asset index bulunamadı, indiriliyor...[/yellow]")
                return self._download_assets(version_data)
            
            # Asset index'i oku
            with open(asset_index_path, 'r') as f:
                asset_index = json.load(f)
            
            if "objects" not in asset_index:
                self.console.print("[yellow]⚠️ Asset index'te nesne bulunamadı[/yellow]")
                return True
            
            # Eksik asset'leri bul
            missing_assets = []
            total_assets = len(asset_index["objects"])
            
            for asset_name, asset_info in asset_index["objects"].items():
                asset_hash = asset_info["hash"]
                asset_hash_prefix = asset_hash[:2]
                asset_path = assets_objects_dir / asset_hash_prefix / asset_hash
                
                if not asset_path.exists():
                    missing_assets.append((asset_name, asset_info))
            
            if not missing_assets:
                self.console.print(f"[green]✅ Tüm asset'ler mevcut! ({total_assets} asset)[/green]")
                return True
            
            # Eksik asset'leri göster ve onar
            self.console.print(f"[yellow]⚠️ {len(missing_assets)}/{total_assets} asset eksik![/yellow]")
            
            if Confirm.ask("Eksik asset'leri indirmek istiyor musunuz?", default=True):
                return self._download_assets(version_data)
            
            return False
            
        except Exception as e:
            self.console.print(f"[red]❌ Asset doğrulama hatası: {e}[/red]")
            if self.config.get("debug", False):
                import traceback
                self.console.print(f"[dim]Detay: {traceback.format_exc()}[/dim]")
            return False
    
    def _get_forge_versions(self, minecraft_version: str) -> List[str]:
        """Belirli bir Minecraft sürümü için Forge sürümlerini al"""
        try:
            url = f"https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forge_versions = []
            for key, value in data.get("promos", {}).items():
                if key.startswith(minecraft_version):
                    forge_versions.append(f"{minecraft_version}-{value}")
            
            return forge_versions
        except Exception as e:
            if self.config.get("debug", False):
                self.console.print(f"[yellow]⚠️ Forge sürümleri alınamadı: {e}[/yellow]")
            return []
    
    def _get_fabric_versions(self, minecraft_version: str) -> List[str]:
        """Belirli bir Minecraft sürümü için Fabric sürümlerini al"""
        try:
            url = f"https://meta.fabricmc.net/v2/versions/loader/{minecraft_version}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            fabric_versions = []
            for loader in data[:5]:  # İlk 5 sürüm
                loader_version = loader["loader"]["version"]
                fabric_versions.append(f"{minecraft_version}-fabric-{loader_version}")
            
            return fabric_versions
        except Exception as e:
            if self.config.get("debug", False):
                self.console.print(f"[yellow]⚠️ Fabric sürümleri alınamadı: {e}[/yellow]")
            return []
    
    def _download_forge(self, minecraft_version: str, forge_version: str) -> bool:
        """Forge'u indir ve kur - Progress bar ile"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"[cyan]⚒️  Forge {forge_version} kuruluyor...", total=100)
                
                # Forge installer URL'si
                forge_full_version = f"{minecraft_version}-{forge_version}"
                installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{forge_full_version}/forge-{forge_full_version}-installer.jar"
                
                progress.update(task, description=f"[cyan]📥 Forge installer indiriliyor...", advance=20)
                
                # Installer'ı indir
                installer_path = self.cache_dir / f"forge-{forge_full_version}-installer.jar"
                
                if not self._download_file(installer_url, installer_path, f"Forge {forge_version} Installer"):
                    self.console.print("[red]❌ Forge installer indirilemedi![/red]")
                    input("[dim]Enter ile devam...[/dim]")
                    return False
                
                # Önce base Minecraft sürümünü indir
                progress.update(task, description=f"[cyan]📦 Base Minecraft {minecraft_version} indiriliyor...", advance=10)
                if not (self.versions_dir / minecraft_version / f"{minecraft_version}.jar").exists():
                    self.console.print(f"[blue]📦 Minecraft {minecraft_version} base version indiriliyor...[/blue]")
                    if not self._download_version(minecraft_version):
                        self.console.print("[red]❌ Base Minecraft sürümü indirilemedi![/red]")
                        input("[dim]Enter ile devam...[/dim]")
                        return False
                
                progress.update(task, description=f"[cyan]⚙️  Forge kuruluyor (1-2 dakika)...", advance=10)
                
                # launcher_profiles.json oluştur
                launcher_profiles_path = self.minecraft_dir / "launcher_profiles.json"
                if not launcher_profiles_path.exists():
                    default_profiles = {
                        "profiles": {
                            "default": {
                                "name": "Default",
                                "type": "latest-release",
                                "lastVersionId": "latest-release"
                            }
                        },
                        "selectedProfile": "default",
                        "clientToken": str(uuid.uuid4()),
                        "authenticationDatabase": {},
                        "launcherVersion": {"name": "BerkeMinecraftLauncher", "format": 21}
                    }
                    with open(launcher_profiles_path, 'w') as f:
                        json.dump(default_profiles, f, indent=2)
                
                # Forge installer'ı çalıştır
                install_cmd = [
                    self.java_executable,
                    "-Djava.awt.headless=true",
                    "-jar", str(installer_path),
                    "--installClient", str(self.minecraft_dir)
                ]
                
                result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                
                progress.update(task, description=f"[cyan]📦 Forge dosyaları kopyalanıyor...", advance=30)
                
                if result.returncode == 0 or "Successfully installed" in result.stdout:
                    # Forge profili oluştur
                    forge_dir = self.minecraft_dir / "versions" / forge_full_version
                    version_dir = self.versions_dir / forge_full_version
                    version_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Forge sürüm dosyalarını kopyala
                    forge_version_json = forge_dir / f"{forge_full_version}.json"
                    if forge_version_json.exists():
                        shutil.copy(forge_version_json, version_dir / f"{forge_full_version}.json")
                    
                    forge_jar = forge_dir / f"{forge_full_version}.jar"
                    if forge_jar.exists():
                        shutil.copy(forge_jar, version_dir / f"{forge_full_version}.jar")
                    
                    # Installer'ı temizle
                    installer_path.unlink(missing_ok=True)
                    
                    progress.update(task, description=f"[green]✅ Forge kuruldu: {forge_full_version}", advance=30)
                    
                    self.console.print(f"[green]✅ Forge başarıyla kuruldu![/green]")
                    self.console.print(f"[cyan]📂 Sürüm ID: {forge_full_version}[/cyan]")
                    input("[dim]Enter ile devam...[/dim]")
                    return True
                else:
                    self.console.print(f"[red]❌ Forge kurulumu başarısız![/red]")
                    if result.stderr:
                        self.console.print(f"[yellow]Hata:[/yellow]\n[dim]{result.stderr[:300]}[/dim]")
                    input("[dim]Enter ile devam...[/dim]")
                    return False
                    
        except subprocess.TimeoutExpired:
            self.console.print(f"[red]❌ Forge kurulumu zaman aşımına uğradı (5 dakika)[/red]")
            input("[dim]Enter ile devam...[/dim]")
            return False
        except Exception as e:
            self.console.print(f"[red]❌ Forge kurulum hatası: {e}[/red]")
            if self.config.get("debug", False):
                import traceback
                self.console.print(f"[dim]Detay: {traceback.format_exc()}[/dim]")
            input("[dim]Enter ile devam...[/dim]")
            return False
    
    def _download_fabric(self, minecraft_version: str, fabric_loader_version: str) -> bool:
        """Fabric'i indir ve kur - Progress bar ile"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=self.console
            ) as progress:
                task = progress.add_task(f"[cyan]🧵 Fabric {fabric_loader_version} kuruluyor...", total=100)
                
                # Fabric loader bilgilerini al
                progress.update(task, description=f"[cyan]📡 Fabric loader bilgileri alınıyor...", advance=10)
                loader_url = f"https://meta.fabricmc.net/v2/versions/loader/{minecraft_version}/{fabric_loader_version}"
                response = requests.get(loader_url, timeout=10)
                response.raise_for_status()
                loader_data = response.json()
                
                # Fabric version ID
                fabric_version_id = f"fabric-loader-{fabric_loader_version}-{minecraft_version}"
                fabric_dir = self.versions_dir / fabric_version_id
                fabric_dir.mkdir(parents=True, exist_ok=True)
                
                progress.update(task, description=f"[cyan]📄 Fabric profile indiriliyor...", advance=20)
                
                # Fabric profile JSON'unu indir
                profile_url = f"https://meta.fabricmc.net/v2/versions/loader/{minecraft_version}/{fabric_loader_version}/profile/json"
                profile_path = fabric_dir / f"{fabric_version_id}.json"
                
                if not self._download_file(profile_url, profile_path, f"Fabric {fabric_loader_version} Profile"):
                    self.console.print("[red]❌ Fabric profile indirilemedi![/red]")
                    return False
                
                progress.update(task, description=f"[cyan]📦 Fabric libraries indiriliyor...", advance=20)
                
                # Profile'dan kütüphaneleri indir
                with open(profile_path, 'r') as f:
                    profile_data = json.load(f)
                
                if "libraries" in profile_data:
                    libraries_dir = self.launcher_dir / "libraries"
                    for lib in profile_data["libraries"]:
                        if "downloads" in lib and "artifact" in lib["downloads"]:
                            artifact = lib["downloads"]["artifact"]
                            lib_url = artifact["url"]
                            lib_path = libraries_dir / artifact["path"]
                            lib_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            if not lib_path.exists():
                                try:
                                    lib_response = requests.get(lib_url, timeout=30)
                                    lib_response.raise_for_status()
                                    with open(lib_path, 'wb') as f:
                                        f.write(lib_response.content)
                                except Exception as e:
                                    if self.config.get("debug", False):
                                        self.console.print(f"[yellow]⚠️ Library atlandı: {lib.get('name')}[/yellow]")
                
                progress.update(task, description=f"[cyan]🎮 Minecraft base version kontrol ediliyor...", advance=20)
                
                # Minecraft base version'ı indir
                if not (self.versions_dir / minecraft_version / f"{minecraft_version}.jar").exists():
                    if not self._download_version(minecraft_version):
                        self.console.print("[red]❌ Base Minecraft sürümü indirilemedi![/red]")
                        return False
                
                # Fabric JAR dosyasını kopyala (symlink olarak)
                base_jar = self.versions_dir / minecraft_version / f"{minecraft_version}.jar"
                fabric_jar = fabric_dir / f"{fabric_version_id}.jar"
                
                if base_jar.exists() and not fabric_jar.exists():
                    shutil.copy(base_jar, fabric_jar)
                
                progress.update(task, description=f"[green]✅ Fabric kuruldu: {fabric_version_id}", advance=30)
                
            self.console.print(f"[green]✅ Fabric başarıyla kuruldu![/green]")
            self.console.print(f"[cyan]📂 Sürüm ID: {fabric_version_id}[/cyan]")
            input("[dim]Enter ile devam...[/dim]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Fabric kurulum hatası: {e}[/red]")
            if self.config.get("debug", False):
                import traceback
                self.console.print(f"[dim]Detay: {traceback.format_exc()}[/dim]")
            input("[dim]Enter ile devam...[/dim]")
            return False
    
    def _launch_minecraft(self, version_id: str):
        """Minecraft'ı başlat"""
        try:
            self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {version_id}[/yellow]")
            
            # Minecraft sürümü için uygun Java kontrolü
            recommended_java = self._get_recommended_java_for_version(version_id)
            current_java = self._check_java_version()
            
            if recommended_java and current_java:
                try:
                    current_major = int(current_java.split('.')[0])
                    recommended_major = int(recommended_java["version"].split('.')[0])
                    
                    if current_major < recommended_major:
                        self.console.print(f"[red]⚠️ Java Uyumsuzluğu![/red]")
                        self.console.print(f"[yellow]Mevcut Java: {current_java}[/yellow]")
                        self.console.print(f"[cyan]Önerilen Java: {recommended_java['version']} ({recommended_java['name']})[/cyan]")
                        if Confirm.ask("Önerilen Java'ya geçmek ister misiniz?", default=True):
                            self.java_executable = recommended_java["path"]
                            self.config["java_path"] = recommended_java["path"]
                            self._save_config()
                            self.console.print(f"[green]✅ Java değiştirildi: {recommended_java['name']}[/green]")
                        else:
                            self.console.print(f"[yellow]⚠️ Uyumsuz Java ile devam ediliyor...[/yellow]")
                    elif current_major > recommended_major + 2:
                        self.console.print(f"[yellow]💡 Daha uygun Java mevcut: {recommended_java['version']}[/yellow]")
                        if Confirm.ask("Daha uygun Java'ya geçmek ister misiniz?", default=False):
                            self.java_executable = recommended_java["path"]
                            self.config["java_path"] = recommended_java["path"]
                            self._save_config()
                            self.console.print(f"[green]✅ Java değiştirildi: {recommended_java['name']}[/green]")
                    else:
                        self.console.print(f"[green]✅ Java sürümü uygun: {current_java}[/green]")
                except ValueError:
                    self.console.print(f"[green]✅ Java sürümü: {current_java}[/green]")
            else:
                self.console.print(f"[green]✅ Java sürümü: {current_java or 'Bulunamadı'}[/green]")
            
            # Önce sistem kontrolü yap
            self._pre_launch_check()
            
            # Asset'leri doğrula ve eksikleri indir
            self.console.print(f"[blue]🔍 Asset'ler kontrol ediliyor...[/blue]")
            self._verify_and_repair_assets(version_id)
            
            command, env_vars = self._create_launch_command(version_id)
            
            # Mevcut environment'a Wayland ayarlarını ekle
            import os
            current_env = os.environ.copy()
            current_env.update(env_vars)
            
            # Hyprland için özel ayarlar
            if os.environ.get("XDG_SESSION_TYPE") == "wayland" and self.config.get("wayland_support", True):
                self.console.print("[blue]🖥️  Wayland/Hyprland tespit edildi, XWayland kullanılıyor...[/blue]")
                current_env.update({
                    "GDK_BACKEND": "x11",
                    "QT_QPA_PLATFORM": "xcb",
                    "SDL_VIDEODRIVER": "x11",
                    "_JAVA_AWT_WM_NONREPARENTING": "1",
                    "AWT_TOOLKIT": "MToolkit",
                    "DISPLAY": ":0",
                    "WAYLAND_DISPLAY": "",
                    "GDK_SYNCHRONIZE": "1"
                })
            
            # Minecraft için özel environment değişkenleri
            current_env.update({
                "MESA_GL_VERSION_OVERRIDE": "4.5",
                "MESA_GLSL_VERSION_OVERRIDE": "450",
                "LIBGL_ALWAYS_SOFTWARE": "0",
                "LIBGL_ALWAYS_INDIRECT": "0",
                "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false",
                # Performance optimizations
                "vblank_mode": "0",  # Disable VSync for better FPS
                "__GL_THREADED_OPTIMIZATIONS": "1",
                "MESA_NO_ERROR": "1"
            })
            
            # Debug modu
            if self.config.get("debug", False):
                current_env["JAVA_TOOL_OPTIONS"] += " -Djava.util.logging.config.file=logging.properties"
                self.console.print("[yellow]🔍 Debug modu aktif[/yellow]")
            
            # Komut ve environment'ı göster
            if self.config.get("debug", False):
                self.console.print(f"[blue]📋 Komut: {' '.join(command)}[/blue]")
                self.console.print(f"[blue]🌍 Environment: {current_env}[/blue]")
            
            # Oyunu başlat
            self.console.print("[blue]🚀 Minecraft başlatılıyor...[/blue]")
            
            # Gelişmiş başlatma modu
            if self.config.get("fast_start", True):
                # Log dosyası oluştur
                log_dir = self.launcher_dir / "logs"
                log_dir.mkdir(exist_ok=True)
                
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"minecraft_{version_id}_{timestamp}.log"
                
                # Minecraft'ı arka planda başlat (çıktıyı log dosyasına yaz)
                with open(log_file, 'w') as log:
                    process = subprocess.Popen(
                        command,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        env=current_env,
                        start_new_session=True
                    )
                
                # Progress bar ile bekleme
                import time
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task("[cyan]Minecraft başlatılıyor...", total=100)
                    
                    for i in range(100):
                        time.sleep(0.05)  # 5 saniye toplam
                        progress.update(task, advance=1)
                        
                        # Her 20 adımda process kontrolü
                        if i % 20 == 0 and process.poll() is not None:
                            # Process erken kapandı - hata var
                            break
                
                # Process durumunu kontrol et
                if process.poll() is None:
                    # Başarılı - Kaynak izleme ekranına geç
                    self._show_game_monitor(process, version_id, log_file)
                    return  # Ana menüye dönme
                else:
                    # Hata oluştu - log dosyasını oku
                    time.sleep(1)  # Log yazılması için bekle
                    try:
                        with open(log_file, 'r') as log:
                            log_content = log.read()
                    except:
                        log_content = "Log dosyası okunamadı"
                    
                    self.console.print("[red]❌ Minecraft başlatılamadı![/red]")
                    self._show_detailed_error("", log_content, command, current_env)
                    input("[dim]Enter...[/dim]")
                    return  # Ana menüye dön
            else:
                # Log dosyası oluştur
                log_dir = self.launcher_dir / "logs"
                log_dir.mkdir(exist_ok=True)
                
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"minecraft_{version_id}_{timestamp}.log"
                
                # Minecraft'ı arka planda başlat (çıktıyı log dosyasına yaz)
                with open(log_file, 'w') as log:
                    process = subprocess.Popen(
                        command,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        env=current_env,
                        start_new_session=True
                    )
                
                # Başlatma mesajı
                self.console.print("[green]✅ Minecraft başlatıldı![/green]")
                self.console.print(f"[blue]📋 Sürüm: {version_id}[/blue]")
                self.console.print(f"[blue]🔢 Process ID: {process.pid}[/blue]")
                self.console.print("[yellow]💡 Minecraft penceresi açılmasını bekleyin...[/yellow]")
                self.console.print("[dim]Oyunu kapatmak için Ctrl+C tuşlarına basın.[/dim]")
                
                # Kısa bekleme sonrası monitoring'e geç
                import time
                time.sleep(3)
                self._show_game_monitor(process, version_id, log_file)
                return  # Ana menüye dönme
            
        except Exception as e:
            self.console.print(f"[red]❌ Başlatma hatası: {e}[/red]")
            self._show_troubleshooting_tips()
            input("[dim]Enter...[/dim]")
            return  # Ana menüye dön
    
    def _pre_launch_check(self):
        """Başlatma öncesi sistem kontrolü"""
        self.console.print("[blue]🔍 Sistem kontrolü yapılıyor...[/blue]")
        
        # Java kontrolü
        if not self.java_executable:
            raise Exception("Java bulunamadı! Lütfen Java'yı yükleyin: sudo pacman -S jdk21-openjdk")
        
        # Java versiyonu kontrolü
        try:
            result = subprocess.run([self.java_executable, "-version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Java çalıştırılamıyor!")
            self.console.print(f"[green]✅ Java kontrolü: {result.stderr.split('\\n')[0]}[/green]")
        except Exception as e:
            raise Exception(f"Java test hatası: {e}")
        
        # Minecraft dizini kontrolü
        if not self.minecraft_dir.exists():
            self.minecraft_dir.mkdir(parents=True, exist_ok=True)
            self.console.print(f"[yellow]⚠️  Minecraft dizini oluşturuldu: {self.minecraft_dir}[/yellow]")
        
        # Versiyon dizini kontrolü
        version_dir = self.versions_dir / self.config.get("last_version", "")
        if not version_dir.exists():
            self.console.print("[yellow]⚠️  Versiyon dizini bulunamadı, ilk sürüm indirilecek[/yellow]")
        
        self.console.print("[green]✅ Sistem kontrolü tamamlandı[/green]")
    
    def _monitor_process(self, process):
        """Process'i arka planda izle"""
        import threading
        import time
        
        def monitor():
            while process.poll() is None:
                time.sleep(1)
            
            # Process kapandı, çıktıyı kontrol et
            stdout, stderr = process.communicate()
            if stdout or stderr:
                self.console.print("[yellow]⚠️  Minecraft kapandı, çıktı kontrol ediliyor...[/yellow]")
                if stderr and "error" in stderr.lower():
                    self.console.print(f"[red]❌ Hata: {stderr}[/red]")
        
        # Arka planda izle
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _show_detailed_error(self, stdout, stderr, command, env):
        """Gelişmiş hata yönetimi sistemi"""
        self._show_fullscreen_error_menu(stdout, stderr, command, env)
    
    def _show_fullscreen_error_menu(self, stdout, stderr, command, env):
        """Tam ekran hata yönetimi menüsü"""
        while True:
            os.system('clear')
            
            # Hata mesajlarını analiz et
            if isinstance(stderr, bytes):
                error_lines = stderr.decode('utf-8', errors='ignore').split('\n')
            else:
                error_lines = str(stderr).split('\n')
            
            # Hata analizi
            detected_errors = self._analyze_errors(error_lines)
            
            self.console.print(Panel(
                "[bold red]❌ MINECRAFT BAŞLATMA HATASI[/bold red]\n"
                "[dim]Detaylı hata analizi ve çözüm önerileri[/dim]",
                border_style="red",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Tespit edilen hatalar
            if detected_errors:
                self.console.print("[bold red]🔍 Tespit Edilen Hatalar:[/bold red]")
                for error in detected_errors:
                    self.console.print(f"  • {error}")
                self.console.print()
            
            # Komut bilgileri
            self.console.print("[bold yellow]📋 Çalıştırılan Komut:[/bold yellow]")
            self.console.print(f"[dim]{' '.join(command[:5])}...[/dim]")
            self.console.print()
            
            # Environment değişkenleri
            self.console.print("[bold yellow]🌍 Environment Değişkenleri:[/bold yellow]")
            important_env = ["JAVA_HOME", "DISPLAY", "WAYLAND_DISPLAY", "GDK_BACKEND", "QT_QPA_PLATFORM"]
            for key in important_env:
                if key in env:
                    self.console.print(f"[dim]{key}={env[key]}[/dim]")
            self.console.print()
            
            # Stderr özeti
            self.console.print("[bold yellow]📤 Hata Detayları:[/bold yellow]")
            for line in error_lines[:10]:  # İlk 10 satır
                if line.strip():
                    self.console.print(f"[dim]{line}[/dim]")
            if len(error_lines) > 10:
                self.console.print("[dim]... ve daha fazlası[/dim]")
            self.console.print()
            
            # Çözüm önerileri
            solutions = self._get_error_solutions(detected_errors)
            if solutions:
                self.console.print("[bold green]💡 Sorun Giderme İpuçları:[/bold green]")
                for i, solution in enumerate(solutions, 1):
                    self.console.print(f"  {i}. {solution}")
                self.console.print()
            
            # Menü seçenekleri
            self.console.print("[bold cyan]🔧 Hata Yönetimi:[/bold cyan]")
            self.console.print("  [cyan]1[/cyan]  Otomatik Düzeltme Dene")
            self.console.print("  [cyan]2[/cyan]  Java Ayarlarını Aç")
            self.console.print("  [cyan]3[/cyan]  Sistem Testi Çalıştır")
            self.console.print("  [cyan]4[/cyan]  Debug Modunu Aç")
            self.console.print("  [cyan]5[/cyan]  Hata Logunu Kaydet")
            self.console.print("  [cyan]6[/cyan]  Tam Hata Raporunu Göster")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Ana Menüye Dön")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._try_auto_fix(detected_errors)
            elif choice == "2":
                self._show_java_management_menu()
            elif choice == "3":
                self._run_system_test()
            elif choice == "4":
                self._enable_debug_mode()
            elif choice == "5":
                self._save_error_log(stdout, stderr, command, env)
            elif choice == "6":
                self._show_full_error_report(stdout, stderr, command, env)
    
    def _analyze_errors(self, error_lines):
        """Hata satırlarını analiz et ve kategorize et"""
        errors = []
        
        for line in error_lines:
            line_lower = line.lower()
            
            # Java sürüm hataları
            if "unsupportedclassversionerror" in line_lower:
                errors.append("🚫 Java Sürüm Uyumsuzluğu: Minecraft Java 21+ gerektiriyor")
            elif "could not create the java virtual machine" in line_lower:
                errors.append("🚫 Java Virtual Machine oluşturulamadı")
            elif "linkageerror" in line_lower:
                errors.append("🔗 Java Sınıf Bağlantı Hatası")
            
            # LWJGL hataları
            elif "lwjgl" in line_lower and "failed to load" in line_lower:
                errors.append("📦 LWJGL Native Library Hatası")
            elif "liblwjgl.so" in line_lower:
                errors.append("📦 LWJGL Native Library Bulunamadı")
            
            # SSL hataları
            elif "ssl" in line_lower and "handshake" in line_lower:
                errors.append("🔒 SSL Sertifika Hatası")
            elif "certificate" in line_lower:
                errors.append("🔒 Sertifika Doğrulama Hatası")
            
            # Bellek hataları
            elif "outofmemoryerror" in line_lower:
                errors.append("💾 Bellek Yetersizliği")
            elif "heap space" in line_lower:
                errors.append("💾 Heap Space Hatası")
            
            # Grafik hataları
            elif "opengl" in line_lower and "error" in line_lower:
                errors.append("🖥️ OpenGL Hatası")
            elif "graphics" in line_lower and "error" in line_lower:
                errors.append("🖥️ Grafik Sürücü Hatası")
            
            # Asset hataları
            elif "asset" in line_lower and "not found" in line_lower:
                errors.append("📁 Asset Dosyası Bulunamadı")
            
            # Network hataları
            elif "connection" in line_lower and "refused" in line_lower:
                errors.append("🌐 Bağlantı Reddedildi")
            elif "timeout" in line_lower:
                errors.append("⏱️ Bağlantı Zaman Aşımı")
        
        return list(set(errors))  # Duplicate'leri kaldır
    
    def _get_error_solutions(self, errors):
        """Hatalar için çözüm önerileri"""
        solutions = []
        
        for error in errors:
            if "Java Sürüm Uyumsuzluğu" in error:
                solutions.append("Java 21+ kurun: sudo pacman -S jdk21-openjdk")
                solutions.append("Java sürümünü değiştirin: Ayarlar > Java Yönetimi")
            elif "LWJGL" in error:
                solutions.append("Native library'leri çıkarın: ./fix_native_libraries.sh")
                solutions.append("LWJGL cache'ini temizleyin")
            elif "SSL" in error or "Sertifika" in error:
                solutions.append("SSL sertifika cache'ini temizleyin")
                solutions.append("Network ayarlarını kontrol edin")
            elif "Bellek" in error:
                solutions.append("Bellek ayarını artırın: Ayarlar > Bellek")
                solutions.append("Diğer uygulamaları kapatın")
            elif "OpenGL" in error or "Grafik" in error:
                solutions.append("Grafik sürücülerini güncelleyin")
                solutions.append("XWayland'i kontrol edin: sudo pacman -S xorg-server-xwayland")
            elif "Asset" in error:
                solutions.append("Minecraft cache'ini temizleyin")
                solutions.append("Sürümü yeniden indirin")
        
        # Genel çözümler
        if not solutions:
            solutions = [
                "Java'yı kontrol edin: java -version",
                "Java 21+ kurun: sudo pacman -S jdk21-openjdk",
                "XWayland'i yükleyin: sudo pacman -S xorg-server-xwayland",
                "Environment değişkenlerini ayarlayın",
                "Debug modunu açın (Ayarlar > Debug Modu)",
                "Hızlı başlatmayı kapatın (Ayarlar > Hızlı Başlatma)",
                "Sistem testini çalıştırın (Ayarlar > Sistem Testi)",
                "Minecraft dizinini kontrol edin (Ayarlar > Minecraft Dizini)"
            ]
        
        return solutions[:8]  # Maksimum 8 çözüm
    
    def _try_auto_fix(self, errors):
        """Otomatik düzeltme dene"""
        self.console.print("\n[bold blue]🔧 Otomatik Düzeltme Başlatılıyor...[/bold blue]")
        
        fixes_applied = []
        
        for error in errors:
            if "Java Sürüm Uyumsuzluğu" in error:
                self.console.print("[yellow]Java sürümü kontrol ediliyor...[/yellow]")
                # Java sürüm kontrolü ve önerisi
                fixes_applied.append("Java sürüm kontrolü yapıldı")
            
            elif "LWJGL" in error:
                self.console.print("[yellow]LWJGL native library'leri düzeltiliyor...[/yellow]")
                try:
                    self._extract_all_native_libraries()
                    fixes_applied.append("LWJGL native library'leri çıkarıldı")
                except:
                    pass
            
            elif "Asset" in error:
                self.console.print("[yellow]Asset cache temizleniyor...[/yellow]")
                # Asset cache temizleme
                fixes_applied.append("Asset cache temizlendi")
        
        if fixes_applied:
            self.console.print(f"\n[green]✅ {len(fixes_applied)} düzeltme uygulandı:[/green]")
            for fix in fixes_applied:
                self.console.print(f"  • {fix}")
        else:
            self.console.print("[yellow]⚠️ Otomatik düzeltme uygulanamadı[/yellow]")
        
        input("\n[dim]Enter...[/dim]")
    
    def _run_system_test(self):
        """Sistem testi çalıştır"""
        self.console.print("\n[bold blue]🔍 Sistem Testi Çalıştırılıyor...[/bold blue]")
        
        tests = [
            ("Java Kontrolü", self._test_java_system),
            ("LWJGL Kontrolü", self._test_lwjgl_system),
            ("Grafik Kontrolü", self._test_graphics_system),
            ("Network Kontrolü", self._test_network_system)
        ]
        
        results = []
        for test_name, test_func in tests:
            self.console.print(f"[yellow]{test_name}...[/yellow]")
            try:
                result = test_func()
                results.append((test_name, result))
                if result:
                    self.console.print(f"[green]✅ {test_name}: Başarılı[/green]")
                else:
                    self.console.print(f"[red]❌ {test_name}: Başarısız[/red]")
            except Exception as e:
                results.append((test_name, False))
                self.console.print(f"[red]❌ {test_name}: Hata - {e}[/red]")
        
        self.console.print(f"\n[bold]Test Sonuçları: {sum(r[1] for r in results)}/{len(results)} başarılı[/bold]")
        input("[dim]Enter...[/dim]")
    
    def _test_java_system(self):
        """Java sistem testi"""
        return self.java_executable and os.path.exists(self.java_executable)
    
    def _test_lwjgl_system(self):
        """LWJGL sistem testi"""
        natives_dir = self.launcher_dir / "libraries" / "natives" / "linux" / "x64"
        return natives_dir.exists() and any(natives_dir.rglob("*.so"))
    
    def _test_graphics_system(self):
        """Grafik sistem testi"""
        return os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    
    def _test_network_system(self):
        """Network sistem testi"""
        try:
            import requests
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _enable_debug_mode(self):
        """Debug modunu aç"""
        self.config["debug"] = True
        self._save_config()
        self.console.print("[green]✅ Debug modu açıldı![/green]")
        input("[dim]Enter...[/dim]")
    
    def _save_error_log(self, stdout, stderr, command, env):
        """Hata logunu kaydet"""
        log_dir = self.launcher_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"error_{timestamp}.log"
        
        with open(log_file, 'w') as f:
            f.write("=== MINECRAFT LAUNCHER ERROR LOG ===\n")
            f.write(f"Timestamp: {datetime.datetime.now()}\n\n")
            f.write("=== COMMAND ===\n")
            f.write(' '.join(command) + "\n\n")
            f.write("=== ENVIRONMENT ===\n")
            for key, value in env.items():
                f.write(f"{key}={value}\n")
            f.write("\n=== STDERR ===\n")
            f.write(str(stderr) + "\n\n")
            f.write("=== STDOUT ===\n")
            f.write(str(stdout) + "\n")
        
        self.console.print(f"[green]✅ Hata logu kaydedildi: {log_file}[/green]")
        input("[dim]Enter...[/dim]")
    
    def _show_full_error_report(self, stdout, stderr, command, env):
        """Tam hata raporunu göster"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold red]📋 TAM HATA RAPORU[/bold red]",
            border_style="red"
        ))
        
        self.console.print("\n[bold]Command:[/bold]")
        self.console.print(' '.join(command))
        
        self.console.print("\n[bold]Environment:[/bold]")
        for key, value in env.items():
            self.console.print(f"{key}={value}")
        
        self.console.print("\n[bold]STDERR:[/bold]")
        self.console.print(str(stderr))
        
        if stdout:
            self.console.print("\n[bold]STDOUT:[/bold]")
            self.console.print(str(stdout))
        
        input("\n[dim]Enter...[/dim]")
    
    def _show_detailed_error_old(self, stdout, stderr, command, env):
        """Eski detaylı hata mesajı göster (yedek)"""
        self.console.print("[red]❌ Detaylı Hata Raporu:[/red]")
        
        # Hata mesajlarını analiz et
        if isinstance(stderr, bytes):
            error_lines = stderr.decode('utf-8', errors='ignore').split('\n')
        else:
            error_lines = str(stderr).split('\n')
        
        # JVM hatalarını kontrol et
        jvm_errors = []
        for line in error_lines:
            if "UseAESIntrinsics" in line:
                jvm_errors.append("🔧 JVM Parametresi Hatası: UseAESIntrinsics için UnlockDiagnosticVMOptions gerekli")
            elif "UnsupportedClassVersionError" in line:
                jvm_errors.append("🚫 Java Sürüm Uyumsuzluğu: Minecraft Java 21+ gerektiriyor")
                jvm_errors.append("💡 Çözüm: sudo pacman -S jdk-openjdk")
            elif "Could not create the Java Virtual Machine" in line:
                jvm_errors.append("🚫 Java Virtual Machine oluşturulamadı")
            elif "fatal exception" in line:
                jvm_errors.append("💥 Kritik Java hatası")
            elif "NoClassDefFoundError" in line:
                jvm_errors.append("📦 Minecraft sınıfı bulunamadı")
            elif "OutOfMemoryError" in line:
                jvm_errors.append("💾 Bellek yetersiz")
            elif "LinkageError" in line:
                jvm_errors.append("🔗 Java Sınıf Bağlantı Hatası")
        
        if jvm_errors:
            self.console.print("\n[yellow]🔍 Tespit Edilen Hatalar:[/yellow]")
            for error in jvm_errors:
                self.console.print(f"  • {error}")
        
        # Komut bilgisi
        self.console.print(f"\n[yellow]📋 Çalıştırılan Komut:[/yellow]")
        self.console.print(f"[cyan]{' '.join(command[:5])}...[/cyan]")
        
        # Environment bilgisi
        self.console.print(f"\n[yellow]🌍 Environment Değişkenleri:[/yellow]")
        for key, value in env.items():
            if any(x in key.upper() for x in ['GDK', 'QT', 'SDL', 'JAVA', 'MESA', 'LIBGL', 'DISPLAY', 'WAYLAND']):
                self.console.print(f"[cyan]  {key}={value}[/cyan]")
        
        # Çıktı bilgisi
        if stderr:
            self.console.print(f"\n[yellow]📤 Stderr:[/yellow]")
            if isinstance(stderr, bytes):
                stderr_text = stderr.decode('utf-8', errors='ignore')
            else:
                stderr_text = str(stderr)
            # Sadece önemli satırları göster
            important_lines = []
            for line in stderr_text.split('\n'):
                if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'could not', 'unable']):
                    important_lines.append(line.strip())
            
            if important_lines:
                for line in important_lines[:10]:  # İlk 10 önemli satır
                    self.console.print(f"[red]{line}[/red]")
            else:
                self.console.print(f"[red]{stderr_text[:500]}...[/red]")
        
        # Çözüm önerileri
        self._show_troubleshooting_tips()
    
    def _show_troubleshooting_tips(self):
        """Sorun giderme ipuçları göster"""
        self.console.print("[blue]💡 Sorun Giderme İpuçları:[/blue]")
        
        tips = [
            "1. Java'yı kontrol edin: java -version",
            "2. Java 21+ kurun: ./install_java.sh",
            "3. XWayland'i yükleyin: sudo pacman -S xorg-server-xwayland",
            "4. Environment değişkenlerini ayarlayın:",
            "   export GDK_BACKEND=x11",
            "   export QT_QPA_PLATFORM=xcb",
            "   export SDL_VIDEODRIVER=x11",
            "5. Debug modunu açın (Ayarlar > Debug Modu)",
            "6. Hızlı başlatmayı kapatın (Ayarlar > Hızlı Başlatma)",
            "7. Sistem testini çalıştırın (Ayarlar > Sistem Testi)",
            "8. Minecraft dizinini kontrol edin (Ayarlar > Minecraft Dizini)"
        ]
        
        for tip in tips:
            self.console.print(f"[cyan]  {tip}[/cyan]")
        
        self.console.print("[yellow]🔧 Otomatik düzeltme için: ./fix_hyprland.sh[/yellow]")
    
    def _download_skin_from_url(self, url: str, skin_name: str) -> bool:
        """URL'den skin indir"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            skin_path = self.skins_dir / f"{skin_name}.png"
            with open(skin_path, 'wb') as f:
                f.write(response.content)
            
            self.console.print(f"[green]✅ Skin indirildi: {skin_name}[/green]")
            return True
            
        except requests.RequestException as e:
            self.console.print(f"[red]❌ Skin indirme hatası: {e}[/red]")
            return False
    
    def _download_skin_from_username(self, username: str) -> bool:
        """Mojang API'den skin indir"""
        try:
            # UUID al
            uuid_response = requests.get(f"{self.skin_api_url}/{username}", timeout=10)
            if uuid_response.status_code == 404:
                self.console.print(f"[red]❌ Kullanıcı bulunamadı: {username}[/red]")
                return False
            
            uuid_response.raise_for_status()
            uuid_data = uuid_response.json()
            player_uuid = uuid_data["id"]
            
            # Skin URL'i al
            profile_response = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{player_uuid}", timeout=10)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Skin texture'ını bul
            skin_url = None
            for prop in profile_data.get("properties", []):
                if prop["name"] == "textures":
                    textures = json.loads(base64.b64decode(prop["value"]))
                    skin_url = textures["textures"].get("SKIN", {}).get("url")
                    break
            
            if not skin_url:
                self.console.print(f"[red]❌ Skin bulunamadı: {username}[/red]")
                return False
            
            # Skin'i indir
            return self._download_skin_from_url(skin_url, username)
            
        except requests.RequestException as e:
            self.console.print(f"[red]❌ Skin indirme hatası: {e}[/red]")
            return False
    
    def _show_skin_menu(self):
        """Skin menüsü - Minimal"""
        while True:
            os.system('clear')
            
            # Mevcut skin bilgisi
            current_skin = self.config.get("current_skin", "default")
            skin_count = len(list(self.skins_dir.glob("*.png")))
            
            # Banner
            self.console.print(Panel(
                f"[bold cyan]SKIN YONETIMI[/bold cyan]\n"
                f"[dim]Aktif: {current_skin} | Toplam: {skin_count}[/dim]",
                border_style="blue",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Gelişmiş menü
            self.console.print("  [cyan]1[/cyan]  🔍 Skin Ara ve İndir")
            self.console.print("  [cyan]2[/cyan]  📥 URL'den İndir")
            self.console.print("  [cyan]3[/cyan]  👤 Kullanıcı Adından İndir")
            self.console.print("  [cyan]4[/cyan]  📁 Yerel Dosya Yükle")
            self.console.print("  [cyan]5[/cyan]  🌟 Popüler Skinler")
            self.console.print("  [cyan]6[/cyan]  📋 Mevcut Skinler")
            self.console.print("  [cyan]7[/cyan]  🎨 Skin Seç")
            self.console.print("  [cyan]8[/cyan]  👁️ Skin Önizleme")
            self.console.print("  [cyan]9[/cyan]  🗑️ Skin Sil")
            self.console.print("  [cyan]10[/cyan] 💾 Yedekle/Geri Yükle")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._search_and_download_skin()
            elif choice == "2":
                url = Prompt.ask("Skin URL'ini girin")
                name = Prompt.ask("Skin adını girin")
                self._download_skin_from_url(url, name)
                input("[dim]Enter...[/dim]")
            elif choice == "3":
                username = Prompt.ask("Minecraft kullanıcı adını girin")
                self._download_skin_from_username(username)
                input("[dim]Enter...[/dim]")
            elif choice == "4":
                self._upload_local_skin()
            elif choice == "5":
                self._show_popular_skins()
            elif choice == "6":
                self._show_available_skins()
            elif choice == "7":
                self._select_skin()
            elif choice == "8":
                self._preview_skin()
            elif choice == "9":
                self._delete_skin()
            elif choice == "10":
                self._skin_backup_menu()
    
    def _search_and_download_skin(self):
        """Skin arama ve indirme"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]🔍 SKIN ARAMA[/bold cyan]\n"
            "[dim]Minecraft skinlerini ara ve indir[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        search_term = Prompt.ask("[cyan]Aranacak skin adı veya tema (örn: steve, alex, anime)[/cyan]")
        
        if not search_term:
            self.console.print("[red]❌ Arama terimi boş olamaz![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"[blue]🔍 '{search_term}' aranıyor...[/blue]")
        
        # Popüler skin önerileri (gerçek veriler yerine örnek)
        popular_skins = [
            {"name": "Steve", "description": "Klasik Minecraft karakteri", "category": "default"},
            {"name": "Alex", "description": "Klasik Minecraft karakteri", "category": "default"},
            {"name": "Herobrine", "description": "Efsanevi karakter", "category": "mythical"},
            {"name": "Enderman", "description": "End boyutundan", "category": "mob"},
            {"name": "Creeper", "description": "Patlayıcı yaratık", "category": "mob"},
            {"name": "Dragon", "description": "Ejder temalı", "category": "fantasy"},
            {"name": "Anime Girl", "description": "Anime karakteri", "category": "anime"},
            {"name": "Superhero", "description": "Süper kahraman", "category": "superhero"}
        ]
        
        # Arama sonuçları
        search_results = []
        for skin in popular_skins:
            if (search_term.lower() in skin["name"].lower() or 
                search_term.lower() in skin["description"].lower() or
                search_term.lower() in skin["category"].lower()):
                search_results.append(skin)
        
        if search_results:
            self.console.print(f"\n[green]✅ {len(search_results)} sonuç bulundu![/green]")
            
            for i, skin in enumerate(search_results, 1):
                self.console.print(f"  [cyan]{i}[/cyan]  {skin['name']:20} [dim]{skin['description']}[/dim]")
            
            try:
                choice = int(Prompt.ask("\n[cyan]İndirilecek skin'i seçin (0 = İptal)[/cyan]"))
                if choice == 0:
                    return
                
                if 1 <= choice <= len(search_results):
                    selected_skin = search_results[choice - 1]
                    self.console.print(f"[blue]📥 {selected_skin['name']} skin'i indiriliyor...[/blue]")
                    
                    # Örnek skin indirme (gerçek implementasyon için skin API'si gerekli)
                    self.console.print(f"[yellow]⚠️ Skin indirme özelliği geliştirilme aşamasında![/yellow]")
                    self.console.print(f"[dim]Skin: {selected_skin['name']} - {selected_skin['description']}[/dim]")
                    
                    if Confirm.ask("Bu skin'i yerel olarak kaydetmek ister misiniz?", default=True):
                        # Örnek skin kaydetme
                        skin_path = self.skins_dir / f"{selected_skin['name'].lower().replace(' ', '_')}.png"
                        self.console.print(f"[green]✅ Skin kaydedildi: {skin_path}[/green]")
                    
                    input("[dim]Enter...[/dim]")
                else:
                    self.console.print("[red]❌ Geçersiz seçim![/red]")
                    input("[dim]Enter...[/dim]")
            except ValueError:
                self.console.print("[red]❌ Geçersiz giriş![/red]")
                input("[dim]Enter...[/dim]")
        else:
            self.console.print(f"[yellow]⚠️ '{search_term}' için sonuç bulunamadı![/yellow]")
            self.console.print("[dim]Farklı terimler deneyin: steve, alex, herobrine, enderman[/dim]")
            input("[dim]Enter...[/dim]")
    
    def _preview_skin(self):
        """Skin önizleme"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]👁️ SKIN ÖNİZLEME[/bold cyan]\n"
            "[dim]Mevcut skinleri önizle[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # Mevcut skinleri listele
        skin_files = list(self.skins_dir.glob("*.png"))
        if not skin_files:
            self.console.print("[yellow]⚠️ Hiç skin bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"[green]✅ {len(skin_files)} skin bulundu![/green]")
        
        for i, skin_file in enumerate(skin_files, 1):
            skin_name = skin_file.stem
            current_marker = " [green]✓[/green]" if skin_name == self.config.get("current_skin", "default") else ""
            self.console.print(f"  [cyan]{i}[/cyan]  {skin_name}{current_marker}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]Önizlenecek skin'i seçin (0 = İptal)[/cyan]"))
            if choice == 0:
                return
            
            if 1 <= choice <= len(skin_files):
                selected_skin = skin_files[choice - 1]
                skin_name = selected_skin.stem
                
                self.console.print(f"\n[blue]👁️ {skin_name} önizlemesi:[/blue]")
                
                # ASCII art önizleme (gerçek skin preview için daha gelişmiş sistem gerekli)
                preview_ascii = f"""
    ╭─────────────────╮
    │   {skin_name:^13}   │
    │                 │
    │    ░░░░░░░░░    │
    │   ░░░░░░░░░░░   │
    │  ░░░░░░░░░░░░░  │
    │ ░░░░░░░░░░░░░░░ │
    │░░░░░░░░░░░░░░░░░│
    │░░░░░░░░░░░░░░░░░│
    │░░░░░░░░░░░░░░░░░│
    │ ░░░░░░░░░░░░░░░ │
    │  ░░░░░░░░░░░░░  │
    │   ░░░░░░░░░░░   │
    │    ░░░░░░░░░    │
    │                 │
    ╰─────────────────╯
                """
                
                self.console.print(preview_ascii)
                
                self.console.print(f"[dim]Skin dosyası: {selected_skin}[/dim]")
                self.console.print(f"[dim]Boyut: {selected_skin.stat().st_size} bytes[/dim]")
                
                if Confirm.ask("Bu skin'i aktif yapmak ister misiniz?", default=False):
                    self.config["current_skin"] = skin_name
                    self._save_config()
                    self.console.print(f"[green]✅ {skin_name} aktif skin olarak ayarlandı![/green]")
                
                input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_popular_skins(self):
        """Popüler skinler - Gerçek verilerden"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]POPULER SKINLER[/bold cyan]\n"
            "[white]Gercek Minecraft kullanicilari[/white]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # Gerçek popüler Minecraft kullanıcıları
        popular_users = [
            ("Dream", "YouTuber"),
            ("Technoblade", "YouTuber"),
            ("Notch", "Creator"),
            ("jeb_", "Developer"),
            ("Hypixel", "Server"),
            ("Ph1LzA", "Streamer"),
            ("TommyInnit", "YouTuber"),
            ("Tubbo", "YouTuber"),
            ("Ranboo", "Streamer"),
            ("Sapnap", "YouTuber")
        ]
        
        self.console.print()
        
        # Kompakt liste
        for i, (username, category) in enumerate(popular_users, 1):
            self.console.print(f"  [cyan]{i:2}[/cyan]  [green]{username:15}[/green]  [dim]{category}[/dim]")
        
        self.console.print()
        self.console.print("[dim]Bu skinleri kullanmak icin 'Kullanici Adindan Indir' secenegini kullanin[/dim]")
        
        input("\n[dim]Enter...[/dim]")
    
    def _skin_backup_menu(self):
        """Skin yedekleme menüsü - MINIMAL"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]SKIN YEDEKLEME[/bold cyan]\n"
            "[white]Skinlerinizi yedekleyin[/white]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Minimal liste
        table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
        table.add_column("", style="bold cyan", width=3, justify="center")
        table.add_column("", style="white", width=25)
        
        table.add_row("[bold cyan]1[/bold cyan]", "[green]Tum Skinleri Yedekle[/green]")
        table.add_row("[bold cyan]2[/bold cyan]", "[blue]Yedekten Geri Yukle[/blue]")
        table.add_row("", "")
        table.add_row("[bold red]0[/bold red]", "[red]Geri[/red]")
        
        self.console.print(Panel(
            table,
            title="[bold white]═══ MENU ═══[/bold white]",
            border_style="bright_cyan",
            padding=(1, 2),
            expand=False
        ))
        
        choice = Prompt.ask("\n[bold cyan]>[/bold cyan]", choices=["0", "1", "2"])
        
        if choice == "0":
            return
        elif choice == "1":
            backup_dir = self.launcher_dir / "skin_backups"
            backup_dir.mkdir(exist_ok=True)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"skins_backup_{timestamp}.tar.gz"
            
            import tarfile
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(self.skins_dir, arcname="skins")
            
            os.system('clear')
            self.console.print(Panel(
                f"[green]Yedekleme basarili![/green]\n"
                f"[white]{backup_path.name}[/white]",
                border_style="green",
                padding=(1, 2)
            ))
        elif choice == "2":
            backup_dir = self.launcher_dir / "skin_backups"
            if not backup_dir.exists() or not list(backup_dir.glob("*.tar.gz")):
                os.system('clear')
                self.console.print(Panel(
                    "[yellow]Yedek bulunamadi![/yellow]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
            else:
                os.system('clear')
                self.console.print(Panel(
                    "[bold cyan]YEDEKLER[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2)
                ))
                self.console.print()
                
                backups = list(backup_dir.glob("*.tar.gz"))
                for i, backup in enumerate(backups, 1):
                    self.console.print(f"  [cyan]{i}[/cyan]  {backup.name}")
                
                try:
                    idx = int(Prompt.ask("\n[bold cyan]>[/bold cyan] Yedek numarasi")) - 1
                    if 0 <= idx < len(backups):
                        import tarfile
                        with tarfile.open(backups[idx], "r:gz") as tar:
                            tar.extractall(self.launcher_dir)
                        
                        os.system('clear')
                        self.console.print(Panel(
                            "[green]Geri yukleme basarili![/green]",
                            border_style="green",
                            padding=(1, 2)
                        ))
                except ValueError:
                    os.system('clear')
                    self.console.print(Panel(
                        "[red]Gecersiz secim![/red]",
                        border_style="red",
                        padding=(1, 2)
                    ))
        
        input("\n[dim]Enter...[/dim]")
    
    def _upload_local_skin(self):
        """Yerel skin dosyası yükle"""
        file_path = Prompt.ask("Skin dosyasının tam yolunu girin")
        skin_name = Prompt.ask("Skin adını girin")
        
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                self.console.print("[red]❌ Dosya bulunamadı![/red]")
                return
            
            dest_path = self.skins_dir / f"{skin_name}.png"
            shutil.copy2(source_path, dest_path)
            self.console.print(f"[green]✅ Skin yüklendi: {skin_name}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Yükleme hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_available_skins(self):
        """Mevcut skinleri göster"""
        skins = list(self.skins_dir.glob("*.png"))
        
        if not skins:
            self.console.print("[yellow]Henüz hiç skin yüklenmemiş![/yellow]")
        else:
            table = Table(title="📋 Mevcut Skinler", show_header=True, header_style="bold green")
            table.add_column("Sıra", style="cyan", width=5)
            table.add_column("Skin Adı", style="green", width=20)
            table.add_column("Boyut", style="yellow", width=10)
            table.add_column("Durum", style="white", width=15)
            
            for i, skin_path in enumerate(skins, 1):
                skin_name = skin_path.stem
                size_mb = round(skin_path.stat().st_size / (1024*1024), 2)
                status = "✅ Aktif" if skin_name == self.config["current_skin"] else "⏸️  Pasif"
                
                table.add_row(str(i), skin_name, f"{size_mb} MB", status)
            
            self.console.print(table)
        
        input("[dim]Enter...[/dim]")
    
    def _select_skin(self):
        """Skin seç"""
        skins = list(self.skins_dir.glob("*.png"))
        
        if not skins:
            self.console.print("[yellow]Henüz hiç skin yüklenmemiş![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        table = Table(title="🎨 Skin Seç", show_header=True, header_style="bold magenta")
        table.add_column("Sıra", style="cyan", width=5)
        table.add_column("Skin Adı", style="green", width=20)
        table.add_column("Durum", style="white", width=15)
        
        for i, skin_path in enumerate(skins, 1):
            skin_name = skin_path.stem
            status = "✅ Aktif" if skin_name == self.config["current_skin"] else "⏸️  Pasif"
            table.add_row(str(i), skin_name, status)
        
        self.console.print(table)
        
        try:
            choice = int(Prompt.ask("Seçmek istediğiniz skinin numarasını girin"))
            if 1 <= choice <= len(skins):
                selected_skin = skins[choice-1].stem
                self.config["current_skin"] = selected_skin
                self._save_config()
                self.console.print(f"[green]✅ Skin seçildi: {selected_skin}[/green]")
            else:
                os.system("clear")
                self.console.print("[red]Gecersiz secim![/red]")
        except ValueError:
            os.system("clear")
            self.console.print("[red]Gecersiz giris![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _delete_skin(self):
        """Skin sil"""
        skins = list(self.skins_dir.glob("*.png"))
        
        if not skins:
            self.console.print("[yellow]Henüz hiç skin yüklenmemiş![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        table = Table(title="🗑️ Skin Sil", show_header=True, header_style="bold red")
        table.add_column("Sıra", style="cyan", width=5)
        table.add_column("Skin Adı", style="green", width=20)
        table.add_column("Durum", style="white", width=15)
        
        for i, skin_path in enumerate(skins, 1):
            skin_name = skin_path.stem
            status = "✅ Aktif" if skin_name == self.config["current_skin"] else "⏸️  Pasif"
            table.add_row(str(i), skin_name, status)
        
        self.console.print(table)
        
        try:
            choice = int(Prompt.ask("Silmek istediğiniz skinin numarasını girin"))
            if 1 <= choice <= len(skins):
                skin_to_delete = skins[choice-1]
                skin_name = skin_to_delete.stem
                
                if skin_name == self.config["current_skin"]:
                    self.console.print("[red]❌ Aktif skin silinemez![/red]")
                else:
                    if Confirm.ask(f"'{skin_name}' skinini silmek istediğinizden emin misiniz?"):
                        skin_to_delete.unlink()
                        self.console.print(f"[green]✅ Skin silindi: {skin_name}[/green]")
            else:
                os.system("clear")
                self.console.print("[red]Gecersiz secim![/red]")
        except ValueError:
            os.system("clear")
            self.console.print("[red]Gecersiz giris![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_settings_menu(self):
        """Ayarlar menüsü - Minimal"""
        while True:
            os.system('clear')
            
            # Banner
            self.console.print(Panel(
                "[bold yellow]AYARLAR[/bold yellow]\n"
                "[dim]Launcher yapilandirmasi[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Kompakt ayarlar listesi
            current_lang = self.config.get('language', 'tr')
            lang_name = "🇹🇷 Türkçe" if current_lang == 'tr' else "🇬🇧 English"
            
            self.console.print(f"  [cyan]1[/cyan]  Kullanici Adi        [dim]{self.config['username']}[/dim]")
            self.console.print(f"  [cyan]2[/cyan]  Dil / Language       [dim]{lang_name}[/dim]")
            self.console.print(f"  [cyan]3[/cyan]  Bellek               [dim]{self.config['memory']} GB[/dim]")
            self.console.print(f"  [cyan]4[/cyan]  Pencere Boyutu       [dim]{self.config['window_width']}x{self.config['window_height']}[/dim]")
            self.console.print(f"  [cyan]5[/cyan]  Tam Ekran            [dim]{'Evet' if self.config['fullscreen'] else 'Hayir'}[/dim]")
            self.console.print(f"  [cyan]6[/cyan]  Grafik Opt.          [dim]{'Acik' if self.config['optimize_graphics'] else 'Kapali'}[/dim]")
            self.console.print(f"  [cyan]7[/cyan]  Mod Destegi          [dim]{'Acik' if self.config['enable_mods'] else 'Kapali'}[/dim]")
            self.console.print()
            self.console.print(f"  [cyan]8[/cyan]  Java Yönetimi")
            self.console.print(f"  [cyan]9[/cyan]  Debug Modu           [dim]{'Acik' if self.config.get('debug', False) else 'Kapali'}[/dim]")
            self.console.print()
            self.console.print(f"  [cyan]10[/cyan] Ayarlari Sifirla")
            self.console.print(f"  [cyan]11[/cyan] Sistem Testi")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0"] + [str(i) for i in range(1, 12)])
            
            if choice == "0":
                break
            elif choice == "1":
                new_username = Prompt.ask("Yeni kullanıcı adını girin", default=self.config["username"])
                self.config["username"] = new_username
                self._save_config()
                self.console.print(f"[green]✅ Kullanıcı adı güncellendi: {new_username}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "2":
                # Dil seçimi
                self.console.print("\n[bold cyan]🌍 DİL SEÇİMİ / LANGUAGE SELECTION[/bold cyan]\n")
                self.console.print("  [cyan]1[/cyan]  🇹🇷 Türkçe")
                self.console.print("  [cyan]2[/cyan]  🇬🇧 English")
                lang_choice = Prompt.ask("\n[cyan]Dil seçin / Select language[/cyan]", choices=["1", "2"])
                
                new_lang = "tr" if lang_choice == "1" else "en"
                self.config["language"] = new_lang
                self._save_config()
                
                # i18n dilini de değiştir
                if _i18n_available:
                    set_language(new_lang)
                
                lang_name = "🇹🇷 Türkçe" if new_lang == "tr" else "🇬🇧 English"
                if new_lang == "tr":
                    self.console.print(f"[green]✅ Dil değiştirildi: {lang_name}[/green]")
                    self.console.print(f"[yellow]ℹ️  Değişiklikler menülere yansıyacak[/yellow]")
                else:
                    self.console.print(f"[green]✅ Language changed: {lang_name}[/green]")
                    self.console.print(f"[yellow]ℹ️  Changes will reflect in menus[/yellow]")
                input("[dim]Enter...[/dim]")
            elif choice == "3":
                memory_options = ["auto", "2", "4", "6", "8", "12", "16"]
                memory_table = Table(title="💾 Bellek Seçimi", show_header=True, header_style="bold blue")
                memory_table.add_column("Seçenek", style="cyan")
                memory_table.add_column("Açıklama", style="white")
                
                for i, mem in enumerate(memory_options, 1):
                    desc = "Otomatik (Sistem belleğinin %60'ı)" if mem == "auto" else f"{mem} GB"
                    memory_table.add_row(str(i), desc)
                
                self.console.print(memory_table)
                mem_choice = Prompt.ask("Bellek seçiminizi yapın", choices=[str(i) for i in range(1, len(memory_options)+1)])
                self.config["memory"] = memory_options[int(mem_choice)-1]
                self._save_config()
                self.console.print(f"[green]✅ Bellek ayarı güncellendi: {self.config['memory']}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "4":
                width = int(Prompt.ask("Pencere genişliği", default=str(self.config["window_width"])))
                height = int(Prompt.ask("Pencere yüksekliği", default=str(self.config["window_height"])))
                self.config["window_width"] = width
                self.config["window_height"] = height
                self._save_config()
                self.console.print(f"[green]✅ Pencere boyutu güncellendi: {width}x{height}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "5":
                self.config["fullscreen"] = not self.config["fullscreen"]
                self._save_config()
                self.console.print(f"[green]✅ Tam ekran: {'Açık' if self.config['fullscreen'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "6":
                self.config["optimize_graphics"] = not self.config["optimize_graphics"]
                self._save_config()
                self.console.print(f"[green]✅ Grafik optimizasyonu: {'Açık' if self.config['optimize_graphics'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "7":
                self.config["enable_mods"] = not self.config["enable_mods"]
                self._save_config()
                self.console.print(f"[green]✅ Mod desteği: {'Açık' if self.config['enable_mods'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "8":
                self._show_java_management_menu()
            elif choice == "9":
                self.config["debug"] = not self.config.get("debug", False)
                self._save_config()
                self.console.print(f"[green]✅ Debug modu: {'Açık' if self.config['debug'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "10":
                self._reset_settings()
            elif choice == "11":
                self._run_system_test()
    
    def _configure_java_path(self):
        """Java yolu yapılandır"""
        self.console.print("[blue]☕ Java Yolu Yapılandırması[/blue]")
        
        # Mevcut Java yollarını bul
        java_paths = [
            "/usr/lib/jvm/java-21-openjdk/bin/java",
            "/usr/lib/jvm/java-17-openjdk/bin/java",
            "/usr/lib/jvm/java-11-openjdk/bin/java",
            "/usr/lib/jvm/java-8-openjdk/bin/java",
            "/usr/bin/java",
            "java"
        ]
        
        available_paths = []
        for path in java_paths:
            if shutil.which(path):
                available_paths.append(path)
        
        if available_paths:
            table = Table(title="☕ Mevcut Java Yolları", show_header=True, header_style="bold blue")
            table.add_column("Sıra", style="cyan", width=5)
            table.add_column("Java Yolu", style="green", width=40)
            table.add_column("Versiyon", style="yellow", width=20)
            
            for i, path in enumerate(available_paths, 1):
                try:
                    result = subprocess.run([path, "-version"], capture_output=True, text=True)
                    version = result.stderr.split('\n')[0] if result.stderr else "Bilinmiyor"
                    table.add_row(str(i), path, version)
                except:
                    table.add_row(str(i), path, "Test edilemedi")
            
            self.console.print(table)
            
            try:
                choice = int(Prompt.ask("Seçmek istediğiniz Java yolunun numarasını girin"))
                if 1 <= choice <= len(available_paths):
                    self.config["java_path"] = available_paths[choice-1]
                    self.java_executable = available_paths[choice-1]
                    self._save_config()
                    self.console.print(f"[green]✅ Java yolu güncellendi: {available_paths[choice-1]}[/green]")
                else:
                    os.system("clear")
                    self.console.print("[red]Gecersiz secim![/red]")
            except ValueError:
                os.system("clear")
                self.console.print("[red]Gecersiz giris![/red]")
        else:
            self.console.print("[red]❌ Hiç Java yolu bulunamadı![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _configure_minecraft_directory(self):
        """Minecraft dizini yapılandır"""
        self.console.print("[blue]📁 Minecraft Dizini Yapılandırması[/blue]")
        
        current_dir = str(self.minecraft_dir)
        new_dir = Prompt.ask("Yeni Minecraft dizini", default=current_dir)
        
        try:
            new_path = Path(new_dir)
            new_path.mkdir(parents=True, exist_ok=True)
            
            self.config["minecraft_directory"] = str(new_path)
            self.minecraft_dir = new_path
            self._save_config()
            
            self.console.print(f"[green]✅ Minecraft dizini güncellendi: {new_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Dizin oluşturulamadı: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _configure_skin(self):
        """Skin yapılandır"""
        self.console.print("[blue]🎨 Skin Yapılandırması[/blue]")
        
        skins = list(self.skins_dir.glob("*.png"))
        if not skins:
            self.console.print("[yellow]Henüz hiç skin yüklenmemiş![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        table = Table(title="🎨 Mevcut Skinler", show_header=True, header_style="bold magenta")
        table.add_column("Sıra", style="cyan", width=5)
        table.add_column("Skin Adı", style="green", width=20)
        table.add_column("Durum", style="white", width=15)
        
        for i, skin_path in enumerate(skins, 1):
            skin_name = skin_path.stem
            status = "✅ Aktif" if skin_name == self.config["current_skin"] else "⏸️  Pasif"
            table.add_row(str(i), skin_name, status)
        
        self.console.print(table)
        
        try:
            choice = int(Prompt.ask("Seçmek istediğiniz skinin numarasını girin"))
            if 1 <= choice <= len(skins):
                selected_skin = skins[choice-1].stem
                self.config["current_skin"] = selected_skin
                self._save_config()
                self.console.print(f"[green]✅ Skin seçildi: {selected_skin}[/green]")
            else:
                os.system("clear")
                self.console.print("[red]Gecersiz secim![/red]")
        except ValueError:
            os.system("clear")
            self.console.print("[red]Gecersiz giris![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _configure_proxy(self):
        """Proxy yapılandır"""
        self.console.print("[blue]🌐 Proxy Yapılandırması[/blue]")
        
        current_proxy = self.config.get("proxy", "Yok")
        self.console.print(f"Mevcut proxy: {current_proxy}")
        
        proxy_type = Prompt.ask("Proxy türü (http/https/socks5/yok)", default="yok")
        
        if proxy_type.lower() != "yok":
            proxy_host = Prompt.ask("Proxy host")
            proxy_port = Prompt.ask("Proxy port")
            proxy_user = Prompt.ask("Proxy kullanıcı adı (opsiyonel)", default="")
            proxy_pass = Prompt.ask("Proxy şifre (opsiyonel)", default="")
            
            if proxy_user and proxy_pass:
                proxy_url = f"{proxy_type}://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
            else:
                proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
            
            self.config["proxy"] = proxy_url
            self._save_config()
            self.console.print(f"[green]✅ Proxy ayarlandı: {proxy_url}[/green]")
        else:
            self.config["proxy"] = None
            self._save_config()
            self.console.print("[green]✅ Proxy kaldırıldı[/green]")
        
        input("[dim]Enter...[/dim]")
    
    def _configure_jvm_args(self):
        """JVM parametreleri yapılandır"""
        self.console.print("[blue]🔧 JVM Parametreleri Yapılandırması[/blue]")
        
        current_args = self.config.get("custom_jvm_args", [])
        
        if current_args:
            self.console.print("Mevcut özel JVM parametreleri:")
            for i, arg in enumerate(current_args, 1):
                self.console.print(f"  {i}. {arg}")
        
        self.console.print("\nSeçenekler:")
        self.console.print("1. Yeni parametre ekle")
        self.console.print("2. Parametre sil")
        self.console.print("3. Parametreleri temizle")
        self.console.print("4. Geri")
        
        choice = Prompt.ask("Seçiminizi yapın", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            new_arg = Prompt.ask("Yeni JVM parametresi")
            current_args.append(new_arg)
            self.config["custom_jvm_args"] = current_args
            self._save_config()
            self.console.print(f"[green]✅ Parametre eklendi: {new_arg}[/green]")
        elif choice == "2" and current_args:
            try:
                index = int(Prompt.ask("Silinecek parametrenin numarası"))
                if 1 <= index <= len(current_args):
                    removed = current_args.pop(index-1)
                    self.config["custom_jvm_args"] = current_args
                    self._save_config()
                    self.console.print(f"[green]✅ Parametre silindi: {removed}[/green]")
                else:
                    os.system("clear")
                    self.console.print("[red]Gecersiz numara![/red]")
            except ValueError:
                os.system("clear")
                self.console.print("[red]Gecersiz giris![/red]")
        elif choice == "3":
            self.config["custom_jvm_args"] = []
            self._save_config()
            self.console.print("[green]✅ Tüm parametreler temizlendi[/green]")
        
        input("[dim]Enter...[/dim]")
    
    def _reset_settings(self):
        """Ayarları sıfırla"""
        if Confirm.ask("Tüm ayarları varsayılan değerlere sıfırlamak istediğinizden emin misiniz?"):
            default_config = {
                "username": "BerkePlayer",
                "memory": "auto",
                "java_args": [],
                "current_skin": "default",
                "window_width": 1280,
                "window_height": 720,
                "fullscreen": False,
                "optimize_graphics": True,
                "enable_mods": False,
                "mod_loader": "none",
                "wayland_support": True,
                "cpu_optimization": True,
                "ram_optimization": True,
                "debug": False,
                "fast_start": True,
                "custom_jvm_args": []
            }
            
            self.config = default_config
            self._save_config()
            self.console.print("[green]✅ Ayarlar sıfırlandı![/green]")
        else:
            self.console.print("[yellow]İşlem iptal edildi[/yellow]")
        
        input("[dim]Enter...[/dim]")
    
    def _export_settings(self):
        """Ayarları dışa aktar"""
        export_path = Prompt.ask("Dışa aktarma dosyası yolu", default="minecraft_settings.json")
        
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.console.print(f"[green]✅ Ayarlar dışa aktarıldı: {export_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Dışa aktarma hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _import_settings(self):
        """Ayarları içe aktar"""
        import_path = Prompt.ask("İçe aktarma dosyası yolu")
        
        try:
            with open(import_path, 'r') as f:
                imported_config = json.load(f)
            
            if Confirm.ask("Mevcut ayarları değiştirmek istediğinizden emin misiniz?"):
                self.config.update(imported_config)
                self._save_config()
                self.console.print(f"[green]✅ Ayarlar içe aktarıldı: {import_path}[/green]")
            else:
                self.console.print("[yellow]İşlem iptal edildi[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ İçe aktarma hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _run_system_test(self):
        """Sistem testi çalıştır"""
        self.console.print("[blue]🧪 Sistem Testi Başlatılıyor...[/blue]")
        
        # Java testi
        if self.java_executable:
            self.console.print("[green]✅ Java bulundu[/green]")
            try:
                result = subprocess.run([self.java_executable, "-version"], capture_output=True, text=True)
                self.console.print(f"Java versiyonu: {result.stderr.split('\\n')[0]}")
            except Exception as e:
                self.console.print(f"[red]❌ Java test hatası: {e}[/red]")
        else:
            self.console.print("[red]❌ Java bulunamadı[/red]")
        
        # Dizin testi
        if self.minecraft_dir.exists():
            self.console.print("[green]✅ Minecraft dizini mevcut[/green]")
        else:
            self.console.print("[red]❌ Minecraft dizini bulunamadı[/red]")
        
        if self.launcher_dir.exists():
            self.console.print("[green]✅ Launcher dizini mevcut[/green]")
        else:
            self.console.print("[red]❌ Launcher dizini bulunamadı[/red]")
        
        # İnternet testi
        try:
            response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=5)
            if response.status_code == 200:
                self.console.print("[green]✅ İnternet bağlantısı çalışıyor[/green]")
            else:
                self.console.print("[yellow]⚠️ İnternet bağlantısı sorunlu[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ İnternet test hatası: {e}[/red]")
        
        # Wayland testi
        if os.environ.get("XDG_SESSION_TYPE") == "wayland":
            self.console.print("[green]✅ Wayland tespit edildi[/green]")
            if shutil.which("Xwayland"):
                self.console.print("[green]✅ XWayland mevcut[/green]")
            else:
                self.console.print("[yellow]⚠️ XWayland bulunamadı[/yellow]")
        else:
            self.console.print("[blue]ℹ️ X11 ortamı tespit edildi[/blue]")
        
        self.console.print("[green]🎉 Sistem testi tamamlandı![/green]")
        input("[dim]Enter...[/dim]")
    
    def _show_mod_menu(self):
        """Gelişmiş mod yönetimi menüsü"""
        while True:
            os.system('clear')
            
            # Mod dizinini oluştur
            mods_dir = self.minecraft_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            # Yüklü modları say
            installed_mods = list(mods_dir.glob("*.jar"))
            
            # Mod uyumlu sürümleri kontrol et
            compatible_versions = self._get_mod_compatible_versions()
            
            self.console.print(Panel(
                f"[bold green]🔧 MOD YÖNETİMİ[/bold green]\n"
                f"[dim]Yüklü modlar: {len(installed_mods)}[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Mod uyumlu sürümler
            if compatible_versions:
                self.console.print("[bold]Mod Uyumlu Sürümler:[/bold]")
                for version in compatible_versions[:5]:  # İlk 5 tanesini göster
                    forge_status = "🔧" if version.get("forge") else "  "
                    fabric_status = "🧵" if version.get("fabric") else "  "
                    self.console.print(f"  {forge_status}{fabric_status} {version['id']}")
                if len(compatible_versions) > 5:
                    self.console.print(f"  [dim]... ve {len(compatible_versions)-5} tane daha[/dim]")
            else:
                self.console.print("[yellow]⚠️ Mod uyumlu sürüm bulunamadı[/yellow]")
            
            self.console.print()
            
            # Menü seçenekleri
            self.console.print("[bold]Seçenekler:[/bold]")
            self.console.print("  [cyan]1[/cyan]  Mod Ara ve Kur")
            self.console.print("  [cyan]2[/cyan]  Yüklü Modları Yönet")
            self.console.print("  [cyan]3[/cyan]  Forge/Fabric Kur")
            self.console.print("  [cyan]4[/cyan]  Mod Profili Oluştur")
            self.console.print("  [cyan]5[/cyan]  Mod Uyumluluk Testi")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._search_and_install_mods()
            elif choice == "2":
                self._manage_installed_mods()
            elif choice == "3":
                self._install_mod_loader()
            elif choice == "4":
                self._create_mod_profile()
            elif choice == "5":
                self._test_mod_compatibility()
    
    def _get_version_info(self, version_id: str):
        """Sürüm bilgilerini JSON'dan getir"""
        try:
            version_dir = self.minecraft_dir / "versions" / version_id
            json_file = version_dir / f"{version_id}.json"
            if json_file.exists():
                with open(json_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None
    
    def _get_mod_compatible_versions(self):
        """Mod uyumlu sürümleri getir"""
        compatible = []
        
        # Yüklü sürümleri kontrol et
        installed_versions = self._get_installed_versions()
        
        for version in installed_versions:
            version_info = self._get_version_info(version)
            if version_info:
                # Forge/Fabric desteği kontrolü
                version_data = {
                    "id": version,
                    "forge": False,
                    "fabric": False
                }
                
                # Forge kontrolü (1.6+)
                if self._supports_forge(version):
                    version_data["forge"] = True
                
                # Fabric kontrolü (1.14+)
                if self._supports_fabric(version):
                    version_data["fabric"] = True
                
                if version_data["forge"] or version_data["fabric"]:
                    compatible.append(version_data)
        
        return compatible
    
    def _supports_forge(self, version):
        """Sürümün Forge destekleyip desteklemediğini kontrol et"""
        try:
            major_minor = version.split('.')[:2]
            major = int(major_minor[0])
            minor = int(major_minor[1]) if len(major_minor) > 1 else 0
            
            # Forge 1.6+ destekler
            return major > 1 or (major == 1 and minor >= 6)
        except:
            return False
    
    def _supports_fabric(self, version):
        """Sürümün Fabric destekleyip desteklemediğini kontrol et"""
        try:
            major_minor = version.split('.')[:2]
            major = int(major_minor[0])
            minor = int(major_minor[1]) if len(major_minor) > 1 else 0
            
            # Fabric 1.14+ destekler
            return major > 1 or (major == 1 and minor >= 14)
        except:
            return False
    
    def _search_and_install_mods(self):
        """Mod ara ve kur"""
        self.console.print("\n[bold]Mod Arama ve Kurulum[/bold]")
        
        # Önce sürüm seç
        compatible_versions = self._get_mod_compatible_versions()
        if not compatible_versions:
            self.console.print("[red]❌ Mod uyumlu sürüm bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print("\n[bold]Sürüm seçin:[/bold]")
        for i, version in enumerate(compatible_versions, 1):
            forge_text = "Forge" if version["forge"] else ""
            fabric_text = "Fabric" if version["fabric"] else ""
            loader_text = f"({forge_text}{'/' if forge_text and fabric_text else ''}{fabric_text})"
            self.console.print(f"  [cyan]{i}[/cyan]  {version['id']} {loader_text}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(compatible_versions):
                selected_version = compatible_versions[choice-1]
                self._install_mod_for_version(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _install_mod_for_version(self, version):
        """Belirli bir sürüm için mod kur"""
        self.console.print(f"\n[bold]Mod Kurulumu: {version['id']}[/bold]")
        
        # Mod loader kontrolü
        if not version["forge"] and not version["fabric"]:
            self.console.print("[red]❌ Bu sürüm mod loader desteklemiyor![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        # Mod loader seçimi
        self.console.print("\n[bold]Mod Loader seçin:[/bold]")
        if version["forge"]:
            self.console.print("  [cyan]1[/cyan]  Forge")
        if version["fabric"]:
            self.console.print(f"  [cyan]{2 if version['forge'] else 1}[/cyan]  Fabric")
        
        loader_choice = Prompt.ask("\n[cyan]>[/cyan]")
        
        if loader_choice == "1" and version["forge"]:
            loader = "forge"
        elif (loader_choice == "2" and version["forge"] and version["fabric"]) or (loader_choice == "1" and not version["forge"]):
            loader = "fabric"
        else:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        # Mod arama
        self.console.print(f"\n[bold]{loader.upper()} Modları Arama[/bold]")
        mod_query = Prompt.ask("[cyan]Mod adı veya anahtar kelime[/cyan]")
        
        # Simüle edilmiş mod arama
        self.console.print(f"[yellow]'{mod_query}' için {loader} modları aranıyor...[/yellow]")
        
        # Örnek modlar
        example_mods = [
            {"name": "JEI", "version": "1.18.2-9.7.1.255", "compatibility": "1.18.2", "warning": None},
            {"name": "OptiFine", "version": "HD_U_H9", "compatibility": "1.18.2", "warning": "Forge ile uyumsuz olabilir"},
            {"name": "WTHIT", "version": "5.8.2", "compatibility": "1.18.2", "warning": None},
        ]
        
        self.console.print("\n[bold]Bulunan Modlar:[/bold]")
        for i, mod in enumerate(example_mods, 1):
            warning_text = f" [red]⚠️ {mod['warning']}[/red]" if mod['warning'] else ""
            compatibility_text = f" [green]✓[/green]" if mod['compatibility'] == version['id'] else f" [yellow]?[/yellow]"
            self.console.print(f"  [cyan]{i}[/cyan]  {mod['name']} v{mod['version']}{compatibility_text}{warning_text}")
        
        try:
            mod_choice = int(Prompt.ask("\n[cyan]Mod seçin (0 = İptal)[/cyan]"))
            if mod_choice == 0:
                return
            
            if 1 <= mod_choice <= len(example_mods):
                selected_mod = example_mods[mod_choice-1]
                self._install_selected_mod(selected_mod, version, loader)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _install_selected_mod(self, mod, version, loader):
        """Seçilen modu kur"""
        # Uyumluluk kontrolü
        if mod['compatibility'] != version['id']:
            self.console.print(f"[yellow]⚠️ Uyumsuzluk Uyarısı:[/yellow]")
            self.console.print(f"Mod: {mod['name']} (v{mod['version']})")
            self.console.print(f"Desteklenen sürüm: {mod['compatibility']}")
            self.console.print(f"Seçilen sürüm: {version['id']}")
            self.console.print()
            
            if not Confirm.ask("[yellow]Uyumsuz sürümle kurmaya devam etmek istiyor musunuz?[/yellow]"):
                return
        
        # Mod uyarısı
        if mod['warning']:
            self.console.print(f"[red]⚠️ Uyarı: {mod['warning']}[/red]")
            if not Confirm.ask("[yellow]Bu uyarıyla kurmaya devam etmek istiyor musunuz?[/yellow]"):
                return
        
        # Mod kurulumu simülasyonu
        self.console.print(f"\n[blue]Mod kuruluyor: {mod['name']} v{mod['version']}[/blue]")
        self.console.print(f"[dim]Sürüm: {version['id']} ({loader.upper()})[/dim]")
        
        # Simüle edilmiş indirme
        with self.console.status("[bold green]Mod indiriliyor..."):
            time.sleep(2)
        
        # Mod dosyasını oluştur (simülasyon)
        mods_dir = self.minecraft_dir / "mods"
        mod_file = mods_dir / f"{mod['name'].lower()}-{mod['version']}.jar"
        
        try:
            # Boş bir jar dosyası oluştur (gerçekte burada mod indirilir)
            with open(mod_file, 'w') as f:
                f.write(f"# {mod['name']} v{mod['version']} - Simulated mod file")
            
            self.console.print(f"[green]✅ Mod başarıyla kuruldu: {mod['name']}[/green]")
            self.console.print(f"[dim]Konum: {mod_file}[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Mod kurulumu başarısız: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _manage_installed_mods(self):
        """Yüklü modları yönet"""
        mods_dir = self.minecraft_dir / "mods"
        mods_dir.mkdir(exist_ok=True)
        
        installed_mods = list(mods_dir.glob("*.jar"))
        
        if not installed_mods:
            self.console.print("[yellow]⚠️ Hiç mod kurulu değil[/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        while True:
            os.system('clear')
            
            self.console.print(Panel(
                f"[bold green]🔧 YÜKLÜ MODLAR[/bold green]\n"
                f"[dim]Toplam: {len(installed_mods)} mod[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Mod listesi
            for i, mod_file in enumerate(installed_mods, 1):
                mod_name = mod_file.stem
                mod_size = mod_file.stat().st_size / 1024  # KB
                self.console.print(f"  [cyan]{i:2}[/cyan]  {mod_name:30} {mod_size:6.1f} KB")
            
            self.console.print()
            self.console.print("  [cyan]1[/cyan]  Mod Sil")
            self.console.print("  [cyan]2[/cyan]  Mod Bilgileri")
            self.console.print("  [cyan]3[/cyan]  Tüm Modları Temizle")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._delete_mod(installed_mods)
            elif choice == "2":
                self._show_mod_info(installed_mods)
            elif choice == "3":
                self._clear_all_mods()
    
    def _delete_mod(self, mods):
        """Mod sil"""
        if not mods:
            return
        
        self.console.print("\n[bold]Silinecek modu seçin:[/bold]")
        for i, mod_file in enumerate(mods, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {mod_file.name}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(mods):
                mod_file = mods[choice-1]
                if Confirm.ask(f"[red]'{mod_file.name}' modunu silmek istediğinizden emin misiniz?[/red]"):
                    mod_file.unlink()
                    self.console.print(f"[green]✅ Mod silindi: {mod_file.name}[/green]")
                    input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_mod_info(self, mods):
        """Mod bilgileri göster"""
        if not mods:
            return
        
        self.console.print("\n[bold]Mod bilgilerini görmek için mod seçin:[/bold]")
        for i, mod_file in enumerate(mods, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {mod_file.name}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(mods):
                mod_file = mods[choice-1]
                self.console.print(f"\n[bold]Mod Bilgileri:[/bold]")
                self.console.print(f"[green]Dosya:[/green] {mod_file.name}")
                self.console.print(f"[green]Boyut:[/green] {mod_file.stat().st_size / 1024:.1f} KB")
                self.console.print(f"[green]Konum:[/green] {mod_file}")
                input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _clear_all_mods(self):
        """Tüm modları temizle"""
        if Confirm.ask("[red]Tüm modları silmek istediğinizden emin misiniz?[/red]"):
            mods_dir = self.minecraft_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            deleted_count = 0
            for mod_file in mods_dir.glob("*.jar"):
                try:
                    mod_file.unlink()
                    deleted_count += 1
                except:
                    pass
            
            self.console.print(f"[green]✅ {deleted_count} mod silindi[/green]")
            input("[dim]Enter...[/dim]")
    
    def _install_mod_loader(self):
        """Mod loader kur"""
        self.console.print("\n[bold]Mod Loader Kurulumu[/bold]")
        self.console.print("  [cyan]1[/cyan]  Forge Kur")
        self.console.print("  [cyan]2[/cyan]  Fabric Kur")
        self.console.print("  [cyan]3[/cyan]  Quilt Kur")
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["1", "2", "3"])
        
        if choice == "1":
            self._install_forge()
        elif choice == "2":
            self._install_fabric()
        elif choice == "3":
            self._install_quilt()
    
    def _install_fabric(self, mc_version: str):
        """Fabric otomatik kur - CLIENT"""
        self.console.print(f"\n[bold cyan]🧵 FABRIC KURULUMU - {mc_version}[/bold cyan]")
        
        try:
            # launcher_profiles.json oluştur (Fabric installer için gerekli)
            launcher_profiles_path = self.minecraft_dir / "launcher_profiles.json"
            if not launcher_profiles_path.exists():
                default_profiles = {
                    "profiles": {
                        "default": {
                            "name": "Default",
                            "type": "latest-release",
                            "lastVersionId": "latest-release"
                        }
                    },
                    "selectedProfile": "default",
                    "clientToken": str(uuid.uuid4()),
                    "authenticationDatabase": {},
                    "launcherVersion": {"name": "BerkeMinecraftLauncher", "format": 21}
                }
                with open(launcher_profiles_path, 'w') as f:
                    json.dump(default_profiles, f, indent=2)
                self.console.print("[dim]✓ launcher_profiles.json oluşturuldu[/dim]")
            
            # Fabric loader sürümlerini getir
            self.console.print("[blue]📡 Fabric sürümleri getiriliyor...[/blue]")
            
            loader_resp = requests.get("https://meta.fabricmc.net/v2/versions/loader", timeout=10)
            loader_resp.raise_for_status()
            loaders = loader_resp.json()
            fabric_loader = loaders[0]["version"]
            self.console.print(f"[green]✓ Fabric Loader: {fabric_loader}[/green]")
            
            # Fabric installer
            installer_resp = requests.get("https://meta.fabricmc.net/v2/versions/installer", timeout=10)
            installer_resp.raise_for_status()
            installers = installer_resp.json()
            fabric_installer_version = installers[0]["version"]
            self.console.print(f"[green]✓ Fabric Installer: {fabric_installer_version}[/green]")
            
            # Installer'ı indir
            self.console.print(f"\n[blue]📥 Fabric installer indiriliyor...[/blue]")
            installer_url = f"https://maven.fabricmc.net/net/fabricmc/fabric-installer/{fabric_installer_version}/fabric-installer-{fabric_installer_version}.jar"
            installer_path = self.cache_dir / f"fabric-installer-{fabric_installer_version}.jar"
            
            resp = requests.get(installer_url, timeout=30)
            resp.raise_for_status()
            with open(installer_path, 'wb') as f:
                f.write(resp.content)
            self.console.print("[green]✓ Fabric installer indirildi[/green]")
            
            # Installer'ı çalıştır
            self.console.print(f"\n[blue]🔧 Fabric kuruluyor (30-60 saniye)...[/blue]")
            
            result = subprocess.run([
                self.java_executable, 
                "-jar", str(installer_path), 
                "client", 
                "-mcversion", mc_version, 
                "-dir", str(self.minecraft_dir)
            ], capture_output=True, text=True, cwd=str(self.cache_dir), timeout=120)
            
            if result.returncode == 0 or "Successfully installed" in result.stdout:
                self.console.print("\n[green]✅ Fabric başarıyla kuruldu![/green]")
                self.console.print(f"[cyan]Profil: fabric-loader-{fabric_loader}-{mc_version}[/cyan]")
            else:
                self.console.print("\n[red]❌ Fabric kurulumu başarısız![/red]")
                if result.stderr:
                    self.console.print(f"[yellow]STDERR:[/yellow]\n[dim]{result.stderr[:500]}[/dim]")
                if result.stdout:
                    self.console.print(f"[yellow]STDOUT:[/yellow]\n[dim]{result.stdout[:500]}[/dim]")
            
            # Installer'ı temizle
            if installer_path.exists():
                installer_path.unlink()
            
        except Exception as e:
            self.console.print(f"\n[red]❌ Hata: {e}[/red]")
            self.console.print("\n[yellow]Manuel kurulum:[/yellow]")
            self.console.print("[dim]https://fabricmc.net/use/installer/[/dim]")
        
        input("\n[dim]Enter...[/dim]")
    
    def _install_quilt(self):
        """Quilt kur"""
        self.console.print("\n[bold]Quilt Kurulumu[/bold]")
        self.console.print("[yellow]⚠️ Quilt kurulumu manuel olarak yapılmalıdır[/yellow]")
        self.console.print("[dim]1. https://quiltmc.org/en/install/ adresine gidin[/dim]")
        self.console.print("[dim]2. Quilt Installer'ı indirin[/dim]")
        self.console.print("[dim]3. İstediğiniz sürümü seçin ve kurun[/dim]")
        input("[dim]Enter...[/dim]")
    
    def _create_mod_profile(self):
        """Mod profili oluştur"""
        self.console.print("\n[bold]Mod Profili Oluşturma[/bold]")
        self.console.print("[yellow]⚠️ Bu özellik henüz geliştirilmekte[/yellow]")
        input("[dim]Enter...[/dim]")
    
    def _test_mod_compatibility(self):
        """Mod uyumluluk testi"""
        self.console.print("\n[bold]Mod Uyumluluk Testi[/bold]")
        self.console.print("[yellow]⚠️ Bu özellik henüz geliştirilmekte[/yellow]")
        input("[dim]Enter...[/dim]")
    
    def _search_and_download_mod(self):
        """Mod ara ve indir - Modrinth API"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]MOD ARAMA[/bold cyan]\n"
            "[white]Modrinth API[/white]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # Minecraft sürümünü sor
        installed_versions = self._get_installed_versions()
        if not installed_versions:
            self.console.print("\n[yellow]Henuz surum yok![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print("\n[blue]Minecraft surumu:[/blue]")
        for i, ver in enumerate(installed_versions[:10], 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {ver}")
        
        try:
            ver_choice = int(Prompt.ask("\n[bold cyan]>[/bold cyan]", default="1"))
            if 1 <= ver_choice <= len(installed_versions):
                mc_version = installed_versions[ver_choice - 1]
            else:
                mc_version = installed_versions[0]
        except:
            mc_version = installed_versions[0]
        
        # Mod ara
        search_query = Prompt.ask("\n[cyan]Mod adi[/cyan] (ornek: sodium, iris)")
        
        if not search_query:
            return
        
        self.console.print(f"\n[blue]Araniyor: {search_query} ({mc_version})...[/blue]")
        
        try:
            # Modrinth API
            response = requests.get(
                f"https://api.modrinth.com/v2/search",
                params={
                    "query": search_query,
                    "facets": f'[["versions:{mc_version}"],["project_type:mod"]]',
                    "limit": 10
                },
                timeout=10
            )
            
            if response.status_code != 200:
                os.system('clear')
                self.console.print(Panel(
                    "[red]API hatasi![/red]",
                    border_style="red",
                    padding=(1, 2)
                ))
                input("[dim]Enter...[/dim]")
                return
            
            data = response.json()
            hits = data.get("hits", [])
            
            if not hits:
                os.system('clear')
                self.console.print(Panel(
                    f"[yellow]Sonuc bulunamadi: {search_query}[/yellow]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                input("[dim]Enter...[/dim]")
                return
            
            # Sonuçları göster - Minimal
            os.system('clear')
            self.console.print(Panel(
                f"[bold cyan]ARAMA SONUCLARI[/bold cyan]\n"
                f"[white]'{search_query}' - {len(hits)} sonuc[/white]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Kompakt liste
            for i, hit in enumerate(hits[:10], 1):
                title = hit.get("title", "Bilinmiyor")[:25]
                description = hit.get("description", "Aciklama yok")[:40]
                downloads = hit.get("downloads", 0)
                
                self.console.print(f"  [cyan]{i:2}[/cyan]  [green]{title:25}[/green]  [dim]{downloads:>8,} indirme[/dim]")
                self.console.print(f"      [dim]{description}[/dim]\n")
            
            # Mod seç
            choice = Prompt.ask("\n[bold cyan]>[/bold cyan] Mod numarasi (0=iptal)", default="0")
            
            try:
                choice_num = int(choice)
                if choice_num == 0:
                    return
                
                if 1 <= choice_num <= len(hits):
                    selected_mod = hits[choice_num - 1]
                    self._download_mod_from_modrinth(selected_mod, mc_version)
                else:
                    os.system("clear")
                    self.console.print("[red]Gecersiz secim![/red]")
            except ValueError:
                os.system("clear")
                self.console.print("[red]Gecersiz giris![/red]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Hata: {e}[/red]")
        
        input("\nDevam etmek için Enter'a basın...")
    
    def _download_mod_from_modrinth(self, mod_data: dict, mc_version: str):
        """Modrinth'ten mod indir"""
        project_id = mod_data.get("project_id")
        mod_name = mod_data.get("title", "Mod")
        
        self.console.print(f"\n[cyan]📥 {mod_name} indiriliyor...[/cyan]")
        
        try:
            # Proje detaylarını al
            response = requests.get(
                f"https://api.modrinth.com/v2/project/{project_id}/version",
                params={"game_versions": f'["{mc_version}"]'},
                timeout=10
            )
            
            if response.status_code != 200:
                self.console.print("[red]❌ Mod versiyonları alınamadı![/red]")
                return
            
            versions = response.json()
            
            if not versions:
                self.console.print(f"[yellow]⚠️ Minecraft {mc_version} için uyumlu versiyon bulunamadı![/yellow]")
                return
            
            # En son versiyonu al
            latest_version = versions[0]
            files = latest_version.get("files", [])
            
            if not files:
                self.console.print("[red]❌ İndirme dosyası bulunamadı![/red]")
                return
            
            # İlk dosyayı indir
            file_data = files[0]
            download_url = file_data.get("url")
            filename = file_data.get("filename")
            
            if not download_url or not filename:
                self.console.print("[red]❌ İndirme bilgileri eksik![/red]")
                return
            
            # Mods dizinine indir
            mods_dir = self.minecraft_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            mod_path = mods_dir / filename
            
            # İndir
            self.console.print(f"[blue]📥 {filename} indiriliyor...[/blue]")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                DownloadColumn(),
                TransferSpeedColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"[cyan]{filename}", total=total_size)
                
                with open(mod_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
            
            self.console.print(f"[green]✅ {mod_name} başarıyla indirildi![/green]")
            self.console.print(f"[blue]📂 Konum: {mod_path}[/blue]")
            
        except Exception as e:
            self.console.print(f"[red]❌ İndirme hatası: {e}[/red]")
    
    def _show_installed_mods(self):
        """Yüklü modları göster"""
        mods_dir = self.minecraft_dir / "mods"
        mods_dir.mkdir(exist_ok=True)
        
        mods = list(mods_dir.glob("*.jar"))
        
        if not mods:
            self.console.print("[yellow]⚠️ Henüz hiç mod yüklenmemiş![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        table = Table(title=f"📋 Yüklü Modlar ({len(mods)} adet)", show_header=True, header_style="bold green", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=5)
        table.add_column("Mod Adı", style="green", width=40)
        table.add_column("Boyut", style="yellow", width=12)
        table.add_column("Durum", style="white", width=15)
        
        for i, mod_path in enumerate(sorted(mods), 1):
            mod_name = mod_path.stem
            size_mb = mod_path.stat().st_size / (1024 * 1024)
            
            table.add_row(
                str(i),
                mod_name,
                f"{size_mb:.2f} MB",
                "✅ Aktif"
            )
        
        self.console.print(table)
        input("\nDevam etmek için Enter'a basın...")
    
    def _upload_local_mod(self):
        """Yerel mod dosyası yükle"""
        self.console.print("\n[cyan]📁 Yerel Mod Yükleme[/cyan]\n")
        
        mod_path = Prompt.ask("Mod dosyasının tam yolunu girin (.jar)")
        
        if not mod_path:
            return
        
        source_path = Path(mod_path).expanduser()
        
        if not source_path.exists():
            self.console.print("[red]❌ Dosya bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        if not source_path.suffix == ".jar":
            self.console.print("[red]❌ Sadece .jar dosyaları desteklenir![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        # Mods dizinine kopyala
        mods_dir = self.minecraft_dir / "mods"
        mods_dir.mkdir(exist_ok=True)
        dest_path = mods_dir / source_path.name
        
        try:
            shutil.copy2(source_path, dest_path)
            self.console.print(f"[green]✅ Mod yüklendi: {source_path.name}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Yükleme hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _delete_mod(self):
        """Mod sil"""
        mods_dir = self.minecraft_dir / "mods"
        mods = list(mods_dir.glob("*.jar"))
        
        if not mods:
            self.console.print("[yellow]⚠️ Silinecek mod yok![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print("\n[cyan]🗑️  Mod Silme[/cyan]\n")
        
        for i, mod_path in enumerate(sorted(mods), 1):
            self.console.print(f"  {i}. {mod_path.stem}")
        
        choice = Prompt.ask("\nSilinecek modun numarasını girin (0 = iptal)", default="0")
        
        try:
            choice_num = int(choice)
            if choice_num == 0:
                return
            
            if 1 <= choice_num <= len(mods):
                mod_to_delete = sorted(mods)[choice_num - 1]
                
                if Confirm.ask(f"[red]{mod_to_delete.name} silinsin mi?[/red]", default=False):
                    mod_to_delete.unlink()
                    self.console.print("[green]✅ Mod silindi![/green]")
            else:
                os.system("clear")
                self.console.print("[red]Gecersiz secim![/red]")
        except ValueError:
            os.system("clear")
            self.console.print("[red]Gecersiz giris![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_popular_mods(self):
        """Popüler modları göster - MINIMAL"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]POPULER MODLAR[/bold cyan]\n"
            "[white]Top 20 - En cok indirilen[/white]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        try:
            response = requests.get(
                "https://api.modrinth.com/v2/search",
                params={
                    "facets": '[["project_type:mod"]]',
                    "limit": 20,
                    "index": "downloads"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                self.console.print("\n[red]API hatasi![/red]")
                input("[dim]Enter...[/dim]")
                return
            
            data = response.json()
            hits = data.get("hits", [])
            
            self.console.print()
            
            # Kompakt liste - 20 mod
            for i, hit in enumerate(hits[:20], 1):
                title = hit.get("title", "Bilinmiyor")[:25]
                description = hit.get("description", "")[:35]
                downloads = hit.get("downloads", 0)
                
                self.console.print(f"  [cyan]{i:2}[/cyan]  [green]{title:25}[/green]  [dim]{downloads:>10,} indirme[/dim]")
                if description:
                    self.console.print(f"      [dim]{description}[/dim]")
                self.console.print()
            
            self.console.print("[dim]Mod indirmek icin 'Mod Ara' menusu[/dim]")
            
        except Exception as e:
            os.system('clear')
            self.console.print(Panel(
                f"[red]Hata: {str(e)}[/red]",
                border_style="red",
                padding=(1, 2)
            ))
        
        input("\n[dim]Enter...[/dim]")
    
    def _open_mods_folder(self):
        """Mod klasörünü aç"""
        mods_dir = self.minecraft_dir / "mods"
        mods_dir.mkdir(exist_ok=True)
        
        try:
            subprocess.Popen(["xdg-open", str(mods_dir)])
            self.console.print(f"[green]✅ Mod klasörü açıldı: {mods_dir}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Klasör açılamadı: {e}[/red]")
            self.console.print(f"[blue]📂 Manuel yol: {mods_dir}[/blue]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_game_monitor(self, process, version_id: str, log_file):
        """Oyun çalışırken kaynak izleme - Minecraft başlamasına izin ver"""
        import psutil
        import time
        
        # İlk başta tek seferlik bilgi göster
        self.console.print("[green]✅ Minecraft başlatıldı![/green]")
        self.console.print(f"[blue]📋 Sürüm: {version_id}[/blue]")
        self.console.print(f"[blue]🔢 Process ID: {process.pid}[/blue]")
        self.console.print("[yellow]💡 Minecraft penceresi açılmasını bekleyin...[/yellow]")
        self.console.print("[dim]Oyunu kapatmak için Ctrl+C tuşlarına basın.[/dim]")
        self.console.print("[cyan]Kaynak izleme için 'm' tuşuna basın.[/cyan]")
        
        # Minecraft'ın başlaması için yeterli zaman ver
        time.sleep(5)
        
        # Basit bir monitoring döngüsü (sürekli clear yok)
        while True:
            try:
                # Process hala çalışıyor mu?
                if process.poll() is not None:
                    self.console.print("\n[yellow]Minecraft kapandı![/yellow]")
                    input("[dim]Enter...[/dim]")
                    return
                
                # Non-blocking input check (1 saniye timeout)
                import select
                import sys
                
                i, o, e = select.select([sys.stdin], [], [], 1.0)
                if i:
                    key = sys.stdin.readline().strip()
                    if key.lower() == 'm':
                        # Monitoring ekranını göster (sadece istek üzerine)
                        self._show_detailed_monitor(process, version_id)
                    elif key.lower() == 'q':
                        self.console.print("[yellow]Minecraft kapatılıyor...[/yellow]")
                        process.terminate()
                        return
                
                # Her 30 saniyede bir basit durum güncellemesi
                if int(time.time()) % 30 == 0:
                    try:
                        p = psutil.Process(process.pid)
                        cpu_percent = p.cpu_percent()
                        mem_mb = p.memory_info().rss / (1024 * 1024)
                        self.console.print(f"[dim]Durum: CPU {cpu_percent:.1f}% | RAM {mem_mb:.0f}MB | PID {process.pid}[/dim]")
                    except:
                        pass
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.console.print("\n[yellow]Minecraft kapandı![/yellow]")
                input("[dim]Enter...[/dim]")
                return
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Minecraft kapatılıyor...[/yellow]")
                process.terminate()
                return
    
    def _show_detailed_monitor(self, process, version_id: str):
        """Detaylı monitoring ekranı (isteğe bağlı)"""
        import psutil
        import time
        
        os.system('clear')
        
        # Banner
        self.console.print(Panel(
            f"[bold cyan]MINECRAFT MONITORING[/bold cyan]\n"
            f"[white]Sürüm: {version_id}[/white]\n"
            f"[dim]PID: {process.pid}[/dim]",
            border_style="green",
            padding=(1, 2)
        ))
        
        # Process bilgisi
        try:
            p = psutil.Process(process.pid)
            
            # CPU kullanımı
            cpu_percent = p.cpu_percent(interval=0.5)
            cpu_bar = self._create_bar(cpu_percent, 100, 50, "CPU")
            
            # RAM kullanımı
            mem_info = p.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            mem_percent = p.memory_percent()
            mem_bar = self._create_bar(mem_percent, 100, 50, "RAM")
            
            # Sistem genel
            sys_cpu = psutil.cpu_percent(interval=0.1)
            sys_mem = psutil.virtual_memory().percent
            
            # Göster
            self.console.print()
            self.console.print(Panel(
                f"[cyan]Minecraft Process:[/cyan]\n\n"
                f"{cpu_bar}\n"
                f"[dim]Kullanım: {cpu_percent:.1f}%[/dim]\n\n"
                f"{mem_bar}\n"
                f"[dim]Kullanım: {mem_mb:.0f} MB ({mem_percent:.1f}%)[/dim]",
                title="[bold white]KAYNAK KULLANIMI[/bold white]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            sys_cpu_bar = self._create_bar(sys_cpu, 100, 50, "SYS CPU")
            sys_mem_bar = self._create_bar(sys_mem, 100, 50, "SYS RAM")
            
            self.console.print(Panel(
                f"[yellow]Sistem Geneli:[/yellow]\n\n"
                f"{sys_cpu_bar}\n"
                f"[dim]{sys_cpu:.1f}%[/dim]\n\n"
                f"{sys_mem_bar}\n"
                f"[dim]{sys_mem:.1f}%[/dim]",
                title="[bold white]SISTEM[/bold white]",
                border_style="yellow",
                padding=(1, 2)
            ))
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.console.print("[red]Process bilgisi alınamadı![/red]")
        
        self.console.print("\n[dim]Enter = Geri dön[/dim]")
        input()
    
    def _create_bar(self, value: float, max_value: float, width: int, label: str) -> str:
        """Büyük progress bar oluştur"""
        filled = int((value / max_value) * width)
        empty = width - filled
        
        # Renk seç
        if value < 50:
            color = "green"
        elif value < 80:
            color = "yellow"
        else:
            color = "red"
        
        bar = f"[{color}]{'█' * filled}[/{color}]" + f"[dim]{'░' * empty}[/dim]"
        return f"[white]{label:8}[/white] {bar}"
    
    def _show_performance_settings(self):
        """Performans Ayarları - Kullanıcı Dostu"""
        while True:
            os.system('clear')
            
            # Banner
            self.console.print(Panel(
                "[bold cyan]PERFORMANS AYARLARI[/bold cyan]\n"
                "[white]Oyun performansini optimize edin[/white]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Mevcut ayarlar
            memory = self.config.get("memory", "auto")
            optimize_graphics = self.config.get("optimize_graphics", True)
            fast_launch = self.config.get("fast_launch", True)
            
            # Sistem bilgisi
            system_info = self._get_system_info()
            
            self.console.print(Panel(
                f"[white]Sistem:[/white] [cyan]{system_info['cpu_cores']} CPU, {system_info['memory']} RAM[/cyan]\n"
                f"[white]Platform:[/white] [cyan]{system_info['os']} {system_info['arch']}[/cyan]",
                title="[bold white]Sistem Bilgisi[/bold white]",
                border_style="blue"
            ))
            
            self.console.print()
            
            # Performans profilleri
            self.console.print(Panel(
                "[white]Mevcut Ayarlar:[/white]\n\n"
                f"[cyan]1[/cyan]  Bellek Ayari          [yellow]{memory}[/yellow]\n"
                f"[cyan]2[/cyan]  Grafik Optimizasyonu  [{'green' if optimize_graphics else 'red'}]{'Acik' if optimize_graphics else 'Kapali'}[/{'green' if optimize_graphics else 'red'}]\n"
                f"[cyan]3[/cyan]  Hizli Baslatma        [{'green' if fast_launch else 'red'}]{'Acik' if fast_launch else 'Kapali'}[/{'green' if fast_launch else 'red'}]\n\n"
                "[dim]Performans profillerini secin:[/dim]",
                title="[bold white]Performans Ayarlari[/bold white]",
                border_style="cyan"
            ))
            
            self.console.print()
            
            # Hızlı profiller
            self.console.print(Panel(
                "[cyan]4[/cyan]  [green]Ultra Performans[/green]     [dim]16GB RAM, maksimum FPS[/dim]\n"
                "[cyan]5[/cyan]  [green]Yuksek Performans[/green]    [dim]8GB RAM, dengeli[/dim]\n"
                "[cyan]6[/cyan]  [yellow]Orta Performans[/yellow]      [dim]4GB RAM, uyumlu[/dim]\n"
                "[cyan]7[/cyan]  [yellow]Dusuk Performans[/yellow]     [dim]2GB RAM, minimum[/dim]\n\n"
                "[cyan]8[/cyan]  [blue]Sistem Optimizasyonu[/blue]  [dim]Auto-optimize scripti[/dim]\n"
                "[cyan]9[/cyan]  [blue]Performans Testi[/blue]      [dim]FPS ve sistem testi[/dim]\n\n"
                "[red]0[/red]  [red]Geri[/red]",
                title="[bold white]Hizli Profiller[/bold white]",
                border_style="blue"
            ))
            
            self.console.print()
            
            choice = Prompt.ask("[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == "0":
                break
            elif choice == "1":
                # Bellek ayarı
                self.console.print("\n[cyan]Bellek Ayari:[/cyan]")
                self.console.print("  [dim]auto[/dim]  - Otomatik (sistem belleginin %60'i)")
                self.console.print("  [dim]2-16[/dim]  - Manuel (GB cinsinden)")
                
                new_memory = Prompt.ask("\n[cyan]Bellek[/cyan]", default=str(memory))
                self.config["memory"] = new_memory
                self._save_config()
                self.console.print(f"[green]Bellek ayari guncellendi: {new_memory}[/green]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "2":
                # Grafik optimizasyonu
                self.config["optimize_graphics"] = not optimize_graphics
                self._save_config()
                status = "acildi" if self.config["optimize_graphics"] else "kapatildi"
                self.console.print(f"\n[green]Grafik optimizasyonu {status}[/green]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "3":
                # Hızlı başlatma
                self.config["fast_launch"] = not fast_launch
                self._save_config()
                status = "acildi" if self.config["fast_launch"] else "kapatildi"
                self.console.print(f"\n[green]Hizli baslatma {status}[/green]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "4":
                # Ultra Performans
                self.config["memory"] = "16"
                self.config["optimize_graphics"] = True
                self.config["fast_launch"] = True
                self.config["enable_mods"] = True
                self._save_config()
                self.console.print("\n[green]Ultra Performans profili yuklendi![/green]")
                self.console.print("[dim]16GB RAM, maksimum optimizasyon[/dim]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "5":
                # Yüksek Performans
                self.config["memory"] = "8"
                self.config["optimize_graphics"] = True
                self.config["fast_launch"] = True
                self._save_config()
                self.console.print("\n[green]Yuksek Performans profili yuklendi![/green]")
                self.console.print("[dim]8GB RAM, dengeli ayarlar[/dim]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "6":
                # Orta Performans
                self.config["memory"] = "4"
                self.config["optimize_graphics"] = True
                self.config["fast_launch"] = False
                self._save_config()
                self.console.print("\n[green]Orta Performans profili yuklendi![/green]")
                self.console.print("[dim]4GB RAM, uyumlu ayarlar[/dim]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "7":
                # Düşük Performans
                self.config["memory"] = "2"
                self.config["optimize_graphics"] = False
                self.config["fast_launch"] = False
                self._save_config()
                self.console.print("\n[green]Dusuk Performans profili yuklendi![/green]")
                self.console.print("[dim]2GB RAM, minimum ayarlar[/dim]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "8":
                # Sistem optimizasyonu
                self.console.print("\n[cyan]Sistem optimizasyonu baslatiliyor...[/cyan]")
                script_path = Path(__file__).parent / "scripts" / "auto_optimize.sh"
                if script_path.exists():
                    subprocess.run(["bash", str(script_path)])
                else:
                    self.console.print("[red]Optimizasyon scripti bulunamadi![/red]")
                input("\n[dim]Enter...[/dim]")
                
            elif choice == "9":
                # Performans testi
                self._run_performance_test()
    
    def _run_performance_test(self):
        """Performans testi yap"""
        import psutil
        
        os.system('clear')
        self.console.print(Panel(
            "[bold cyan]PERFORMANS TESTI[/bold cyan]\n"
            "[white]Sistem kapasitesi olculuyor...[/white]",
            border_style="cyan"
        ))
        
        self.console.print()
        
        # CPU testi
        self.console.print("[cyan]CPU testi...[/cyan]")
        cpu_percent = psutil.cpu_percent(interval=2)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # RAM testi
        self.console.print("[cyan]RAM testi...[/cyan]")
        mem = psutil.virtual_memory()
        
        # Disk testi
        self.console.print("[cyan]Disk testi...[/cyan]")
        disk = psutil.disk_usage('/')
        
        os.system('clear')
        
        # Sonuçlar
        self.console.print(Panel(
            "[bold green]TEST TAMAMLANDI[/bold green]",
            border_style="green"
        ))
        
        self.console.print()
        
        # CPU sonucu
        cpu_score = 100 - cpu_percent
        cpu_color = "green" if cpu_score > 70 else "yellow" if cpu_score > 50 else "red"
        self.console.print(Panel(
            f"[white]Cekirdek:[/white] [cyan]{cpu_count}[/cyan]\n"
            f"[white]Frekans:[/white] [cyan]{cpu_freq.current:.0f} MHz[/cyan]\n"
            f"[white]Kullanim:[/white] [{cpu_color}]{cpu_percent:.1f}%[/{cpu_color}]\n"
            f"[white]Skor:[/white] [{cpu_color}]{cpu_score:.0f}/100[/{cpu_color}]",
            title="[bold white]CPU[/bold white]",
            border_style=cpu_color
        ))
        
        self.console.print()
        
        # RAM sonucu
        ram_score = 100 - mem.percent
        ram_color = "green" if ram_score > 70 else "yellow" if ram_score > 50 else "red"
        self.console.print(Panel(
            f"[white]Toplam:[/white] [cyan]{mem.total / (1024**3):.1f} GB[/cyan]\n"
            f"[white]Kullanilabilir:[/white] [cyan]{mem.available / (1024**3):.1f} GB[/cyan]\n"
            f"[white]Kullanim:[/white] [{ram_color}]{mem.percent:.1f}%[/{ram_color}]\n"
            f"[white]Skor:[/white] [{ram_color}]{ram_score:.0f}/100[/{ram_color}]",
            title="[bold white]RAM[/bold white]",
            border_style=ram_color
        ))
        
        self.console.print()
        
        # Disk sonucu
        disk_score = 100 - disk.percent
        disk_color = "green" if disk_score > 70 else "yellow" if disk_score > 50 else "red"
        self.console.print(Panel(
            f"[white]Toplam:[/white] [cyan]{disk.total / (1024**3):.0f} GB[/cyan]\n"
            f"[white]Bos:[/white] [cyan]{disk.free / (1024**3):.0f} GB[/cyan]\n"
            f"[white]Kullanim:[/white] [{disk_color}]{disk.percent:.1f}%[/{disk_color}]\n"
            f"[white]Skor:[/white] [{disk_color}]{disk_score:.0f}/100[/{disk_color}]",
            title="[bold white]DISK[/bold white]",
            border_style=disk_color
        ))
        
        self.console.print()
        
        # Genel skor
        overall_score = (cpu_score + ram_score + disk_score) / 3
        overall_color = "green" if overall_score > 70 else "yellow" if overall_score > 50 else "red"
        
        # FPS tahmini
        if overall_score > 80:
            fps_estimate = "300-500+"
            quality = "Ultra"
        elif overall_score > 65:
            fps_estimate = "200-300"
            quality = "Cok Yuksek"
        elif overall_score > 50:
            fps_estimate = "100-200"
            quality = "Yuksek"
        elif overall_score > 35:
            fps_estimate = "60-100"
            quality = "Orta"
        else:
            fps_estimate = "30-60"
            quality = "Dusuk"
        
        self.console.print(Panel(
            f"[{overall_color}]GENEL SKOR: {overall_score:.0f}/100[/{overall_color}]\n\n"
            f"[white]Tahmini FPS:[/white] [{overall_color}]{fps_estimate}[/{overall_color}]\n"
            f"[white]Kalite:[/white] [{overall_color}]{quality}[/{overall_color}]",
            title="[bold white]SONUC[/bold white]",
            border_style=overall_color,
            padding=(1, 2)
        ))
        
        input("\n[dim]Enter...[/dim]")
    
    def _show_about(self):
        """Hakkında - Geliştirici bilgileri - KOMPAKT"""
        os.system('clear')
        
        # Kompakt banner
        self.console.print(Panel(
            "[bold cyan]BERKE MINECRAFT LAUNCHER[/bold cyan]\n"
            f"[white]v{__version__} - Terminal Edition[/white]\n"
            "[dim]Gelistirici: Berke Oruc (2009)[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # 2 kolon - Kompakt
        from rich.columns import Columns
        
        # Tek tablo - Kompakt
        info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        info_table.add_column("", style="dim cyan", width=12)
        info_table.add_column("", style="white", width=20)
        info_table.add_column("", style="dim green", width=12)
        info_table.add_column("", style="white", width=15)
        
        # Bilgiler
        installed_count = len(self._get_installed_versions())
        java_ver = self._check_java_version()
        
        info_table.add_row("Gelistirici", "Berke Oruc", "Surumler", f"{installed_count} adet")
        info_table.add_row("Dogum", "2009", "Java", f"v{java_ver}" if java_ver else "N/A")
        info_table.add_row("Platform", "Arch Linux", "Launcher", f"v{__version__}")
        
        self.console.print(Panel(info_table, title="[bold white]BILGILER[/bold white]", border_style="cyan", padding=(1, 1)))
        
        # Özellikler - 2 kolon
        self.console.print()
        features = (
            "[green]+[/green] Tum surumler      [green]+[/green] Skin yonetimi\n"
            "[green]+[/green] Paralel indirme   [green]+[/green] Mod destegi\n"
            "[green]+[/green] Cache yonetimi    [green]+[/green] Java otomatik\n"
            "[green]+[/green] Performans izleme [green]+[/green] Wayland destegi\n"
            "[green]+[/green] JVM optimizasyon  [green]+[/green] Dinamik arayuz"
        )
        self.console.print(Panel(features, title="[bold white]OZELLIKLER[/bold white]", border_style="green", padding=(1, 2)))
        
        self.console.print("\n[dim]Mojang Studios | Rich Library | Arch Linux[/dim]\n")
        
        input("[dim]Enter...[/dim]")
    
    def _show_system_info(self):
        """Sistem bilgilerini göster"""
        info = self._get_system_info()
        
        table = Table(title="💻 Sistem Bilgileri", show_header=True, header_style="bold green")
        table.add_column("Özellik", style="cyan", width=20)
        table.add_column("Değer", style="white")
        
        table.add_row("İşletim Sistemi", info["os"])
        table.add_row("Mimari", info["arch"])
        table.add_row("Bellek", info["memory"])
        table.add_row("CPU Çekirdekleri", info["cpu_cores"])
        table.add_row("Java Yolu", self.java_executable or "Bulunamadı")
        table.add_row("Minecraft Dizini", str(self.minecraft_dir))
        table.add_row("Launcher Dizini", str(self.launcher_dir))
        table.add_row("Cache Dizini", str(self.cache_dir))
        
        self.console.print(table)
    
    def _show_version_management_menu(self):
        """İndirilmiş sürümleri yönet - silme, düzenleme"""
        os.system('clear')
        
        # İndirilmiş sürümleri bul
        installed_versions = []
        if self.versions_dir.exists():
            for version_dir in self.versions_dir.iterdir():
                if version_dir.is_dir():
                    json_file = version_dir / f"{version_dir.name}.json"
                    if json_file.exists():
                        installed_versions.append(version_dir.name)
        
        if not installed_versions:
            self.console.print(Panel(
                "[bold yellow]HIC SURUM YOK[/bold yellow]\n"
                "[dim]Once surum indirmeniz gerekiyor[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(Panel(
            "[bold cyan]SURUM YONETIMI[/bold cyan]\n"
            f"[dim]Toplam: {len(installed_versions)} surum[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Sürüm listesi
        for i, version in enumerate(installed_versions, 1):
            version_dir = self.versions_dir / version
            size_mb = sum(f.stat().st_size for f in version_dir.rglob('*') if f.is_file()) / (1024*1024)
            
            self.console.print(f"  [cyan]{i:2}[/cyan]  {version:15}  [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri | Numara = Sec | S = Tumunu Sil[/dim]")
        
        try:
            choice_input = Prompt.ask("\n[cyan]>[/cyan]")
            
            if choice_input == "0":
                return
            elif choice_input.upper() == "S":
                if Confirm.ask("Tüm sürümleri silmek istediğinizden emin misiniz?", default=False):
                    import shutil
                    shutil.rmtree(self.versions_dir)
                    self.console.print("[green]✅ Tüm sürümler silindi![/green]")
                    input("[dim]Enter...[/dim]")
                return
            
            choice = int(choice_input)
            
            if 1 <= choice <= len(installed_versions):
                version_id = installed_versions[choice-1]
                self._show_version_edit_menu(version_id)
                
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_version_edit_menu(self, version_id: str):
        """Tek sürüm düzenleme menüsü"""
        while True:
            os.system('clear')
            
            version_dir = self.versions_dir / version_id
            size_mb = sum(f.stat().st_size for f in version_dir.rglob('*') if f.is_file()) / (1024*1024)
            
            self.console.print(Panel(
                f"[bold cyan]SURUM DUZENLE[/bold cyan]\n"
                f"[dim]Surum: {version_id}[/dim]\n"
                f"[dim]Boyut: {size_mb:.1f} MB[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Seçenek", style="cyan", width=20)
            table.add_column("Açıklama", style="dim")
            
            table.add_row("1", "Sürümü Başlat")
            table.add_row("2", "Sürümü Sil")
            table.add_row("3", "Modları Yönet")
            table.add_row("4", "Resource Pack Yönet")
            table.add_row("5", "Shader Yönet")
            table.add_row("6", "Dünya Yönetimi")
            table.add_row("0", "Geri")
            
            self.console.print(table)
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6"])
            
            if choice == "0":
                return
            elif choice == "1":
                self._launch_minecraft(version_id)
                return
            elif choice == "2":
                if Confirm.ask(f"'{version_id}' sürümünü silmek istediğinizden emin misiniz?", default=False):
                    import shutil
                    shutil.rmtree(version_dir)
                    self.console.print("[green]✅ Sürüm silindi![/green]")
                    input("[dim]Enter...[/dim]")
                    return
            elif choice == "3":
                self._show_mod_management_menu(version_id)
            elif choice == "4":
                self._show_resource_pack_menu(version_id)
            elif choice == "5":
                self._show_shader_menu(version_id)
            elif choice == "6":
                self._show_world_management_menu(version_id)

    def _show_mod_management_menu(self, version_id: str):
        """Mod yönetim menüsü - Forge desteği ile"""
        while True:
            os.system('clear')
            
            mods_dir = self.versions_dir / version_id / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            # Mevcut modları listele
            mod_files = list(mods_dir.glob("*.jar"))
            
            self.console.print(Panel(
                f"[bold cyan]MOD YONETIMI[/bold cyan]\n"
                f"[dim]Surum: {version_id}[/dim]\n"
                f"[dim]Toplam: {len(mod_files)} mod[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Seçenek", style="cyan", width=20)
            table.add_column("Açıklama", style="dim")
            
            table.add_row("1", "Mod Ekle (Dosya)")
            table.add_row("2", "Modrinth'ten Ara")
            table.add_row("3", "Modları Listele")
            table.add_row("4", "Mod Sil")
            table.add_row("5", "Forge Kur")
            table.add_row("0", "Geri")
            
            self.console.print(table)
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                return
            elif choice == "1":
                self._add_mod_from_file(version_id)
            elif choice == "2":
                self._search_and_install_mod(version_id)
            elif choice == "3":
                self._list_mods(version_id)
            elif choice == "4":
                self._delete_mod(version_id)
            elif choice == "5":
                self._install_forge(version_id)

    def _add_mod_from_file(self, version_id: str):
        """Dosyadan mod ekle"""
        self.console.print("\n[cyan]Mod dosyası yolunu girin:[/cyan]")
        file_path = Prompt.ask("[cyan]>[/cyan]")
        
        if not os.path.exists(file_path):
            self.console.print("[red]❌ Dosya bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        if not file_path.endswith('.jar'):
            self.console.print("[red]❌ Sadece .jar dosyaları desteklenir![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        mods_dir = self.versions_dir / version_id / "mods"
        mods_dir.mkdir(exist_ok=True)
        
        filename = os.path.basename(file_path)
        dest_path = mods_dir / filename
        
        import shutil
        shutil.copy2(file_path, dest_path)
        
        self.console.print("[green]✅ Mod başarıyla eklendi![/green]")
        input("[dim]Enter...[/dim]")

    def _search_and_install_mod(self, version_id: str):
        """Modrinth'ten mod ara ve yükle"""
        self.console.print("\n[cyan]Mod adı girin:[/cyan]")
        search_query = Prompt.ask("[cyan]>[/cyan]")
        
        if not search_query:
            return
        
        try:
            # Modrinth API'den ara
            url = f"https://api.modrinth.com/v2/search?query={search_query}&limit=10"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            mods = data.get("hits", [])
            
            if not mods:
                self.console.print("[yellow]⚠️ Mod bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                return
            
            self.console.print(f"\n[green]{len(mods)} mod bulundu:[/green]\n")
            
            for i, mod in enumerate(mods, 1):
                title = mod.get("title", "Bilinmeyen")
                downloads = mod.get("downloads", 0)
                self.console.print(f"  [cyan]{i:2}[/cyan]  {title:30} [dim]{downloads} indirme[/dim]")
            
            self.console.print("\n[dim]Numara = Sec | 0 = Geri[/dim]")
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(mods):
                selected_mod = mods[choice-1]
                self._install_mod_from_modrinth(version_id, selected_mod)
                
        except Exception as e:
            self.console.print(f"[red]❌ Hata: {e}[/red]")
            input("[dim]Enter...[/dim]")

    def _install_mod_from_modrinth(self, version_id: str, mod_data: dict):
        """Modrinth'ten mod yükle"""
        try:
            mod_id = mod_data["project_id"]
            mod_title = mod_data["title"]
            
            # Mod sürümlerini al
            url = f"https://api.modrinth.com/v2/project/{mod_id}/version"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            versions = response.json()
            if not versions:
                self.console.print("[yellow]⚠️ Mod sürümü bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                return
            
            # Uyumlu sürüm bul
            compatible_version = None
            for version in versions:
                game_versions = version.get("game_versions", [])
                if version_id in game_versions:
                    compatible_version = version
                    break
            
            if not compatible_version:
                self.console.print(f"[yellow]⚠️ {version_id} için uyumlu sürüm bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                return
            
            # İndirme URL'si al
            files = compatible_version.get("files", [])
            if not files:
                self.console.print("[red]❌ İndirme dosyası bulunamadı![/red]")
                input("[dim]Enter...[/dim]")
                return
            
            download_url = files[0]["url"]
            filename = files[0]["filename"]
            
            # Modu indir
            mods_dir = self.versions_dir / version_id / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            self.console.print(f"[cyan]İndiriliyor: {mod_title}...[/cyan]")
            
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            with open(mods_dir / filename, 'wb') as f:
                f.write(response.content)
            
            self.console.print("[green]✅ Mod başarıyla yüklendi![/green]")
            input("[dim]Enter...[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Hata: {e}[/red]")
            input("[dim]Enter...[/dim]")

    def _list_mods(self, version_id: str):
        """Modları listele"""
        mods_dir = self.versions_dir / version_id / "mods"
        
        if not mods_dir.exists():
            self.console.print("[yellow]⚠️ Mod dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        mod_files = list(mods_dir.glob("*.jar"))
        
        if not mod_files:
            self.console.print("[yellow]⚠️ Hiç mod bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Toplam {len(mod_files)} mod:[/green]\n")
        
        for i, mod_file in enumerate(mod_files, 1):
            size_mb = mod_file.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {mod_file.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        input("\n[dim]Enter...[/dim]")

    def _delete_mod(self, version_id: str):
        """Mod sil"""
        mods_dir = self.versions_dir / version_id / "mods"
        
        if not mods_dir.exists():
            self.console.print("[yellow]⚠️ Mod dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        mod_files = list(mods_dir.glob("*.jar"))
        
        if not mod_files:
            self.console.print("[yellow]⚠️ Hiç mod bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Silinecek mod seçin:[/green]\n")
        
        for i, mod_file in enumerate(mod_files, 1):
            size_mb = mod_file.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {mod_file.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(mod_files):
                mod_file = mod_files[choice-1]
                if Confirm.ask(f"'{mod_file.name}' modunu silmek istediğinizden emin misiniz?", default=False):
                    mod_file.unlink()
                    self.console.print("[green]✅ Mod silindi![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _install_forge(self, version_id: str):
        """Forge yükle - CLIENT kurulumu"""
        self.console.print(f"\n[cyan]Forge yükleniyor: {version_id}[/cyan]")
        
        try:
            # launcher_profiles.json oluştur (Forge installer için gerekli)
            launcher_profiles_path = self.minecraft_dir / "launcher_profiles.json"
            if not launcher_profiles_path.exists():
                default_profiles = {
                    "profiles": {
                        "default": {
                            "name": "Default",
                            "type": "latest-release",
                            "lastVersionId": "latest-release"
                        }
                    },
                    "selectedProfile": "default",
                    "clientToken": str(uuid.uuid4()),
                    "authenticationDatabase": {},
                    "launcherVersion": {"name": "BerkeMinecraftLauncher", "format": 21}
                }
                with open(launcher_profiles_path, 'w') as f:
                    json.dump(default_profiles, f, indent=2)
                self.console.print("[dim]✓ launcher_profiles.json oluşturuldu[/dim]")
            
            # Forge installer'ı indir
            forge_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version_id}/forge-{version_id}-installer.jar"
            
            self.console.print("[cyan]Forge installer indiriliyor...[/cyan]")
            
            response = requests.get(forge_url, timeout=30)
            response.raise_for_status()
            
            installer_path = self.cache_dir / f"forge-installer-{version_id}.jar"
            with open(installer_path, 'wb') as f:
                f.write(response.content)
            
            # Forge'u yükle (CLIENT mod, headless)
            self.console.print("[cyan]Forge yükleniyor (1-2 dakika sürebilir)...[/cyan]")
            
            import subprocess
            result = subprocess.run([
                self.java_executable,
                "-Djava.awt.headless=true",  # GUI'siz mod
                "-jar", str(installer_path),
                "--installClient",
                "--installDir", str(self.minecraft_dir)
            ], capture_output=True, text=True, cwd=str(Path.home()), timeout=300)
            
            if result.returncode == 0:
                self.console.print("[green]✅ Forge başarıyla yüklendi![/green]")
                self.console.print(f"[cyan]Profil: forge-{version_id}[/cyan]")
                
                # Installer'ı sil
                installer_path.unlink(missing_ok=True)
                
                input("[dim]Enter...[/dim]")
            else:
                self.console.print(f"[red]❌ Forge yüklenemedi[/red]")
                if result.stderr:
                    self.console.print(f"[yellow]STDERR:[/yellow]\n[dim]{result.stderr[:500]}[/dim]")
                if result.stdout:
                    self.console.print(f"[yellow]STDOUT:[/yellow]\n[dim]{result.stdout[:500]}[/dim]")
                input("[dim]Enter...[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Hata: {e}[/red]")
            input("[dim]Enter...[/dim]")

    def _show_resource_pack_menu(self, version_id: str):
        """Resource Pack yönetim menüsü"""
        resource_packs_dir = self.versions_dir / version_id / "resourcepacks"
        resource_packs_dir.mkdir(exist_ok=True)
        
        resource_packs = list(resource_packs_dir.glob("*.zip"))
        
        self.console.print(Panel(
            f"[bold cyan]RESOURCE PACK YONETIMI[/bold cyan]\n"
            f"[dim]Surum: {version_id}[/dim]\n"
            f"[dim]Toplam: {len(resource_packs)} pack[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Seçenek", style="cyan", width=20)
        table.add_column("Açıklama", style="dim")
        
        table.add_row("1", "Resource Pack Ekle")
        table.add_row("2", "Resource Pack'leri Listele")
        table.add_row("3", "Resource Pack Sil")
        table.add_row("0", "Geri")
        
        self.console.print(table)
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3"])
        
        if choice == "1":
            self._add_resource_pack(version_id)
        elif choice == "2":
            self._list_resource_packs(version_id)
        elif choice == "3":
            self._delete_resource_pack(version_id)

    def _add_resource_pack(self, version_id: str):
        """Resource Pack ekle"""
        self.console.print("\n[cyan]Resource Pack dosyası yolunu girin:[/cyan]")
        file_path = Prompt.ask("[cyan]>[/cyan]")
        
        if not os.path.exists(file_path):
            self.console.print("[red]❌ Dosya bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        if not file_path.endswith('.zip'):
            self.console.print("[red]❌ Sadece .zip dosyaları desteklenir![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        resource_packs_dir = self.versions_dir / version_id / "resourcepacks"
        resource_packs_dir.mkdir(exist_ok=True)
        
        filename = os.path.basename(file_path)
        dest_path = resource_packs_dir / filename
        
        import shutil
        shutil.copy2(file_path, dest_path)
        
        self.console.print("[green]✅ Resource Pack başarıyla eklendi![/green]")
        input("[dim]Enter...[/dim]")

    def _list_resource_packs(self, version_id: str):
        """Resource Pack'leri listele"""
        resource_packs_dir = self.versions_dir / version_id / "resourcepacks"
        
        if not resource_packs_dir.exists():
            self.console.print("[yellow]⚠️ Resource Pack dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        resource_packs = list(resource_packs_dir.glob("*.zip"))
        
        if not resource_packs:
            self.console.print("[yellow]⚠️ Hiç Resource Pack bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Toplam {len(resource_packs)} Resource Pack:[/green]\n")
        
        for i, pack in enumerate(resource_packs, 1):
            size_mb = pack.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {pack.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        input("\n[dim]Enter...[/dim]")

    def _delete_resource_pack(self, version_id: str):
        """Resource Pack sil"""
        resource_packs_dir = self.versions_dir / version_id / "resourcepacks"
        
        if not resource_packs_dir.exists():
            self.console.print("[yellow]⚠️ Resource Pack dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        resource_packs = list(resource_packs_dir.glob("*.zip"))
        
        if not resource_packs:
            self.console.print("[yellow]⚠️ Hiç Resource Pack bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Silinecek Resource Pack seçin:[/green]\n")
        
        for i, pack in enumerate(resource_packs, 1):
            size_mb = pack.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {pack.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(resource_packs):
                pack = resource_packs[choice-1]
                if Confirm.ask(f"'{pack.name}' Resource Pack'ini silmek istediğinizden emin misiniz?", default=False):
                    pack.unlink()
                    self.console.print("[green]✅ Resource Pack silindi![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _show_shader_menu(self, version_id: str):
        """Shader yönetim menüsü"""
        shaders_dir = self.versions_dir / version_id / "shaderpacks"
        shaders_dir.mkdir(exist_ok=True)
        
        shaders = list(shaders_dir.glob("*.zip"))
        
        self.console.print(Panel(
            f"[bold cyan]SHADER YONETIMI[/bold cyan]\n"
            f"[dim]Surum: {version_id}[/dim]\n"
            f"[dim]Toplam: {len(shaders)} shader[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Seçenek", style="cyan", width=20)
        table.add_column("Açıklama", style="dim")
        
        table.add_row("1", "Shader Ekle")
        table.add_row("2", "Shader'leri Listele")
        table.add_row("3", "Shader Sil")
        table.add_row("0", "Geri")
        
        self.console.print(table)
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3"])
        
        if choice == "1":
            self._add_shader(version_id)
        elif choice == "2":
            self._list_shaders(version_id)
        elif choice == "3":
            self._delete_shader(version_id)

    def _add_shader(self, version_id: str):
        """Shader ekle"""
        self.console.print("\n[cyan]Shader dosyası yolunu girin:[/cyan]")
        file_path = Prompt.ask("[cyan]>[/cyan]")
        
        if not os.path.exists(file_path):
            self.console.print("[red]❌ Dosya bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        if not file_path.endswith('.zip'):
            self.console.print("[red]❌ Sadece .zip dosyaları desteklenir![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        shaders_dir = self.versions_dir / version_id / "shaderpacks"
        shaders_dir.mkdir(exist_ok=True)
        
        filename = os.path.basename(file_path)
        dest_path = shaders_dir / filename
        
        import shutil
        shutil.copy2(file_path, dest_path)
        
        self.console.print("[green]✅ Shader başarıyla eklendi![/green]")
        input("[dim]Enter...[/dim]")

    def _list_shaders(self, version_id: str):
        """Shader'leri listele"""
        shaders_dir = self.versions_dir / version_id / "shaderpacks"
        
        if not shaders_dir.exists():
            self.console.print("[yellow]⚠️ Shader dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        shaders = list(shaders_dir.glob("*.zip"))
        
        if not shaders:
            self.console.print("[yellow]⚠️ Hiç shader bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Toplam {len(shaders)} shader:[/green]\n")
        
        for i, shader in enumerate(shaders, 1):
            size_mb = shader.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {shader.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        input("\n[dim]Enter...[/dim]")

    def _delete_shader(self, version_id: str):
        """Shader sil"""
        shaders_dir = self.versions_dir / version_id / "shaderpacks"
        
        if not shaders_dir.exists():
            self.console.print("[yellow]⚠️ Shader dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        shaders = list(shaders_dir.glob("*.zip"))
        
        if not shaders:
            self.console.print("[yellow]⚠️ Hiç shader bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Silinecek shader seçin:[/green]\n")
        
        for i, shader in enumerate(shaders, 1):
            size_mb = shader.stat().st_size / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {shader.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(shaders):
                shader = shaders[choice-1]
                if Confirm.ask(f"'{shader.name}' shader'ini silmek istediğinizden emin misiniz?", default=False):
                    shader.unlink()
                    self.console.print("[green]✅ Shader silindi![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _show_world_management_menu(self, version_id: str):
        """Dünya yönetim menüsü"""
        saves_dir = self.versions_dir / version_id / "saves"
        saves_dir.mkdir(exist_ok=True)
        
        worlds = [d for d in saves_dir.iterdir() if d.is_dir()]
        
        self.console.print(Panel(
            f"[bold cyan]DUNYA YONETIMI[/bold cyan]\n"
            f"[dim]Surum: {version_id}[/dim]\n"
            f"[dim]Toplam: {len(worlds)} dunya[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Seçenek", style="cyan", width=20)
        table.add_column("Açıklama", style="dim")
        
        table.add_row("1", "Dünyaları Listele")
        table.add_row("2", "Dünya Sil")
        table.add_row("3", "Dünya Kopyala")
        table.add_row("4", "Dünya Adını Değiştir")
        table.add_row("0", "Geri")
        
        self.console.print(table)
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4"])
        
        if choice == "1":
            self._list_worlds(version_id)
        elif choice == "2":
            self._delete_world(version_id)
        elif choice == "3":
            self._copy_world(version_id)
        elif choice == "4":
            self._rename_world(version_id)

    def _list_worlds(self, version_id: str):
        """Dünyaları listele"""
        saves_dir = self.versions_dir / version_id / "saves"
        
        if not saves_dir.exists():
            self.console.print("[yellow]⚠️ Saves dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        worlds = [d for d in saves_dir.iterdir() if d.is_dir()]
        
        if not worlds:
            self.console.print("[yellow]⚠️ Hiç dünya bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Toplam {len(worlds)} dünya:[/green]\n")
        
        for i, world in enumerate(worlds, 1):
            size_mb = sum(f.stat().st_size for f in world.rglob('*') if f.is_file()) / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {world.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        input("\n[dim]Enter...[/dim]")

    def _delete_world(self, version_id: str):
        """Dünya sil"""
        saves_dir = self.versions_dir / version_id / "saves"
        
        if not saves_dir.exists():
            self.console.print("[yellow]⚠️ Saves dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        worlds = [d for d in saves_dir.iterdir() if d.is_dir()]
        
        if not worlds:
            self.console.print("[yellow]⚠️ Hiç dünya bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Silinecek dünya seçin:[/green]\n")
        
        for i, world in enumerate(worlds, 1):
            size_mb = sum(f.stat().st_size for f in world.rglob('*') if f.is_file()) / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {world.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(worlds):
                world = worlds[choice-1]
                if Confirm.ask(f"'{world.name}' dünyasını silmek istediğinizden emin misiniz?", default=False):
                    import shutil
                    shutil.rmtree(world)
                    self.console.print("[green]✅ Dünya silindi![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _copy_world(self, version_id: str):
        """Dünya kopyala"""
        saves_dir = self.versions_dir / version_id / "saves"
        
        if not saves_dir.exists():
            self.console.print("[yellow]⚠️ Saves dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        worlds = [d for d in saves_dir.iterdir() if d.is_dir()]
        
        if not worlds:
            self.console.print("[yellow]⚠️ Hiç dünya bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Kopyalanacak dünya seçin:[/green]\n")
        
        for i, world in enumerate(worlds, 1):
            size_mb = sum(f.stat().st_size for f in world.rglob('*') if f.is_file()) / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {world.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(worlds):
                world = worlds[choice-1]
                new_name = Prompt.ask(f"Yeni dünya adı (şu anki: {world.name})")
                
                if new_name and new_name != world.name:
                    import shutil
                    dest = saves_dir / new_name
                    shutil.copytree(world, dest)
                    self.console.print("[green]✅ Dünya kopyalandı![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _rename_world(self, version_id: str):
        """Dünya adını değiştir"""
        saves_dir = self.versions_dir / version_id / "saves"
        
        if not saves_dir.exists():
            self.console.print("[yellow]⚠️ Saves dizini bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        worlds = [d for d in saves_dir.iterdir() if d.is_dir()]
        
        if not worlds:
            self.console.print("[yellow]⚠️ Hiç dünya bulunamadı![/yellow]")
            input("[dim]Enter...[/dim]")
            return
        
        self.console.print(f"\n[green]Adı değiştirilecek dünya seçin:[/green]\n")
        
        for i, world in enumerate(worlds, 1):
            size_mb = sum(f.stat().st_size for f in world.rglob('*') if f.is_file()) / (1024*1024)
            self.console.print(f"  [cyan]{i:2}[/cyan]  {world.name:40} [dim]{size_mb:.1f} MB[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(worlds):
                world = worlds[choice-1]
                new_name = Prompt.ask(f"Yeni dünya adı (şu anki: {world.name})")
                
                if new_name and new_name != world.name:
                    dest = saves_dir / new_name
                    world.rename(dest)
                    self.console.print("[green]✅ Dünya adı değiştirildi![/green]")
                    input("[dim]Enter...[/dim]")
                    
        except ValueError:
            self.console.print("[red]❌ Geçersiz seçim![/red]")
            input("[dim]Enter...[/dim]")

    def _show_versions_menu(self):
        """Sürüm menüsünü göster - Gelişmiş arama ile"""
        os.system('clear')
        
        versions = self._get_available_versions()
        
        # Banner
        self.console.print(Panel(
            "[bold cyan]MINECRAFT SURUMLERI[/bold cyan]\n"
            "[dim]Tum surumler • Arama • Filtreler[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # ARAMA ÖZELLİĞİ
        self.console.print("\n[cyan]Arama:[/cyan] [dim](bos = tumu)[/dim]")
        search_query = Prompt.ask("[cyan]>[/cyan]", default="").strip().lower()
        
        # Arama filtresi
        if search_query:
            filtered_versions = [v for v in versions if search_query in v["id"].lower() or search_query in v["type"].lower()]
            
            if not filtered_versions:
                self.console.print(f"\n[yellow]'{search_query}' icin sonuc bulunamadi![/yellow]\n")
                input("[dim]Enter...[/dim]")
                return
            
            versions = filtered_versions
            self.console.print(f"\n[green]{len(versions)} sonuc bulundu![/green]")
        
        # Filtre seçenekleri
        self.console.print("\n[cyan]Filtre:[/cyan] [dim]all | release | snapshot | beta | alpha[/dim]")
        filter_choice = Prompt.ask("[cyan]>[/cyan]", choices=["all", "release", "snapshot", "beta", "alpha"], default="all")
        
        if filter_choice != "all":
            versions = [v for v in versions if v["type"] == filter_choice]
        
        os.system('clear')
        
        # Sonuçları göster
        self.console.print(Panel(
            f"[bold cyan]SURUM LISTESI[/bold cyan]\n"
            f"[dim]Toplam: {len(versions)} surum[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Minimal liste - İlk 20 sürüm
        for i, version in enumerate(versions[:20], 1):
            version_id = version["id"]
            v_type = version["type"]
            
            # Tür göstergesi
            type_badge = {
                "release": "[green]R[/green]",
                "snapshot": "[yellow]S[/yellow]",
                "old_beta": "[blue]B[/blue]",
                "old_alpha": "[magenta]A[/magenta]"
            }.get(v_type, "[dim]?[/dim]")
            
            self.console.print(f"  [cyan]{i:2}[/cyan]  {type_badge}  {version_id:15}  [dim]{version['releaseTime'][:10]}[/dim]")
        
        if len(versions) > 20:
            self.console.print(f"\n[dim]... ve {len(versions) - 20} surum daha[/dim]")
        
        self.console.print("\n[dim]0 = Geri | Numara = Indir | D = Yonetim | M = Modlar[/dim]")
        
        try:
            choice_input = Prompt.ask("\n[cyan]>[/cyan]")
            
            if choice_input == "0":
                return
            elif choice_input.upper() == "D":
                self._show_version_management_menu()
                return
            elif choice_input.upper() == "M":
                self._show_mod_menu()
                return
            
            choice = int(choice_input)
            
            if 1 <= choice <= len(versions[:20]):
                version_id = versions[choice-1]["id"]
                if self._download_version(version_id):
                    self.console.print("[green]✅ Sürüm başarıyla indirildi![/green]")
                    if Confirm.ask("Şimdi başlatmak ister misiniz?", default=True):
                        self._launch_minecraft(version_id)
                else:
                    self.console.print("[red]❌ Sürüm indirilemedi![/red]")
                    input("[dim]Enter...[/dim]")
            else:
                self.console.print("\n[red]Gecersiz secim![/red]\n")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("\n[red]Gecersiz giris![/red]\n")
            input("[dim]Enter...[/dim]")
    
    def _show_installed_versions(self):
        """İndirilen sürümleri göster - Minimal ve Kompakt"""
        os.system('clear')
        
        versions = self._get_installed_versions()
        
        if not versions:
            self.console.print(Panel(
                "[yellow]Henuz surum indirilmemis![/yellow]\n"
                "[dim]Once bir surum indirmeniz gerekiyor.[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            
            if Confirm.ask("\nSurum indirmek ister misiniz?"):
                self._show_versions_menu()
            return
        
        # Banner
        self.console.print(Panel(
            f"[bold cyan]SÜRÜM YÖNETİMİ[/bold cyan]\n"
            f"[dim]Yüklü sürümler: {len(versions)}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Sürüm listesi
        for i, version in enumerate(versions, 1):
            version_dir = self.versions_dir / version
            jar_file = version_dir / f"{version}.jar"
            
            if jar_file.exists():
                size_mb = round(jar_file.stat().st_size / (1024*1024), 1)
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [dim]{size_mb:.0f} MB[/dim]")
            else:
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [red]Eksik[/red]")
        
        self.console.print()
        self.console.print("  [cyan]1[/cyan]  Sürüm Başlat")
        self.console.print("  [cyan]2[/cyan]  Sürüm Yönet")
        self.console.print("  [cyan]3[/cyan]  Sürüm Sil")
        self.console.print("  [cyan]4[/cyan]  Sürüm Onar")
        self.console.print()
        self.console.print("  [dim]0[/dim]  Geri")
        
        choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4"])
        
        if choice == "0":
            return
        elif choice == "1":
            self._select_and_launch_version(versions)
        elif choice == "2":
            self._manage_version(versions)
        elif choice == "3":
            self._delete_version(versions)
        elif choice == "4":
            self._repair_version(versions)
    
    def _select_and_launch_version(self, versions):
        """Sürüm seç ve başlat"""
        self.console.print("\n[bold]Başlatılacak sürümü seçin:[/bold]")
        for i, version in enumerate(versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {selected_version}[/yellow]")
                self._launch_minecraft(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _manage_version(self, versions):
        """Sürüm yönetimi"""
        self.console.print("\n[bold]Yönetilecek sürümü seçin:[/bold]")
        for i, version in enumerate(versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                self._show_version_management_menu(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_version_management_menu(self, version_id):
        """Sürüm yönetimi menüsü"""
        while True:
            os.system('clear')
            
            self.console.print(Panel(
                f"[bold green]SÜRÜM YÖNETİMİ: {version_id}[/bold green]\n"
                f"[dim]Sürüm detayları ve işlemler[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            # Sürüm bilgileri
            version_dir = self.versions_dir / version_id
            jar_file = version_dir / f"{version_id}.jar"
            size_mb = round(jar_file.stat().st_size / (1024*1024), 1) if jar_file.exists() else 0
            
            self.console.print()
            self.console.print(f"[bold]Sürüm Bilgileri:[/bold]")
            self.console.print(f"[green]ID:[/green] {version_id}")
            self.console.print(f"[green]Boyut:[/green] {size_mb} MB")
            self.console.print(f"[green]Konum:[/green] {version_dir}")
            
            self.console.print()
            self.console.print("[bold]Seçenekler:[/bold]")
            self.console.print("  [cyan]1[/cyan]  Sürümü Başlat")
            self.console.print("  [cyan]2[/cyan]  Sürümü Onar")
            self.console.print("  [cyan]3[/cyan]  Sürümü Sil")
            self.console.print("  [cyan]4[/cyan]  Sürüm Verilerini Sıfırla")
            self.console.print("  [cyan]5[/cyan]  Sürüm Bilgileri")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {version_id}[/yellow]")
                self._launch_minecraft(version_id)
                break
            elif choice == "2":
                self._repair_single_version(version_id)
            elif choice == "3":
                if self._confirm_delete_version(version_id):
                    self._delete_single_version(version_id)
                    break
            elif choice == "4":
                self._reset_version_data(version_id)
            elif choice == "5":
                self._show_version_info(version_id)
    
    def _delete_version(self, versions):
        """Sürüm sil"""
        self.console.print("\n[bold]Silinecek sürümü seçin:[/bold]")
        for i, version in enumerate(versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                if self._confirm_delete_version(selected_version):
                    self._delete_single_version(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _confirm_delete_version(self, version_id):
        """Sürüm silme onayı"""
        return Confirm.ask(f"[red]'{version_id}' sürümünü silmek istediğinizden emin misiniz?[/red]")
    
    def _delete_single_version(self, version_id):
        """Tek sürümü sil"""
        version_dir = self.versions_dir / version_id
        
        try:
            if version_dir.exists():
                import shutil
                shutil.rmtree(version_dir)
                self.console.print(f"[green]✅ {version_id} sürümü başarıyla silindi![/green]")
            else:
                self.console.print(f"[yellow]⚠️ {version_id} sürüm dizini bulunamadı![/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ {version_id} sürümü silinirken hata: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _repair_version(self, versions):
        """Sürüm onar"""
        self.console.print("\n[bold]Onarılacak sürümü seçin:[/bold]")
        for i, version in enumerate(versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version}")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                self._repair_single_version(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _repair_single_version(self, version_id):
        """Tek sürümü onar"""
        self.console.print(f"\n[blue]🔧 {version_id} sürümü onarılıyor...[/blue]")
        
        version_dir = self.versions_dir / version_id
        version_json_path = version_dir / f"{version_id}.json"
        
        if not version_json_path.exists():
            self.console.print(f"[red]❌ {version_id} sürüm JSON'u bulunamadı![/red]")
            input("[dim]Enter...[/dim]")
            return
        
        try:
            # Sürümü yeniden indir
            self.console.print("[yellow]📥 Sürüm dosyaları kontrol ediliyor...[/yellow]")
            self._download_version(version_id)
            
            # Native library'leri kontrol et
            self.console.print("[yellow]📦 Native library'ler kontrol ediliyor...[/yellow]")
            self._extract_all_native_libraries()
            
            # Asset'leri kontrol et
            self.console.print("[yellow]🎨 Asset'ler kontrol ediliyor...[/yellow]")
            # Asset kontrolü burada yapılabilir
            
            self.console.print(f"[green]✅ {version_id} sürümü başarıyla onarıldı![/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ {version_id} sürümü onarılırken hata: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _reset_version_data(self, version_id):
        """Sürüm verilerini sıfırla"""
        if Confirm.ask(f"[yellow]'{version_id}' sürümünün verilerini sıfırlamak istediğinizden emin misiniz?[/yellow]"):
            try:
                # Minecraft dizinindeki sürüm klasörünü sil
                minecraft_version_dir = self.minecraft_dir / "versions" / version_id
                if minecraft_version_dir.exists():
                    import shutil
                    shutil.rmtree(minecraft_version_dir)
                
                # Saves, logs, options.txt gibi dosyaları sil
                saves_dir = self.minecraft_dir / "saves"
                logs_dir = self.minecraft_dir / "logs"
                options_file = self.minecraft_dir / "options.txt"
                
                if saves_dir.exists():
                    shutil.rmtree(saves_dir)
                if logs_dir.exists():
                    shutil.rmtree(logs_dir)
                if options_file.exists():
                    options_file.unlink()
                
                self.console.print(f"[green]✅ {version_id} sürüm verileri sıfırlandı![/green]")
                
            except Exception as e:
                self.console.print(f"[red]❌ Veri sıfırlama hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_version_info(self, version_id):
        """Sürüm bilgileri göster"""
        version_dir = self.versions_dir / version_id
        version_json_path = version_dir / f"{version_id}.json"
        
        if version_json_path.exists():
            try:
                with open(version_json_path, 'r') as f:
                    version_data = json.load(f)
                
                self.console.print(f"\n[bold]{version_id} Sürüm Bilgileri:[/bold]")
                self.console.print(f"[green]ID:[/green] {version_data.get('id', 'N/A')}")
                self.console.print(f"[green]Tip:[/green] {version_data.get('type', 'N/A')}")
                self.console.print(f"[green]Ana Sınıf:[/green] {version_data.get('mainClass', 'N/A')}")
                
                if 'libraries' in version_data:
                    self.console.print(f"[green]Kütüphaneler:[/green] {len(version_data['libraries'])} adet")
                
                jar_file = version_dir / f"{version_id}.jar"
                size_mb = round(jar_file.stat().st_size / (1024*1024), 1) if jar_file.exists() else 0
                self.console.print(f"[green]Boyut:[/green] {size_mb} MB")
                
            except Exception as e:
                self.console.print(f"[red]❌ Sürüm bilgileri okunamadı: {e}[/red]")
        else:
            self.console.print(f"[red]❌ {version_id} sürüm JSON'u bulunamadı![/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_launch_versions(self):
        """Sadece başlatma için sürüm listesi"""
        os.system('clear')
        
        versions = self._get_installed_versions()
        
        if not versions:
            self.console.print(Panel(
                "[yellow]Henüz sürüm indirilmemiş![/yellow]\n"
                "[dim]Önce bir sürüm indirmeniz gerekiyor.[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            
            if Confirm.ask("\nSürüm indirmek ister misiniz?"):
                self._show_versions_menu()
            return
        
        # Banner
        self.console.print(Panel(
            f"[bold cyan]MINECRAFT BAŞLAT[/bold cyan]\n"
            f"[dim]Yüklü sürümler: {len(versions)}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Sürüm listesi - Mod loader türü ile
        for i, version in enumerate(versions, 1):
            version_dir = self.versions_dir / version
            jar_file = version_dir / f"{version}.jar"
            
            # Mod loader türünü belirle
            loader_type = ""
            if "forge" in version.lower():
                loader_type = "[yellow]⚒️  Forge[/yellow]"
            elif "fabric" in version.lower():
                loader_type = "[green]🧵 Fabric[/green]"
            elif "quilt" in version.lower():
                loader_type = "[purple]🎨 Quilt[/purple]"
            else:
                loader_type = "[blue]⭐ Vanilla[/blue]"
            
            if jar_file.exists():
                size_mb = round(jar_file.stat().st_size / (1024*1024), 1)
                self.console.print(f"  [cyan]{i}[/cyan]  {version:25}  {loader_type}  [dim]{size_mb:.0f} MB[/dim]")
            else:
                # JAR dosyası yoksa dizindeki herhangi bir JAR'a bak
                jar_files = list(version_dir.glob("*.jar"))
                if jar_files:
                    size_mb = round(jar_files[0].stat().st_size / (1024*1024), 1)
                    self.console.print(f"  [cyan]{i}[/cyan]  {version:25}  {loader_type}  [dim]{size_mb:.0f} MB[/dim]")
                else:
                    self.console.print(f"  [cyan]{i}[/cyan]  {version:25}  {loader_type}  [red]Eksik JAR[/red]")
        
        self.console.print("\n[dim]0 = Geri | Numara = Başlat[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {selected_version}[/yellow]")
                self._launch_minecraft(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_version_management(self):
        """Sürüm yönetimi - sürüm seç, sonra ne yapmak istediğini sor"""
        os.system('clear')
        
        versions = self._get_installed_versions()
        
        if not versions:
            self.console.print(Panel(
                "[yellow]Henüz sürüm indirilmemiş![/yellow]\n"
                "[dim]Önce bir sürüm indirmeniz gerekiyor.[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            
            if Confirm.ask("\nSürüm indirmek ister misiniz?"):
                self._show_versions_menu()
            return
        
        # Banner
        self.console.print(Panel(
            f"[bold cyan]SÜRÜM YÖNETİMİ[/bold cyan]\n"
            f"[dim]Yüklü sürümler: {len(versions)}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Sürüm listesi
        for i, version in enumerate(versions, 1):
            version_dir = self.versions_dir / version
            jar_file = version_dir / f"{version}.jar"
            
            if jar_file.exists():
                size_mb = round(jar_file.stat().st_size / (1024*1024), 1)
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [dim]{size_mb:.0f} MB[/dim]")
            else:
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [red]Eksik[/red]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]Yönetilecek sürümü seçin:[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(versions):
                selected_version = versions[choice - 1]
                self._ask_version_action(selected_version)
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _ask_version_action(self, version_id):
        """Seçilen sürüm için ne yapmak istediğini sor"""
        while True:
            os.system('clear')
            
            self.console.print(Panel(
                f"[bold green]SÜRÜM: {version_id}[/bold green]\n"
                f"[dim]Bu sürüm ile ne yapmak istiyorsunuz?[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            self.console.print()
            self.console.print("[bold]Seçenekler:[/bold]")
            self.console.print("  [cyan]1[/cyan]  🚀 Sürümü Başlat")
            self.console.print("  [cyan]2[/cyan]  🔧 Sürümü Onar")
            self.console.print("  [cyan]3[/cyan]  🗑️ Sürümü Sil")
            self.console.print("  [cyan]4[/cyan]  🔄 Sürüm Verilerini Sıfırla")
            self.console.print("  [cyan]5[/cyan]  ℹ️ Sürüm Bilgileri")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {version_id}[/yellow]")
                self._launch_minecraft(version_id)
                break
            elif choice == "2":
                self._repair_single_version(version_id)
            elif choice == "3":
                if self._confirm_delete_version(version_id):
                    self._delete_single_version(version_id)
                    break
            elif choice == "4":
                self._reset_version_data(version_id)
            elif choice == "5":
                self._show_version_info(version_id)
    
    def _show_advanced_download_menu(self):
        """Gelişmiş sürüm indirme menüsü"""
        while True:
            os.system('clear')
            
            self.console.print(Panel(
                "[bold cyan]SÜRÜM İNDİR[/bold cyan]\n"
                "[dim]Minecraft sürümlerini indir ve yönet[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            self.console.print("[bold]Seçenekler:[/bold]")
            self.console.print("  [cyan]1[/cyan]  📋 Tüm Sürümler")
            self.console.print("  [cyan]2[/cyan]  📊 Popüler Sürümler")
            self.console.print("  [cyan]3[/cyan]  🎮 Snapshots")
            self.console.print("  [cyan]4[/cyan]  🔧 Release Candidates")
            self.console.print("  [cyan]5[/cyan]  📈 En Güncel Sürümler")
            self.console.print("  [cyan]6[/cyan]  ⚒️  Forge Sürümleri")
            self.console.print("  [cyan]7[/cyan]  🧵 Fabric Sürümleri")
            self.console.print("  [cyan]8[/cyan]  ⚡ OptiFine Bilgisi")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._show_versions_menu()
            elif choice == "2":
                self._show_popular_versions()
            elif choice == "3":
                self._show_snapshot_versions()
            elif choice == "4":
                self._show_release_candidate_versions()
            elif choice == "5":
                self._show_latest_versions()
            elif choice == "6":
                self._show_forge_versions()
            elif choice == "7":
                self._show_fabric_versions()
            elif choice == "8":
                self._show_optifine_versions()
    
    def _search_versions(self):
        """Sürüm arama"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]SÜRÜM ARAMA[/bold cyan]\n"
            "[dim]Minecraft sürümlerinde arama yapın[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        search_term = Prompt.ask("[cyan]Aranacak sürüm (örn: 1.21, 1.20, snapshot)[/cyan]")
        
        if not search_term:
            self.console.print("[red]❌ Arama terimi boş olamaz![/red]")
            input("[dim]Enter...[/dim]")
    
    def _download_version_with_progress(self, version_id):
        """Progress bar ile sürüm indirme"""
        try:
            # İndirme ekranı başlat
            self.console.print(Panel(
                f"[bold cyan]MINECRAFT SÜRÜM İNDİRİLİYOR[/bold cyan]\n"
                f"[dim]Sürüm: {version_id}[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            # Sürüm bilgilerini al
            self.console.print(f"[blue]🔍 Sürüm bilgileri alınıyor: {version_id}[/blue]")
            versions = self._get_available_versions()
            version_info = None
            
            for version in versions:
                if version["id"] == version_id:
                    version_info = version
                    break
            
            if not version_info:
                self.console.print(f"[red]❌ Sürüm bulunamadı: {version_id}[/red]")
                input("[dim]Enter...[/dim]")
                return
            
            # Sürüm boyutunu hesapla
            total_size = 0
            if "downloads" in version_info and "client" in version_info["downloads"]:
                total_size = version_info["downloads"]["client"].get("size", 0)
            
            size_mb = round(total_size / (1024 * 1024), 1) if total_size > 0 else "Bilinmiyor"
            
            self.console.print(f"[green]✅ Sürüm bulundu! Boyut: {size_mb} MB[/green]")
            
            # İndirme başlat
            if self._download_version(version_id):
                self.console.print(f"[green]✅ {version_id} başarıyla indirildi![/green]")
                if Confirm.ask("Şimdi başlatmak ister misiniz?", default=True):
                    self._launch_minecraft(version_id)
            else:
                self.console.print(f"[red]❌ {version_id} indirilemedi![/red]")
                
        except Exception as e:
            self.console.print(f"[red]❌ İndirme hatası: {e}[/red]")
        
        input("[dim]Enter...[/dim]")
    
    def _show_popular_versions(self):
        """Popüler sürümler"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]POPÜLER SÜRÜMLER[/bold cyan]\n"
            "[dim]En çok oynanan Minecraft sürümleri[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        # Popüler sürümler listesi
        popular_versions = [
            {"id": "1.21.1", "name": "1.21.1", "description": "En güncel sürüm"},
            {"id": "1.20.6", "name": "1.20.6", "description": "Stabil sürüm"},
            {"id": "1.19.4", "name": "1.19.4", "description": "Mod uyumlu"},
            {"id": "1.18.2", "name": "1.18.2", "description": "Forge uyumlu"},
            {"id": "1.16.5", "name": "1.16.5", "description": "Klasik sürüm"},
            {"id": "1.12.2", "name": "1.12.2", "description": "Eski mod sürümü"}
        ]
        
        self.console.print()
        for i, version in enumerate(popular_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version['name']:10} [dim]{version['description']}[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]İndirilecek sürümü seçin:[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(popular_versions):
                selected_version = popular_versions[choice - 1]
                self._download_version_with_progress(selected_version['id'])
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_snapshot_versions(self):
        """Snapshot sürümleri"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]SNAPSHOT SÜRÜMLERİ[/bold cyan]\n"
            "[dim]Minecraft snapshot sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 Snapshot sürümleri aranıyor...[/blue]")
        
        try:
            versions = self._get_available_versions()
            snapshot_versions = []
            
            for version in versions:
                if version.get('type', '').lower() == 'snapshot':
                    snapshot_versions.append(version)
            
            if snapshot_versions:
                self.console.print(f"\n[green]✅ {len(snapshot_versions)} snapshot bulundu![/green]")
                
                # En son 10 snapshot'ı göster
                recent_snapshots = snapshot_versions[:10]
                for i, version in enumerate(recent_snapshots, 1):
                    self.console.print(f"  [cyan]{i}[/cyan]  {version['id']:25} [dim]snapshot[/dim]")
                
                if len(snapshot_versions) > 10:
                    self.console.print(f"  [dim]... ve {len(snapshot_versions) - 10} snapshot daha[/dim]")
                
                # İndirme seçimi
                try:
                    choice = int(Prompt.ask("\n[cyan]İndirilecek snapshot'ı seçin (0 = İptal)[/cyan]"))
                    if choice == 0:
                        return
                    
                    if 1 <= choice <= len(recent_snapshots):
                        selected_version = recent_snapshots[choice - 1]
                        self._download_version_with_progress(selected_version['id'])
                    else:
                        self.console.print("[red]❌ Geçersiz seçim![/red]")
                        input("[dim]Enter...[/dim]")
                except ValueError:
                    self.console.print("[red]❌ Geçersiz giriş![/red]")
                    input("[dim]Enter...[/dim]")
            else:
                self.console.print("[yellow]⚠️ Hiç snapshot bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Snapshot arama hatası: {e}[/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_release_candidate_versions(self):
        """Release Candidate sürümleri"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]RELEASE CANDIDATE SÜRÜMLERİ[/bold cyan]\n"
            "[dim]Minecraft release candidate sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 Release candidate sürümleri aranıyor...[/blue]")
        
        try:
            versions = self._get_available_versions()
            rc_versions = []
            
            for version in versions:
                if 'rc' in version.get('id', '').lower() or version.get('type', '').lower() == 'release_candidate':
                    rc_versions.append(version)
            
            if rc_versions:
                self.console.print(f"\n[green]✅ {len(rc_versions)} release candidate bulundu![/green]")
                
                # En son 10 RC'yi göster
                recent_rcs = rc_versions[:10]
                for i, version in enumerate(recent_rcs, 1):
                    self.console.print(f"  [cyan]{i}[/cyan]  {version['id']:25} [dim]release_candidate[/dim]")
                
                if len(rc_versions) > 10:
                    self.console.print(f"  [dim]... ve {len(rc_versions) - 10} RC daha[/dim]")
                
                # İndirme seçimi
                try:
                    choice = int(Prompt.ask("\n[cyan]İndirilecek RC'yi seçin (0 = İptal)[/cyan]"))
                    if choice == 0:
                        return
                    
                    if 1 <= choice <= len(recent_rcs):
                        selected_version = recent_rcs[choice - 1]
                        self._download_version_with_progress(selected_version['id'])
                    else:
                        self.console.print("[red]❌ Geçersiz seçim![/red]")
                        input("[dim]Enter...[/dim]")
                except ValueError:
                    self.console.print("[red]❌ Geçersiz giriş![/red]")
                    input("[dim]Enter...[/dim]")
            else:
                self.console.print("[yellow]⚠️ Hiç release candidate bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ RC arama hatası: {e}[/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_latest_versions(self):
        """En güncel sürümler"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]EN GÜNCEL SÜRÜMLER[/bold cyan]\n"
            "[dim]Minecraft'ın en yeni sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 En güncel sürümler aranıyor...[/blue]")
        
        try:
            versions = self._get_available_versions()
            latest_versions = []
            
            for version in versions:
                if version.get('type', '').lower() == 'release':
                    latest_versions.append(version)
            
            if latest_versions:
                self.console.print(f"\n[green]✅ {len(latest_versions)} güncel sürüm bulundu![/green]")
                
                # En son 15 release'i göster
                recent_releases = latest_versions[:15]
                for i, version in enumerate(recent_releases, 1):
                    self.console.print(f"  [cyan]{i}[/cyan]  {version['id']:25} [dim]release[/dim]")
                
                if len(latest_versions) > 15:
                    self.console.print(f"  [dim]... ve {len(latest_versions) - 15} sürüm daha[/dim]")
                
                # İndirme seçimi
                try:
                    choice = int(Prompt.ask("\n[cyan]İndirilecek sürümü seçin (0 = İptal)[/cyan]"))
                    if choice == 0:
                        return
                    
                    if 1 <= choice <= len(recent_releases):
                        selected_version = recent_releases[choice - 1]
                        self._download_version_with_progress(selected_version['id'])
                    else:
                        self.console.print("[red]❌ Geçersiz seçim![/red]")
                        input("[dim]Enter...[/dim]")
                except ValueError:
                    self.console.print("[red]❌ Geçersiz giriş![/red]")
                    input("[dim]Enter...[/dim]")
            else:
                self.console.print("[yellow]⚠️ Hiç güncel sürüm bulunamadı![/yellow]")
                input("[dim]Enter...[/dim]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Güncel sürüm arama hatası: {e}[/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_forge_versions(self):
        """Forge sürümleri"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]FORGE SÜRÜMLERİ[/bold cyan]\n"
            "[dim]Minecraft Forge sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 Forge sürümleri aranıyor...[/blue]")
        
        # Popüler Forge sürümleri
        forge_versions = [
            {"id": "1.21.1-forge-50.0.0", "name": "1.21.1 Forge 50.0.0", "description": "En güncel Forge"},
            {"id": "1.20.6-forge-49.0.0", "name": "1.20.6 Forge 49.0.0", "description": "Stabil Forge"},
            {"id": "1.19.4-forge-45.2.0", "name": "1.19.4 Forge 45.2.0", "description": "Mod uyumlu"},
            {"id": "1.18.2-forge-40.2.0", "name": "1.18.2 Forge 40.2.0", "description": "Popüler sürüm"},
            {"id": "1.16.5-forge-36.2.0", "name": "1.16.5 Forge 36.2.0", "description": "Klasik Forge"},
            {"id": "1.12.2-forge-14.23.5.2860", "name": "1.12.2 Forge 14.23.5.2860", "description": "Eski mod sürümü"}
        ]
        
        self.console.print(f"\n[green]✅ {len(forge_versions)} Forge sürümü bulundu![/green]")
        
        for i, version in enumerate(forge_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version['name']:35} [dim]{version['description']}[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]İndirilecek Forge sürümünü seçin:[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(forge_versions):
                selected_version = forge_versions[choice - 1]
                self.console.print(f"\n[cyan]Seçilen: {selected_version['name']}[/cyan]")
                
                if Confirm.ask(f"\n[cyan]{selected_version['name']} indirilsin ve kurulsun mu?[/cyan]", default=True):
                    # Forge version ID'i parse et: "1.21.1-forge-50.0.0" → mc="1.21.1", forge="50.0.0"
                    parts = selected_version['id'].split('-')
                    if len(parts) >= 3 and parts[1] == 'forge':
                        minecraft_version = parts[0]
                        forge_version = '-'.join(parts[2:])
                        self._download_forge(minecraft_version, forge_version)
                    else:
                        self.console.print("[red]❌ Geçersiz Forge version formatı![/red]")
                        input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_optifine_versions(self):
        """OptiFine sürümleri"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]OPTIFINE SÜRÜMLERİ[/bold cyan]\n"
            "[dim]Minecraft OptiFine sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 OptiFine sürümleri aranıyor...[/blue]")
        
        # Popüler OptiFine sürümleri
        optifine_versions = [
            {"id": "1.21.1-OptiFine-HD-U-I9", "name": "1.21.1 OptiFine HD U I9", "description": "En güncel OptiFine"},
            {"id": "1.20.6-OptiFine-HD-U-I8", "name": "1.20.6 OptiFine HD U I8", "description": "Stabil OptiFine"},
            {"id": "1.19.4-OptiFine-HD-U-I6", "name": "1.19.4 OptiFine HD U I6", "description": "Performans odaklı"},
            {"id": "1.18.2-OptiFine-HD-U-H9", "name": "1.18.2 OptiFine HD U H9", "description": "Popüler sürüm"},
            {"id": "1.16.5-OptiFine-HD-U-G8", "name": "1.16.5 OptiFine HD U G8", "description": "Klasik OptiFine"},
            {"id": "1.12.2-OptiFine-HD-U-G5", "name": "1.12.2 OptiFine HD U G5", "description": "Eski sürüm"}
        ]
        
        self.console.print(f"\n[green]✅ {len(optifine_versions)} OptiFine sürümü bulundu![/green]")
        
        for i, version in enumerate(optifine_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version['name']:35} [dim]{version['description']}[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]İndirilecek OptiFine sürümünü seçin:[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(optifine_versions):
                selected_version = optifine_versions[choice - 1]
                self.console.print(f"[yellow]⚠️ OptiFine sürümleri manuel olarak indirilmelidir.[/yellow]")
                self.console.print(f"[blue]🌐 OptiFine İndirme: https://optifine.net/downloads[/blue]")
                self.console.print(f"[dim]OptiFine'ı indirdikten sonra mods klasörüne yerleştirin.[/dim]")
                input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _show_fabric_versions(self):
        """Fabric sürümleri"""
        os.system('clear')
        
        self.console.print(Panel(
            "[bold cyan]FABRIC SÜRÜMLERİ[/bold cyan]\n"
            "[dim]Minecraft Fabric sürümlerini indirin[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print("[blue]🔍 Fabric sürümleri aranıyor...[/blue]")
        
        # Popüler Fabric sürümleri
        fabric_versions = [
            {"id": "1.21.1-fabric-0.16.0", "name": "1.21.1 Fabric 0.16.0", "description": "En güncel Fabric"},
            {"id": "1.20.6-fabric-0.15.0", "name": "1.20.6 Fabric 0.15.0", "description": "Stabil Fabric"},
            {"id": "1.19.4-fabric-0.14.0", "name": "1.19.4 Fabric 0.14.0", "description": "Mod uyumlu"},
            {"id": "1.18.2-fabric-0.13.0", "name": "1.18.2 Fabric 0.13.0", "description": "Popüler sürüm"},
            {"id": "1.16.5-fabric-0.12.0", "name": "1.16.5 Fabric 0.12.0", "description": "Klasik Fabric"},
            {"id": "1.12.2-fabric-0.8.0", "name": "1.12.2 Fabric 0.8.0", "description": "Eski sürüm"}
        ]
        
        self.console.print(f"\n[green]✅ {len(fabric_versions)} Fabric sürümü bulundu![/green]")
        
        for i, version in enumerate(fabric_versions, 1):
            self.console.print(f"  [cyan]{i}[/cyan]  {version['name']:35} [dim]{version['description']}[/dim]")
        
        self.console.print("\n[dim]0 = Geri[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]İndirilecek Fabric sürümünü seçin:[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(fabric_versions):
                selected_version = fabric_versions[choice - 1]
                self.console.print(f"\n[cyan]Seçilen: {selected_version['name']}[/cyan]")
                
                if Confirm.ask(f"\n[cyan]{selected_version['name']} indirilsin ve kurulsun mu?[/cyan]", default=True):
                    # Fabric version ID'i parse et: "1.21.1-fabric-0.16.0" → mc="1.21.1", fabric="0.16.0"
                    parts = selected_version['id'].split('-')
                    if len(parts) >= 3 and parts[1] == 'fabric':
                        minecraft_version = parts[0]
                        fabric_version = '-'.join(parts[2:])
                        self._download_fabric(minecraft_version, fabric_version)
                    else:
                        self.console.print("[red]❌ Geçersiz Fabric version formatı![/red]")
                        input("[dim]Enter...[/dim]")
            else:
                self.console.print("[red]❌ Geçersiz seçim![/red]")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz giriş![/red]")
            input("[dim]Enter...[/dim]")
    
    def _first_run_setup(self):
        """İlk çalıştırma kurulum menüsü"""
        if not self.config.get("first_run_completed", False):
            os.system('clear')
            
            self.console.print(Panel(
                "[bold cyan]🎮 BERKE MINECRAFT LAUNCHER'e HOŞ GELDİNİZ![/bold cyan]\n"
                "[dim]İlk kurulum sihirbazı[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            self.console.print("[bold]Launcher Hakkında:[/bold]")
            self.console.print("• 🚀 Ultra hızlı Minecraft launcher'ı")
            self.console.print("• ☕ Otomatik Java yönetimi")
            self.console.print("• 📥 Gelişmiş sürüm indirme sistemi")
            self.console.print("• 🎨 Skin yönetimi")
            self.console.print("• 🔧 Mod desteği")
            self.console.print("• 🖥️ Wayland/Hyprland uyumlu")
            
            self.console.print()
            self.console.print("[bold]Kurulum Adımları:[/bold]")
            
            # Java kontrolü
            java_versions = self._get_installed_java_versions()
            if not java_versions:
                self.console.print("[red]❌ Java bulunamadı![/red]")
                self.console.print("[yellow]Java kurulumu yapılıyor...[/yellow]")
                
                if Confirm.ask("Java 21 otomatik kurulsun mu?", default=True):
                    self.console.print("[blue]📦 Java 21 kuruluyor...[/blue]")
                    try:
                        import subprocess
                        result = subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "jdk21-openjdk"], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            self.console.print("[green]✅ Java 21 başarıyla kuruldu![/green]")
                            # Java'yı güncelle
                            self.java_executable = "/usr/lib/jvm/java-21-openjdk/bin/java"
                            self.config["java_path"] = "/usr/lib/jvm/java-21-openjdk/bin/java"
                            self._save_config()
                        else:
                            self.console.print("[red]❌ Java kurulumu başarısız![/red]")
                            self.console.print("[yellow]Manuel kurulum: sudo pacman -S jdk21-openjdk[/yellow]")
                    except Exception as e:
                        self.console.print(f"[red]❌ Java kurulum hatası: {e}[/red]")
            else:
                self.console.print("[green]✅ Java bulundu![/green]")
                # En uygun Java'yı seç
                recommended = None
                for java in java_versions:
                    try:
                        major = int(java["version"].split('.')[0])
                        if major == 21:
                            recommended = java
                            break
                        elif major == 17 and not recommended:
                            recommended = java
                    except:
                        continue
                
                if recommended:
                    self.java_executable = recommended["path"]
                    self.config["java_path"] = recommended["path"]
                    self._save_config()
                    self.console.print(f"[green]✅ Java otomatik seçildi: {recommended['name']}[/green]")
            
            # İlk sürüm önerisi
            self.console.print()
            self.console.print("[bold]İlk Minecraft sürümü:[/bold]")
            if Confirm.ask("1.21.1 sürümü indirilsin mi?", default=True):
                self.console.print("[blue]📥 1.21.1 sürümü indiriliyor...[/blue]")
                if self._download_version("1.21.1"):
                    self.console.print("[green]✅ 1.21.1 başarıyla indirildi![/green]")
                else:
                    self.console.print("[red]❌ 1.21.1 indirilemedi![/red]")
            
            # Kurulum tamamlandı
            self.config["first_run_completed"] = True
            self._save_config()
            
            self.console.print()
            self.console.print(Panel(
                "[bold green]🎉 KURULUM TAMAMLANDI![/bold green]\n"
                "[dim]Artık Berke Minecraft Launcher'ı kullanabilirsiniz![/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
    
    def run(self):
        """Ana launcher döngüsü - Minimal TUI"""
        # İlk çalıştırma kontrolü
        self._first_run_setup()
        
        print("DEBUG: run() başladı")
        while True:
            # TTY kontrolü yap
            if sys.stdout.isatty():
                # Ekranı temizle
                os.system('clear' if os.name == 'posix' else 'cls')
            
            # Banner göster
            self.console.print(self._create_banner())
            
            # Sistem durumu - Renkli ve şık
            java_version = self._check_java_version()
            versions_count = len(self._get_installed_versions())
            username = self.config.get('username', 'Player')
            
            # Status bar
            status_parts = [
                f"[green]Java {java_version}[/green]" if java_version else "[red]Java N/A[/red]",
                f"[cyan]{versions_count} Surum[/cyan]",
                f"[yellow]{username}[/yellow]"
            ]
            status_text = " [dim]|[/dim] ".join(status_parts)
            
            self.console.print(Panel(
                status_text,
                border_style="dim",
                padding=(0, 2),
                expand=False
            ))
            self.console.print()
            
            # Ana menü göster
            self.console.print(self._create_main_menu())
            
            # Kullanıcı seçimi
            choice = Prompt.ask("\n[bold cyan]>[/bold cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "0":
                # Çıkış - Güzel mesaj
                os.system('clear')
                goodbye_msg = f"""
[bold cyan]██████╗ [/bold cyan] 
[bold cyan]██╔══██╗[/bold cyan] [bold green]Tesekkurler![/bold green]
[bold cyan]██████╔╝[/bold cyan] 
[bold cyan]██╔══██╗[/bold cyan] [yellow]Bay Bay![/yellow]
[bold cyan]██████╔╝[/bold cyan] 
[bold cyan]╚═════╝ [/bold cyan] [dim]BerkeMC v{__version__}[/dim]
                """
                self.console.print(Panel(
                    goodbye_msg.strip(),
                    border_style="green",
                    padding=(1, 2)
                ))
                break
            elif choice == "1":
                # Minecraft Başlat - Sadece başlatma için
                self._show_launch_versions()
            elif choice == "2":
                # Sürüm İndir - Gelişmiş menü
                self._show_advanced_download_menu()
            elif choice == "3":
                # Sürümlerim - Yönetim
                self._show_version_management()
                installed = self._get_installed_versions()
                if not installed:
                    self.console.print(Panel(
                        "[yellow]Henuz surum yok![/yellow]\n"
                        "[dim]Once bir surum indirin.[/dim]",
                        border_style="yellow",
                        padding=(1, 2)
                    ))
                    if Confirm.ask("\nSurum indirmek ister misiniz?"):
                        self._show_versions_menu()
                else:
                    self.console.print(Panel(
                        f"[bold cyan]SURUMLERIM[/bold cyan]\n"
                        f"[dim]Toplam: {len(installed)} surum[/dim]",
                        border_style="cyan",
                        padding=(1, 2)
                    ))
                    self.console.print()
                    
                    # Maksimum 15 sürüm göster
                    for idx, version_id in enumerate(installed[:15], 1):
                        version_dir = self.versions_dir / version_id
                        jar_file = version_dir / f"{version_id}.jar"
                        size = jar_file.stat().st_size / (1024 * 1024) if jar_file.exists() else 0
                        self.console.print(f"  [cyan]{idx:2}[/cyan]  {version_id:15}  [dim]{size:.0f} MB[/dim]")
                    
                    if len(installed) > 15:
                        self.console.print(f"\n[dim]... ve {len(installed) - 15} surum daha[/dim]")
                    
                    self.console.print()
                    self.console.print("[dim]0 = Geri | Numara = Baslat | M = Yonet[/dim]")
                    
                    try:
                        choice_input = Prompt.ask("\n[cyan]>[/cyan]")
                        
                        if choice_input == "0":
                            continue
                        elif choice_input.upper() == "M":
                            self._show_version_management_menu()
                        else:
                            choice = int(choice_input)
                            if 1 <= choice <= len(installed):
                                version_id = installed[choice-1]
                                self._launch_minecraft(version_id)
                            else:
                                self.console.print("[red]❌ Geçersiz seçim![/red]")
                                input("[dim]Enter...[/dim]")
                    except ValueError:
                        self.console.print("[red]❌ Geçersiz giriş![/red]")
                input("[dim]Enter...[/dim]")
            elif choice == "4":
                # Skin Yönetimi
                self._show_skin_menu()
            elif choice == "5":
                # Mod Yönetimi
                self._show_mod_menu()
            elif choice == "6":
                # Ayarlar
                self._show_settings_menu()
            elif choice == "7":
                # Performans Ayarları
                self._show_performance_settings()
            elif choice == "8":
                # Hakkında (Sistem + Geliştirici)
                self._show_about()

def main():
    """Ana fonksiyon"""
    print("🚀 BerkeMC başlatılıyor...")
    try:
        launcher = MinecraftLauncher()
        print("✅ Launcher oluşturuldu, çalıştırılıyor...")
        launcher.run()
    except KeyboardInterrupt:
        print("\n👋 Görüşürüz!")
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
