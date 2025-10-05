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
            "/usr/lib/jvm/java-17-openjdk/bin/java",
            "/usr/lib/jvm/java-21-openjdk/bin/java",
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
            version_match = re.search(r'version "(\d+)', version_output)
            if version_match:
                java_version = int(version_match.group(1))
                return java_version
            return None
        except Exception as e:
            self.console.print(f"[red]Java sürüm kontrolü başarısız: {e}[/red]")
            return None
    
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
        logo = """
[bold cyan]██████╗ [/bold cyan] [bold white]BERKE MINECRAFT LAUNCHER[/bold white]
[bold cyan]██╔══██╗[/bold cyan] [dim]v2.3.0 - Ultra Fast Edition[/dim]
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
            
            response = session.get(url, stream=True, timeout=30)
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
            
            # Sürüm JSON'unu indir
            version_json_path = version_dir / f"{version_id}.json"
            if not self._download_file(version_info["url"], version_json_path, f"{version_id} JSON"):
                return False
            
            # Sürüm JSON'unu oku
            try:
                with open(version_json_path, 'r') as f:
                    version_data = json.load(f)
            except json.JSONDecodeError:
                self.console.print(f"[red]Sürüm JSON'u okunamadı: {version_id}[/red]")
                return False
            
            # Client JAR'ı indir (eski sürümler için hata yakalama)
            try:
                client_jar_url = version_data["downloads"]["client"]["url"]
                client_jar_path = version_dir / f"{version_id}.jar"
                if not self._download_file(client_jar_url, client_jar_path, f"{version_id} Client"):
                    return False
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
        """İndirilen sürümleri listele"""
        versions = []
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                jar_file = version_dir / f"{version_dir.name}.jar"
                if jar_file.exists():
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
            "GDK_BACKEND": "x11",  # XWayland kullan
            "QT_QPA_PLATFORM": "xcb",  # Qt için X11
            "SDL_VIDEODRIVER": "x11",  # SDL için X11
            "MOZ_ENABLE_WAYLAND": "0",  # Firefox için X11
            "_JAVA_AWT_WM_NONREPARENTING": "1",  # Java AWT için
            "AWT_TOOLKIT": "MToolkit",  # Java AWT toolkit
            "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false"  # Headless modu kapat
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
            
            # LWJGL Native Library Path
            f"-Dorg.lwjgl.librarypath={self.versions_dir.parent / 'libraries'}",
            
            # Minecraft Özel Optimizasyonlar + Online Server Support
            "-Dminecraft.launcher.brand=berke-ultra-launcher",
            "-Dminecraft.launcher.version=2.3.0",
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
            "--assetsDir", str(self.minecraft_dir.parent / "assets"),
        ]
        
        # Asset index (eski sürümlerde olmayabilir)
        if "assetIndex" in version_data:
            minecraft_args.extend(["--assetIndex", version_data["assetIndex"]["id"]])
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
    
    def _launch_minecraft(self, version_id: str):
        """Minecraft'ı başlat"""
        try:
            self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {version_id}[/yellow]")
            
            # Java sürüm kontrolü
            java_version = self._check_java_version()
            if java_version and java_version < 17:
                self.console.print(f"[red]⚠️ Java Sürüm Uyarısı![/red]")
                self.console.print(f"[yellow]Mevcut Java sürümü: {java_version}[/yellow]")
                self.console.print(f"[yellow]Minecraft için Java 17+ gerekli![/yellow]")
                self.console.print(f"[cyan]Çözüm: sudo pacman -S jdk17-openjdk[/cyan]")
            elif java_version and java_version > 21:
                self.console.print(f"[yellow]⚠️ Java Sürüm Uyarısı![/yellow]")
                self.console.print(f"[yellow]Mevcut Java sürümü: {java_version} (Beta)[/yellow]")
                self.console.print(f"[yellow]Minecraft için Java 17-21 önerilir![/yellow]")
                self.console.print(f"[cyan]Çözüm: sudo pacman -S jdk17-openjdk[/cyan]")
                
                if not Confirm.ask("Yine de devam etmek istiyor musunuz?"):
                    return
            
            # Önce sistem kontrolü yap
            self._pre_launch_check()
            
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
                "MESA_GL_VERSION_OVERRIDE": "3.3",
                "MESA_GLSL_VERSION_OVERRIDE": "330",
                "LIBGL_ALWAYS_SOFTWARE": "0",
                "LIBGL_ALWAYS_INDIRECT": "0",
                "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false"
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
        """Detaylı hata mesajı göster"""
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
            
            # Minimal menü
            self.console.print("  [cyan]1[/cyan]  URL'den Indir")
            self.console.print("  [cyan]2[/cyan]  Kullanici Adindan Indir")
            self.console.print("  [cyan]3[/cyan]  Yerel Dosya Yukle")
            self.console.print("  [cyan]4[/cyan]  Populer Skinler")
            self.console.print("  [cyan]5[/cyan]  Mevcut Skinler")
            self.console.print("  [cyan]6[/cyan]  Skin Sec")
            self.console.print("  [cyan]7[/cyan]  Skin Sil")
            self.console.print("  [cyan]8[/cyan]  Yedekle/Geri Yukle")
            self.console.print()
            self.console.print("  [dim]0[/dim]  Geri")
            
            choice = Prompt.ask("\n[cyan]>[/cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                url = Prompt.ask("Skin URL'ini girin")
                name = Prompt.ask("Skin adını girin")
                self._download_skin_from_url(url, name)
                input("[dim]Enter...[/dim]")
            elif choice == "2":
                username = Prompt.ask("Minecraft kullanıcı adını girin")
                self._download_skin_from_username(username)
                input("[dim]Enter...[/dim]")
            elif choice == "3":
                self._upload_local_skin()
            elif choice == "4":
                self._show_popular_skins()
            elif choice == "5":
                self._show_available_skins()
            elif choice == "6":
                self._select_skin()
            elif choice == "7":
                self._delete_skin()
            elif choice == "8":
                self._skin_backup_menu()
            elif choice == "0":
                break
    
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
            self.console.print(f"  [cyan]1[/cyan]  Kullanici Adi        [dim]{self.config['username']}[/dim]")
            self.console.print(f"  [cyan]2[/cyan]  Bellek               [dim]{self.config['memory']} GB[/dim]")
            self.console.print(f"  [cyan]3[/cyan]  Pencere Boyutu       [dim]{self.config['window_width']}x{self.config['window_height']}[/dim]")
            self.console.print(f"  [cyan]4[/cyan]  Tam Ekran            [dim]{'Evet' if self.config['fullscreen'] else 'Hayir'}[/dim]")
            self.console.print(f"  [cyan]5[/cyan]  Grafik Opt.          [dim]{'Acik' if self.config['optimize_graphics'] else 'Kapali'}[/dim]")
            self.console.print(f"  [cyan]6[/cyan]  Mod Destegi          [dim]{'Acik' if self.config['enable_mods'] else 'Kapali'}[/dim]")
            self.console.print()
            self.console.print(f"  [cyan]7[/cyan]  Java Yolu")
            self.console.print(f"  [cyan]8[/cyan]  Java Guncelle")
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
            elif choice == "3":
                width = int(Prompt.ask("Pencere genişliği", default=str(self.config["window_width"])))
                height = int(Prompt.ask("Pencere yüksekliği", default=str(self.config["window_height"])))
                self.config["window_width"] = width
                self.config["window_height"] = height
                self._save_config()
                self.console.print(f"[green]✅ Pencere boyutu güncellendi: {width}x{height}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "4":
                self.config["fullscreen"] = not self.config["fullscreen"]
                self._save_config()
                self.console.print(f"[green]✅ Tam ekran: {'Açık' if self.config['fullscreen'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "5":
                self.config["optimize_graphics"] = not self.config["optimize_graphics"]
                self._save_config()
                self.console.print(f"[green]✅ Grafik optimizasyonu: {'Açık' if self.config['optimize_graphics'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "6":
                self.config["enable_mods"] = not self.config["enable_mods"]
                self._save_config()
                self.console.print(f"[green]✅ Mod desteği: {'Açık' if self.config['enable_mods'] else 'Kapalı'}[/green]")
                input("[dim]Enter...[/dim]")
            elif choice == "7":
                self._configure_java_path()
            elif choice == "8":
                # Java otomatik güncelleme
                self._auto_update_java()
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
        """Mod menüsünü göster - MINIMAL"""
        while True:
            os.system('clear')
            
            # Mod dizinini oluştur
            mods_dir = self.minecraft_dir / "mods"
            mods_dir.mkdir(exist_ok=True)
            
            # Yüklü modları say
            installed_mods = list(mods_dir.glob("*.jar"))
            mod_count = len(installed_mods)
            
            # Banner
            self.console.print(Panel(
                f"[bold cyan]MOD YONETIMI[/bold cyan]\n"
                f"[white]Yuklu: {mod_count} mod[/white]\n"
                f"[dim]Modrinth API[/dim]",
                border_style="cyan",
                padding=(1, 2)
            ))
            
            self.console.print()
            
            # Minimal liste
            table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
            table.add_column("", style="bold cyan", width=3, justify="center")
            table.add_column("", style="white", width=25)
            table.add_column("", style="dim", width=30)
            
            table.add_row("[bold cyan]1[/bold cyan]", "[green]Mod Ara[/green]", "[dim]Modrinth'ten indir[/dim]")
            table.add_row("[bold cyan]2[/bold cyan]", "[green]Yuklu Modlar[/green]", f"[dim]{mod_count} adet[/dim]")
            table.add_row("[bold cyan]3[/bold cyan]", "[blue]Yerel Mod Yukle[/blue]", "[dim]Dosyadan ekle[/dim]")
            table.add_row("[bold cyan]4[/bold cyan]", "[red]Mod Sil[/red]", "[dim]Kaldır[/dim]")
            table.add_row("[bold cyan]5[/bold cyan]", "[yellow]Populer Modlar[/yellow]", "[dim]Top 20[/dim]")
            table.add_row("", "", "")
            table.add_row("[bold red]0[/bold red]", "[red]Geri[/red]", "[dim]Ana menu[/dim]")
            
            self.console.print(Panel(
                table,
                title="[bold white]═══ MENU ═══[/bold white]",
                border_style="bright_cyan",
                padding=(1, 2),
                expand=False
            ))
            
            choice = Prompt.ask("\n[bold cyan]>[/bold cyan]", choices=["0", "1", "2", "3", "4", "5"])
            
            if choice == "0":
                break
            elif choice == "1":
                self._search_and_download_mod()
            elif choice == "2":
                self._show_installed_mods()
            elif choice == "3":
                self._upload_local_mod()
            elif choice == "4":
                self._delete_mod()
            elif choice == "5":
                self._show_popular_mods()
    
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
            "[white]v2.3.0 - Terminal Edition[/white]\n"
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
        info_table.add_row("Platform", "Arch Linux", "Launcher", "v2.3.0")
        
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
        """Forge yükle"""
        self.console.print(f"\n[cyan]Forge yükleniyor: {version_id}[/cyan]")
        
        try:
            # Forge installer'ı indir
            forge_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version_id}/forge-{version_id}-installer.jar"
            
            self.console.print("[cyan]Forge installer indiriliyor...[/cyan]")
            
            response = requests.get(forge_url, timeout=30)
            response.raise_for_status()
            
            installer_path = self.versions_dir / f"forge-installer-{version_id}.jar"
            with open(installer_path, 'wb') as f:
                f.write(response.content)
            
            # Forge'u yükle
            self.console.print("[cyan]Forge yükleniyor...[/cyan]")
            
            import subprocess
            result = subprocess.run([
                self.java_executable,
                "-jar", str(installer_path),
                "--installServer"
            ], capture_output=True, text=True, cwd=str(self.versions_dir / version_id))
            
            if result.returncode == 0:
                self.console.print("[green]✅ Forge başarıyla yüklendi![/green]")
                
                # Installer'ı sil
                installer_path.unlink(missing_ok=True)
                
                input("[dim]Enter...[/dim]")
            else:
                self.console.print(f"[red]❌ Forge yüklenemedi: {result.stderr}[/red]")
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
            f"[bold cyan]MINECRAFT BASLAT[/bold cyan]\n"
            f"[dim]Yuklu surumler: {len(versions)}[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))
        
        self.console.print()
        
        # Minimal liste
        for i, version in enumerate(versions, 1):
            version_dir = self.versions_dir / version
            jar_file = version_dir / f"{version}.jar"
            
            if jar_file.exists():
                size_mb = round(jar_file.stat().st_size / (1024*1024), 1)
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [dim]{size_mb:.0f} MB[/dim]")
            else:
                self.console.print(f"  [cyan]{i}[/cyan]  {version:15}  [red]Eksik[/red]")
        
        self.console.print("\n[dim]0 = Geri | Numara = Baslat[/dim]")
        
        try:
            choice = int(Prompt.ask("\n[cyan]>[/cyan]"))
            
            if choice == 0:
                return
            
            if 1 <= choice <= len(versions):
                version_id = versions[choice-1]
                
                # Direkt başlat
                self._launch_minecraft(version_id)
            else:
                self.console.print("\n[red]Gecersiz secim![/red]\n")
                input("[dim]Enter...[/dim]")
        except ValueError:
            self.console.print("\n[red]Gecersiz giris![/red]\n")
            input("[dim]Enter...[/dim]")
    
    def run(self):
        """Ana launcher döngüsü - Minimal TUI"""
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
                goodbye_msg = """
[bold cyan]██████╗ [/bold cyan] 
[bold cyan]██╔══██╗[/bold cyan] [bold green]Tesekkurler![/bold green]
[bold cyan]██████╔╝[/bold cyan] 
[bold cyan]██╔══██╗[/bold cyan] [yellow]Iyi oyunlar![/yellow]
[bold cyan]██████╔╝[/bold cyan] 
[bold cyan]╚═════╝ [/bold cyan] [dim]Berke Minecraft Launcher v2.3[/dim]
                """
                self.console.print(Panel(
                    goodbye_msg.strip(),
                    border_style="green",
                    padding=(1, 2)
                ))
                break
            elif choice == "1":
                # Minecraft Başlat
                self._show_installed_versions()
            elif choice == "2":
                # Sürüm İndir
                self._show_versions_menu()
            elif choice == "3":
                # Sürümlerim - Kompakt
                os.system('clear')
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
