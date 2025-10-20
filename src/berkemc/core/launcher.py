"""
Enhanced Minecraft Launcher with keyboard navigation and improved UI
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

# Import our modules
from ..ui import KeyboardNavigator, MenuItem, ColorManager, ProgressDisplay
from ..managers import SkinManager, ModManager, PerformanceManager
from ..utils import SystemUtils, FileUtils, NetworkUtils, ValidationUtils

# Version info
try:
    from version import __version__, get_full_version_string
except ImportError:
    __version__ = "4.0.0"
    def get_full_version_string():
        return f"BerkeMC v{__version__}"

# i18n system
try:
    from i18n import I18n, t as i18n_t, set_language, get_current_language
    _i18n_available = True
except ImportError:
    _i18n_available = False
    def i18n_t(key, **kwargs):
        return key

# Initialize colorama
colorama.init(autoreset=True)

class MinecraftLauncher:
    """Enhanced Minecraft Launcher with keyboard navigation"""
    
    def __init__(self):
        # Terminal control
        if sys.stdout.isatty():
            self.console = Console(width=120)
        else:
            self.console = Console(force_terminal=False, legacy_windows=False)
        
        # Directories
        self.home_dir = Path.home()
        self.minecraft_dir = self.home_dir / ".minecraft"
        self.launcher_dir = self.home_dir / ".berke_minecraft_launcher"
        self.versions_dir = self.launcher_dir / "versions"
        self.skins_dir = self.launcher_dir / "skins"
        self.cache_dir = self.launcher_dir / "cache"
        self.config_file = self.launcher_dir / "config.json"
        
        # Ensure directories exist
        FileUtils.ensure_directory(self.minecraft_dir)
        FileUtils.ensure_directory(self.launcher_dir)
        FileUtils.ensure_directory(self.versions_dir)
        FileUtils.ensure_directory(self.skins_dir)
        FileUtils.ensure_directory(self.cache_dir)
        
        # Find Java
        self.java_executable = SystemUtils.find_java()
        
        # Load config
        self.config = self._load_config()
        
        # Load i18n language
        if _i18n_available:
            lang = self.config.get("language", "tr")
            set_language(lang)
        
        # Initialize managers
        self.skin_manager = SkinManager(self.console, self.skins_dir)
        self.mod_manager = ModManager(self.console, self.minecraft_dir)
        self.performance_manager = PerformanceManager(self.console)
        
        # Initialize UI components
        self.navigator = KeyboardNavigator(self.console)
        self.color_manager = ColorManager()
        self.progress_display = ProgressDisplay(self.console)
        
        # Minecraft API URLs
        self.version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        self.assets_url = "https://resources.download.minecraft.net"
        self.skin_api_url = "https://api.mojang.com/users/profiles/minecraft"
    
    def _load_config(self) -> Dict:
        """Load configuration file"""
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
                # Add missing keys
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
        """Save configuration file"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_banner(self) -> Panel:
        """Create banner with proper color formatting"""
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
            border_style="bright_cyan",
            padding=(1, 2),
            expand=False
        )
    
    def _create_status_bar(self) -> Panel:
        """Create status bar with system info"""
        java_version = SystemUtils.check_java_version(self.java_executable) if self.java_executable else None
        versions_count = len(self._get_installed_versions())
        username = self.config.get('username', 'Player')
        
        # Status parts with proper color formatting
        status_parts = []
        if java_version:
            status_parts.append(f"[green]Java {java_version}[/green]")
        else:
            status_parts.append("[red]Java N/A[/red]")
        
        status_parts.append(f"[cyan]{versions_count} Sürüm[/cyan]")
        status_parts.append(f"[yellow]{username}[/yellow]")
        
        status_text = " [dim]|[/dim] ".join(status_parts)
        
        return Panel(
            status_text,
            border_style="dim",
            padding=(0, 2),
            expand=False
        )
    
    def _create_main_menu_items(self) -> List[MenuItem]:
        """Create main menu items for keyboard navigation"""
        items = []
        
        # Main functions - Green
        items.append(MenuItem(
            "1",
            "Minecraft Başlat",
            "Oyunu başlat",
            callback=self._launch_minecraft_callback,
            color="green"
        ))
        
        items.append(MenuItem(
            "2", 
            "Sürüm İndir",
            "Yeni sürüm yükle",
            callback=self._download_version_callback,
            color="green"
        ))
        
        items.append(MenuItem(
            "3",
            "Sürümlerim",
            "Yüklü sürümleri gör",
            callback=self._manage_versions_callback,
            color="green"
        ))
        
        # Customization - Blue
        items.append(MenuItem(
            "4",
            "Skin Yönetimi",
            "Karakter görüntüsünü değiştir",
            callback=self._skin_management_callback,
            color="blue"
        ))
        
        items.append(MenuItem(
            "5",
            "Mod Yönetimi", 
            "Modları ara ve yükle",
            callback=self._mod_management_callback,
            color="blue"
        ))
        
        # System - Yellow
        items.append(MenuItem(
            "6",
            "Ayarlar",
            "Launcher ayarlarını düzenle",
            callback=self._settings_callback,
            color="yellow"
        ))
        
        items.append(MenuItem(
            "7",
            "Performans",
            "Sistem kaynaklarını izle",
            callback=self._performance_callback,
            color="yellow"
        ))
        
        items.append(MenuItem(
            "8",
            "Hakkında",
            "Launcher hakkında bilgi",
            callback=self._about_callback,
            color="yellow"
        ))
        
        return items
    
    def _launch_minecraft_callback(self):
        """Callback for launching Minecraft"""
        self._show_launch_versions()
        return None
    
    def _download_version_callback(self):
        """Callback for downloading versions"""
        self._show_advanced_download_menu()
        return None
    
    def _manage_versions_callback(self):
        """Callback for managing versions"""
        self._show_version_management()
        return None
    
    def _skin_management_callback(self):
        """Callback for skin management"""
        self._show_skin_menu()
        return None
    
    def _mod_management_callback(self):
        """Callback for mod management"""
        self._show_mod_menu()
        return None
    
    def _settings_callback(self):
        """Callback for settings"""
        self._show_settings_menu()
        return None
    
    def _performance_callback(self):
        """Callback for performance monitoring"""
        self._show_performance_menu()
        return None
    
    def _about_callback(self):
        """Callback for about"""
        self._show_about()
        return None
    
    def _show_skin_menu(self):
        """Show skin management menu with keyboard navigation"""
        os.system('clear')
        
        # Create menu items
        items = self.skin_manager.create_skin_menu_items(self.navigator)
        
        # Show menu
        self.navigator.show_menu("SKIN YÖNETİMİ", items, show_exit=True)
    
    def _show_mod_menu(self):
        """Show mod management menu with keyboard navigation"""
        os.system('clear')
        
        # Create menu items
        items = self.mod_manager.create_mod_menu_items(self.navigator)
        
        # Show menu
        self.navigator.show_menu("MOD YÖNETİMİ", items, show_exit=True)
    
    def _show_performance_menu(self):
        """Show performance monitoring menu"""
        os.system('clear')
        
        items = [
            MenuItem(
                "1",
                "Canlı Performans",
                "Gerçek zamanlı sistem izleme",
                callback=self._show_live_performance,
                color="green"
            ),
            MenuItem(
                "2",
                "Sistem Bilgileri",
                "Detaylı sistem bilgileri",
                callback=self._show_system_info,
                color="blue"
            ),
            MenuItem(
                "3",
                "Minecraft Önerileri",
                "Sistem için optimizasyon önerileri",
                callback=self._show_minecraft_recommendations,
                color="yellow"
            )
        ]
        
        self.navigator.show_menu("PERFORMANS İZLEME", items, show_exit=True)
    
    def _show_live_performance(self):
        """Show live performance monitoring"""
        self.performance_manager.show_performance_dashboard()
        return None
    
    def _show_system_info(self):
        """Show detailed system information"""
        os.system('clear')
        
        info = self.performance_manager.get_system_info()
        if info:
            table = self.performance_manager.create_detailed_info_table(info)
            self.console.print(table)
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_minecraft_recommendations(self):
        """Show Minecraft performance recommendations"""
        os.system('clear')
        
        recommendations = self.performance_manager.get_minecraft_recommendations()
        
        table = Table(title="Minecraft Performans Önerileri", show_header=True, header_style="bold cyan")
        table.add_column("Öneri", style="white", width=60)
        
        for rec in recommendations:
            table.add_row(rec)
        
        self.console.print(table)
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _get_installed_versions(self) -> List[str]:
        """Get list of installed versions"""
        versions = []
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                jar_file = version_dir / f"{version_dir.name}.jar"
                if jar_file.exists():
                    versions.append(version_dir.name)
        return sorted(versions, reverse=True)
    
    def _show_launch_versions(self):
        """Show versions for launching with keyboard navigation"""
        os.system('clear')
        
        installed = self._get_installed_versions()
        if not installed:
            self.console.print(Panel(
                "[yellow]Henüz sürüm yok![/yellow]\n"
                "[dim]Önce bir sürüm indirin.[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            if Confirm.ask("\nSürüm indirmek ister misiniz?"):
                self._show_advanced_download_menu()
            return
        
        # Create menu items for versions
        items = []
        for i, version_id in enumerate(installed[:20], 1):  # Limit to 20 versions
            version_dir = self.versions_dir / version_id
            jar_file = version_dir / f"{version_id}.jar"
            size = jar_file.stat().st_size / (1024 * 1024) if jar_file.exists() else 0
            
            items.append(MenuItem(
                str(i),
                version_id,
                f"{size:.0f} MB",
                callback=lambda v=version_id: self._launch_version_callback(v),
                color="cyan"
            ))
        
        self.navigator.show_menu("SÜRÜM SEÇ", items, show_exit=True)
    
    def _launch_version_callback(self, version_id: str):
        """Callback for launching specific version"""
        self._launch_minecraft(version_id)
        return None
    
    def _launch_minecraft(self, version_id: str):
        """Launch Minecraft with specified version - Original working code"""
        try:
            self.console.print(f"[yellow]🚀 Minecraft başlatılıyor: {version_id}[/yellow]")
            
            # Check if Java is available
            if not self.java_executable:
                self.console.print("[red]❌ Java bulunamadı! Minecraft başlatılamaz.[/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
                return
            
            # Check if version exists
            version_dir = self.versions_dir / version_id
            jar_file = version_dir / f"{version_id}.jar"
            
            if not jar_file.exists():
                self.console.print(f"[red]❌ {version_id} sürümü bulunamadı![/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
                return
            
            # Pre-launch check
            self._pre_launch_check()
            
            # Create launch command
            command, env_vars = self._create_launch_command(version_id)
            
            # Prepare environment
            import os
            current_env = os.environ.copy()
            current_env.update(env_vars)
            
            # Wayland/Hyprland support
            if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                self.console.print("[blue]🖥️ Wayland/Hyprland tespit edildi, XWayland kullanılıyor...[/blue]")
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
            
            # Minecraft environment variables
            current_env.update({
                "MESA_GL_VERSION_OVERRIDE": "4.5",
                "MESA_GLSL_VERSION_OVERRIDE": "450",
                "LIBGL_ALWAYS_SOFTWARE": "0",
                "LIBGL_ALWAYS_INDIRECT": "0",
                "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false",
                "vblank_mode": "0",
                "__GL_THREADED_OPTIMIZATIONS": "1",
                "MESA_NO_ERROR": "1"
            })
            
            # Launch Minecraft
            self.console.print("[blue]🚀 Minecraft başlatılıyor...[/blue]")
            
            # Create log file
            log_dir = self.launcher_dir / "logs"
            log_dir.mkdir(exist_ok=True)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"minecraft_{version_id}_{timestamp}.log"
            
            # Start Minecraft process
            import subprocess
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    env=current_env,
                    start_new_session=True
                )
            
            # Wait a bit and check if process is still running
            import time
            time.sleep(3)
            
            if process.poll() is None:
                # Success - show monitoring
                self.console.print("[green]✅ Minecraft başlatıldı![/green]")
                self.console.print(f"[blue]📋 Sürüm: {version_id}[/blue]")
                self.console.print(f"[blue]🔢 Process ID: {process.pid}[/blue]")
                self.console.print("[yellow]💡 Minecraft penceresi açılmasını bekleyin...[/yellow]")
                self.console.print("[dim]Oyunu kapatmak için Ctrl+C tuşlarına basın.[/dim]")
                
                # Show game monitor
                self._show_game_monitor(process, version_id, log_file)
            else:
                # Error occurred
                try:
                    with open(log_file, 'r') as log:
                        log_content = log.read()
                except:
                    log_content = "Log dosyası okunamadı"
                
                self.console.print("[red]❌ Minecraft başlatılamadı![/red]")
                self.console.print(f"[red]Hata logu: {log_content[:500]}...[/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Başlatma hatası: {e}[/red]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
    
    def _pre_launch_check(self):
        """Pre-launch system check"""
        self.console.print("[blue]🔍 Sistem kontrolü yapılıyor...[/blue]")
        
        # Java check
        if not self.java_executable:
            raise Exception("Java bulunamadı! Lütfen Java'yı yükleyin: sudo pacman -S jdk21-openjdk")
        
        # Java version check
        try:
            import subprocess
            result = subprocess.run([self.java_executable, "-version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Java sürüm kontrolü başarısız")
        except Exception as e:
            raise Exception(f"Java kontrolü başarısız: {e}")
        
        self.console.print("[green]✅ Sistem kontrolü tamamlandı[/green]")
    
    def _create_launch_command(self, version_id: str):
        """Create launch command for Minecraft"""
        # Get memory setting
        memory = self.config.get('memory', 'auto')
        if memory == 'auto':
            try:
                import psutil
                total_memory = psutil.virtual_memory().total
                memory_mb = min(int(total_memory * 0.25 / (1024**2)), 4096)
                memory = f"{memory_mb}M"
            except:
                memory = "2048M"
        
        # Build Java command
        command = [
            self.java_executable,
            f"-Xmx{memory}",
            f"-Xms{memory}",
            "-XX:+UseG1GC",
            "-XX:+ParallelRefProcEnabled",
            "-XX:MaxGCPauseMillis=200",
            "-XX:+UnlockExperimentalVMOptions",
            "-XX:+DisableExplicitGC",
            "-XX:+AlwaysPreTouch",
            "-XX:G1NewSizePercent=30",
            "-XX:G1MaxNewSizePercent=40",
            "-XX:G1HeapRegionSize=8M",
            "-XX:G1ReservePercent=20",
            "-XX:G1HeapWastePercent=5",
            "-XX:G1MixedGCCountTarget=4",
            "-XX:InitiatingHeapOccupancyPercent=15",
            "-XX:G1MixedGCLiveThresholdPercent=90",
            "-XX:G1RSetUpdatingPauseTimePercent=5",
            "-XX:SurvivorRatio=32",
            "-XX:+PerfDisableSharedMem",
            "-XX:MaxTenuringThreshold=1",
            "-Dusing.aikars.flags=https://mcflags.emc.gs",
            "-Daikars.new.flags=true"
        ]
        
        # Add custom Java arguments
        custom_args = self.config.get('java_args', [])
        command.extend(custom_args)
        
        # Add Minecraft JAR
        version_dir = self.versions_dir / version_id
        jar_file = version_dir / f"{version_id}.jar"
        command.extend(["-jar", str(jar_file)])
        
        # Add username
        username = self.config.get('username', 'BerkePlayer')
        command.extend(["--username", username])
        
        # Add window size
        width = self.config.get('window_width', 1280)
        height = self.config.get('window_height', 720)
        command.extend(["--width", str(width), "--height", str(height)])
        
        # Environment variables
        env_vars = {
            "MESA_GL_VERSION_OVERRIDE": "4.5",
            "MESA_GLSL_VERSION_OVERRIDE": "450",
            "LIBGL_ALWAYS_SOFTWARE": "0",
            "LIBGL_ALWAYS_INDIRECT": "0",
            "JAVA_TOOL_OPTIONS": "-Djava.awt.headless=false"
        }
        
        return command, env_vars
    
    def _show_game_monitor(self, process, version_id: str, log_file):
        """Show game monitoring screen"""
        try:
            import psutil
            import time
            
            self.console.print("[green]🎮 Minecraft çalışıyor - Kaynak izleme[/green]")
            self.console.print("[dim]Ctrl+C ile çıkış yapabilirsiniz[/dim]")
            
            while process.poll() is None:
                try:
                    # Get process info
                    proc = psutil.Process(process.pid)
                    cpu_percent = proc.cpu_percent()
                    memory_info = proc.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    
                    # Clear screen and show info
                    os.system('clear')
                    
                    # Create monitoring table
                    table = Table(title=f"Minecraft {version_id} - Kaynak İzleme", show_header=True, header_style="bold cyan")
                    table.add_column("Metrik", style="cyan", width=20)
                    table.add_column("Değer", style="white", width=20)
                    table.add_column("Durum", style="green", width=20)
                    
                    table.add_row("CPU Kullanımı", f"{cpu_percent:.1f}%", "🟢 OK" if cpu_percent < 80 else "🟡 Yüksek")
                    table.add_row("RAM Kullanımı", f"{memory_mb:.0f} MB", "🟢 OK" if memory_mb < 2048 else "🟡 Yüksek")
                    table.add_row("Process ID", str(process.pid), "🟢 Aktif")
                    table.add_row("Log Dosyası", log_file.name, "🟢 Kaydediliyor")
                    
                    self.console.print(table)
                    self.console.print(f"\n[dim]Son güncelleme: {time.strftime('%H:%M:%S')}[/dim]")
                    self.console.print("[dim]Ctrl+C ile çıkış[/dim]")
                    
                    time.sleep(2)
                    
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]⚠️ Minecraft kapatılıyor...[/yellow]")
                    process.terminate()
                    process.wait()
                    self.console.print("[green]✅ Minecraft kapatıldı.[/green]")
                    break
                except Exception as e:
                    self.console.print(f"[red]Monitoring hatası: {e}[/red]")
                    break
            
            if process.poll() is not None:
                self.console.print("[yellow]⚠️ Minecraft kapandı.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Monitoring hatası: {e}[/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
    
    def _show_advanced_download_menu(self):
        """Show advanced download menu"""
        os.system('clear')
        
        items = [
            MenuItem(
                "1",
                "Popüler Sürümler",
                "En popüler Minecraft sürümleri",
                callback=self._show_popular_versions,
                color="green"
            ),
            MenuItem(
                "2",
                "Sürüm Ara",
                "Belirli bir sürüm ara",
                callback=self._search_versions,
                color="blue"
            ),
            MenuItem(
                "3",
                "Tüm Sürümler",
                "Mevcut tüm sürümleri gör",
                callback=self._show_all_versions,
                color="yellow"
            )
        ]
        
        self.navigator.show_menu("SÜRÜM İNDİR", items, show_exit=True)
    
    def _show_popular_versions(self):
        """Show popular versions"""
        os.system('clear')
        
        popular_versions = [
            "1.20.4", "1.20.1", "1.19.4", "1.19.2", "1.18.2",
            "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.13.2"
        ]
        
        items = []
        for i, version in enumerate(popular_versions, 1):
            items.append(MenuItem(
                str(i),
                version,
                "Popüler sürüm",
                callback=lambda v=version: self._download_version_callback(v),
                color="green"
            ))
        
        self.navigator.show_menu("POPÜLER SÜRÜMLER", items, show_exit=True)
    
    def _search_versions(self):
        """Search for specific versions"""
        query = input("\n[cyan]Sürüm ara: [/cyan]").strip()
        if query:
            # Import VersionManager
            from ..core.version import VersionManager
            version_manager = VersionManager(self.console, self.versions_dir, self.cache_dir)
            
            # Search versions
            versions = version_manager.search_versions(query)
            if versions:
                items = []
                for i, version in enumerate(versions[:20], 1):
                    items.append(MenuItem(
                        str(i),
                        version['id'],
                        f"{version.get('type', 'Unknown')} - {version.get('releaseTime', '')[:10]}",
                        callback=lambda v=version['id']: self._download_version_callback(v),
                        color="cyan"
                    ))
                
                self.navigator.show_menu(f"'{query}' Arama Sonuçları", items, show_exit=True)
            else:
                self.console.print(f"[red]❌ '{query}' için sürüm bulunamadı![/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_all_versions(self):
        """Show all available versions"""
        # Import VersionManager
        from ..core.version import VersionManager
        version_manager = VersionManager(self.console, self.versions_dir, self.cache_dir)
        
        # Get all versions
        versions = version_manager.get_available_versions()
        if versions:
            # Show recent versions (last 50)
            recent_versions = versions[-50:]
            items = []
            for i, version in enumerate(recent_versions, 1):
                items.append(MenuItem(
                    str(i),
                    version['id'],
                    f"{version.get('type', 'Unknown')} - {version.get('releaseTime', '')[:10]}",
                    callback=lambda v=version['id']: self._download_version_callback(v),
                    color="blue"
                ))
            
            self.navigator.show_menu("TÜM SÜRÜMLER (Son 50)", items, show_exit=True)
        else:
            self.console.print("[red]❌ Sürümler yüklenemedi![/red]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _download_version_callback(self, version_id: str):
        """Callback for downloading version"""
        self.console.print(f"[green]📥 {version_id} indiriliyor...[/green]")
        
        # Import VersionManager
        from ..core.version import VersionManager
        version_manager = VersionManager(self.console, self.versions_dir, self.cache_dir)
        
        # Download version
        if version_manager.download_version(version_id):
            self.console.print(f"[green]✅ {version_id} başarıyla indirildi![/green]")
        else:
            self.console.print(f"[red]❌ {version_id} indirilemedi![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_version_management(self):
        """Show version management"""
        os.system('clear')
        
        installed = self._get_installed_versions()
        if not installed:
            self.console.print(Panel(
                "[yellow]Henüz sürüm yok![/yellow]\n"
                "[dim]Önce bir sürüm indirin.[/dim]",
                border_style="yellow",
                padding=(1, 2)
            ))
            return
        
        # Create menu items for installed versions
        items = []
        for i, version_id in enumerate(installed[:20], 1):
            version_dir = self.versions_dir / version_id
            jar_file = version_dir / f"{version_id}.jar"
            size = jar_file.stat().st_size / (1024 * 1024) if jar_file.exists() else 0
            
            items.append(MenuItem(
                str(i),
                version_id,
                f"{size:.0f} MB",
                callback=lambda v=version_id: self._manage_single_version_callback(v),
                color="cyan"
            ))
        
        self.navigator.show_menu("SÜRÜM YÖNETİMİ", items, show_exit=True)
    
    def _manage_single_version_callback(self, version_id: str):
        """Callback for managing single version"""
        self._show_single_version_menu(version_id)
        return None
    
    def _show_single_version_menu(self, version_id: str):
        """Show menu for single version management"""
        os.system('clear')
        
        items = [
            MenuItem(
                "1",
                "Başlat",
                f"Minecraft {version_id} başlat",
                callback=lambda: self._launch_version_callback(version_id),
                color="green"
            ),
            MenuItem(
                "2",
                "Bilgiler",
                f"{version_id} hakkında bilgi",
                callback=lambda: self._show_version_info_callback(version_id),
                color="blue"
            ),
            MenuItem(
                "3",
                "Sil",
                f"{version_id} sürümünü sil",
                callback=lambda: self._delete_version_callback(version_id),
                color="red"
            )
        ]
        
        self.navigator.show_menu(f"SÜRÜM: {version_id}", items, show_exit=True)
    
    def _show_version_info_callback(self, version_id: str):
        """Callback for showing version info"""
        os.system('clear')
        
        version_dir = self.versions_dir / version_id
        jar_file = version_dir / f"{version_id}.jar"
        
        if jar_file.exists():
            size = jar_file.stat().st_size / (1024 * 1024)
            modified = jar_file.stat().st_mtime
            
            table = Table(title=f"Sürüm Bilgileri: {version_id}", show_header=True, header_style="bold cyan")
            table.add_column("Özellik", style="cyan", width=20)
            table.add_column("Değer", style="white", width=30)
            
            table.add_row("Sürüm ID", version_id)
            table.add_row("Dosya Boyutu", f"{size:.1f} MB")
            table.add_row("Son Değişiklik", time.ctime(modified))
            
            self.console.print(table)
        else:
            self.console.print(f"[red]❌ {version_id} sürümü bulunamadı![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _delete_version_callback(self, version_id: str):
        """Callback for deleting version"""
        if Confirm.ask(f"\n[red]{version_id} sürümünü silmek istediğinizden emin misiniz?[/red]"):
            try:
                version_dir = self.versions_dir / version_id
                if version_dir.exists():
                    import shutil
                    shutil.rmtree(version_dir)
                    self.console.print(f"[green]✅ {version_id} sürümü silindi[/green]")
                else:
                    self.console.print(f"[red]❌ {version_id} sürümü bulunamadı![/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Silme hatası: {e}[/red]")
            
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_settings_menu(self):
        """Show settings menu with keyboard navigation"""
        os.system('clear')
        
        items = [
            MenuItem(
                "1",
                "Kullanıcı Adı",
                f"Mevcut: {self.config.get('username', 'BerkePlayer')}",
                callback=self._change_username_callback,
                color="cyan"
            ),
            MenuItem(
                "2",
                "Bellek Ayarları",
                f"Mevcut: {self.config.get('memory', 'auto')}",
                callback=self._change_memory_callback,
                color="blue"
            ),
            MenuItem(
                "3",
                "Pencere Boyutu",
                f"Mevcut: {self.config.get('window_width', 1280)}x{self.config.get('window_height', 720)}",
                callback=self._change_window_size_callback,
                color="green"
            ),
            MenuItem(
                "4",
                "Java Ayarları",
                "Java parametrelerini düzenle",
                callback=self._change_java_settings_callback,
                color="yellow"
            ),
            MenuItem(
                "5",
                "Java Yönetimi",
                "Java sürümlerini yönet",
                callback=self._show_java_management_menu,
                color="magenta"
            ),
            MenuItem(
                "6",
                "Sistem Testi",
                "Sistem uyumluluğunu test et",
                callback=self._show_system_test_menu,
                color="red"
            )
        ]
        
    def _show_java_management_menu(self):
        """Java management menu"""
        os.system('clear')
        
        # Get Java info
        java_info = SystemUtils.get_system_info()
        java_version = SystemUtils.check_java_version(self.java_executable) if self.java_executable else None
        
        items = [
            MenuItem(
                "1",
                "Java Bilgileri",
                f"Mevcut: {java_version or 'Bulunamadı'}",
                callback=self._show_java_info,
                color="cyan"
            ),
            MenuItem(
                "2",
                "Java Sürümleri",
                "Sistemdeki tüm Java sürümleri",
                callback=self._show_available_java_versions,
                color="blue"
            ),
            MenuItem(
                "3",
                "Java Test",
                "Java uyumluluğunu test et",
                callback=self._test_java_compatibility,
                color="green"
            )
        ]
        
        self.navigator.show_menu("JAVA YÖNETİMİ", items, show_exit=True)
    
    def _show_java_info(self):
        """Show Java information"""
        os.system('clear')
        
        java_version = SystemUtils.check_java_version(self.java_executable) if self.java_executable else None
        
        table = Table(title="Java Bilgileri", show_header=True, header_style="bold cyan")
        table.add_column("Özellik", style="cyan", width=20)
        table.add_column("Değer", style="white", width=30)
        
        table.add_row("Java Yolu", self.java_executable or "Bulunamadı")
        table.add_row("Sürüm", java_version or "Bilinmiyor")
        table.add_row("Uyumlu", "✅ Evet" if SystemUtils.is_java_compatible() else "❌ Hayır")
        
        self.console.print(table)
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_available_java_versions(self):
        """Show available Java versions"""
        os.system('clear')
        
        # This would show all Java versions - simplified for now
        self.console.print("[yellow]Java sürümleri listelenecek[/yellow]")
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _test_java_compatibility(self):
        """Test Java compatibility"""
        os.system('clear')
        
        if SystemUtils.is_java_compatible():
            self.console.print("[green]✅ Java uyumlu![/green]")
        else:
            self.console.print("[red]❌ Java uyumsuz![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_system_test_menu(self):
        """Show system test menu"""
        os.system('clear')
        
        items = [
            MenuItem(
                "1",
                "Tam Sistem Testi",
                "Tüm bileşenleri test et",
                callback=self._run_full_system_test,
                color="green"
            ),
            MenuItem(
                "2",
                "Java Test",
                "Sadece Java'yı test et",
                callback=self._test_java_only,
                color="blue"
            ),
            MenuItem(
                "3",
                "İnternet Test",
                "Bağlantıyı test et",
                callback=self._test_internet,
                color="cyan"
            )
        ]
        
        self.navigator.show_menu("SİSTEM TESTİ", items, show_exit=True)
    
    def _run_full_system_test(self):
        """Run full system test"""
        os.system('clear')
        
        self.console.print("[green]🔍 Sistem testi başlatılıyor...[/green]")
        
        # Test Java
        java_ok = SystemUtils.is_java_compatible()
        self.console.print(f"Java: {'✅ OK' if java_ok else '❌ HATA'}")
        
        # Test Internet
        internet_ok = NetworkUtils.check_internet_connection()
        self.console.print(f"İnternet: {'✅ OK' if internet_ok else '❌ HATA'}")
        
        # Test Directories
        dirs_ok = all([
            self.minecraft_dir.exists(),
            self.launcher_dir.exists(),
            self.versions_dir.exists()
        ])
        self.console.print(f"Dizinler: {'✅ OK' if dirs_ok else '❌ HATA'}")
        
        if all([java_ok, internet_ok, dirs_ok]):
            self.console.print("[green]🎉 Tüm testler başarılı![/green]")
        else:
            self.console.print("[red]⚠️ Bazı testler başarısız![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _test_java_only(self):
        """Test Java only"""
        os.system('clear')
        
        if SystemUtils.is_java_compatible():
            self.console.print("[green]✅ Java testi başarılı![/green]")
        else:
            self.console.print("[red]❌ Java testi başarısız![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _test_internet(self):
        """Test internet connection"""
        os.system('clear')
        
        if NetworkUtils.check_internet_connection():
            self.console.print("[green]✅ İnternet bağlantısı OK![/green]")
        else:
            self.console.print("[red]❌ İnternet bağlantısı yok![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _change_username_callback(self):
        """Callback for changing username"""
        current = self.config.get('username', 'BerkePlayer')
        new_username = input(f"\n[cyan]Kullanıcı adı (mevcut: {current}): [/cyan]").strip()
        
        if new_username and ValidationUtils.validate_username(new_username):
            self.config['username'] = new_username
            self._save_config()
            self.console.print(f"[green]✅ Kullanıcı adı '{new_username}' olarak değiştirildi[/green]")
        elif new_username:
            self.console.print("[red]❌ Geçersiz kullanıcı adı! (3-16 karakter, sadece harf, rakam ve _)[/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _change_memory_callback(self):
        """Callback for changing memory settings"""
        current = self.config.get('memory', 'auto')
        self.console.print(f"\n[cyan]Mevcut bellek ayarı: {current}[/cyan]")
        self.console.print("[dim]Örnekler: auto, 2G, 4G, 8192M[/dim]")
        
        new_memory = input("\n[cyan]Yeni bellek ayarı: [/cyan]").strip()
        
        if new_memory and ValidationUtils.validate_memory(new_memory):
            self.config['memory'] = new_memory
            self._save_config()
            self.console.print(f"[green]✅ Bellek ayarı '{new_memory}' olarak değiştirildi[/green]")
        elif new_memory:
            self.console.print("[red]❌ Geçersiz bellek ayarı![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _change_window_size_callback(self):
        """Callback for changing window size"""
        current_width = self.config.get('window_width', 1280)
        current_height = self.config.get('window_height', 720)
        
        self.console.print(f"\n[cyan]Mevcut pencere boyutu: {current_width}x{current_height}[/cyan]")
        
        try:
            new_width = input("\n[cyan]Genişlik: [/cyan]").strip()
            new_height = input("[cyan]Yükseklik: [/cyan]").strip()
            
            if new_width and new_height:
                width = int(new_width)
                height = int(new_height)
                
                if 800 <= width <= 3840 and 600 <= height <= 2160:
                    self.config['window_width'] = width
                    self.config['window_height'] = height
                    self._save_config()
                    self.console.print(f"[green]✅ Pencere boyutu {width}x{height} olarak değiştirildi[/green]")
                else:
                    self.console.print("[red]❌ Geçersiz boyut! (800-3840 x 600-2160)[/red]")
        except ValueError:
            self.console.print("[red]❌ Geçersiz sayı![/red]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _change_java_settings_callback(self):
        """Callback for changing Java settings"""
        current_args = self.config.get('java_args', [])
        self.console.print(f"\n[cyan]Mevcut Java parametreleri: {' '.join(current_args) if current_args else 'Yok'}[/cyan]")
        
        new_args = input("\n[cyan]Yeni Java parametreleri (boşlukla ayırın): [/cyan]").strip()
        
        if new_args:
            args = new_args.split()
            self.config['java_args'] = args
            self._save_config()
            self.console.print(f"[green]✅ Java parametreleri güncellendi[/green]")
        else:
            self.config['java_args'] = []
            self._save_config()
            self.console.print(f"[green]✅ Java parametreleri temizlendi[/green]")
        
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_about(self):
        """Show about information"""
        os.system('clear')
        
        about_text = f"""
[bold cyan]BerkeMC v{__version__}[/bold cyan]

[bold white]Geliştirici:[/bold white] Berke
[bold white]Platform:[/bold white] Arch Linux
[bold white]Dil:[/bold white] Python 3

[bold yellow]Özellikler:[/bold yellow]
• Ok tuşları ile gezinme
• NameMC skin entegrasyonu
• Mod yönetimi
• Performans izleme
• Gelişmiş arayüz

[bold green]Teşekkürler:[/bold green]
• Rich kütüphanesi
• Minecraft/Mojang
• Arch Linux topluluğu
        """
        
        panel = Panel(
            about_text.strip(),
            title="[bold white]HAKKINDA[/bold white]",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def run(self):
        """Main launcher loop with keyboard navigation"""
        # First run setup
        self._first_run_setup()
        
        while True:
            # Clear screen
            if sys.stdout.isatty():
                os.system('clear' if os.name == 'posix' else 'cls')
            
            # Show banner
            self.console.print(self._create_banner())
            
            # Show status bar
            self.console.print(self._create_status_bar())
            self.console.print()
            
            # Create and show main menu
            items = self._create_main_menu_items()
            choice = self.navigator.show_menu("ANA MENÜ", items, show_exit=True)
            
            if choice is None:  # User pressed Esc or chose exit
                # Show goodbye message
                os.system('clear')
                goodbye_msg = f"""
[bold cyan]██████╗ [/bold cyan] 
[bold cyan]██╔══██╗[/bold cyan] [bold green]Teşekkürler![/bold green]
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
    
    def _first_run_setup(self):
        """First run setup"""
        if not self.config_file.exists():
            self.console.print(Panel(
                "[bold green]🎉 BerkeMC'ye hoş geldiniz![/bold green]\n\n"
                "[dim]İlk kurulum yapılıyor...[/dim]",
                border_style="green",
                padding=(1, 2)
            ))
            
            # Check Java
            if not self.java_executable:
                self.console.print(Panel(
                    "[bold red]⚠️ Java bulunamadı![/bold red]\n\n"
                    "[dim]Minecraft çalıştırmak için Java gerekli.[/dim]\n"
                    "[dim]Lütfen Java'yı yükleyin:[/dim]\n"
                    "[cyan]sudo pacman -S jdk-openjdk[/cyan]",
                    border_style="red",
                    padding=(1, 2)
                ))
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
            
            # Check internet connection
            if not NetworkUtils.check_internet_connection():
                self.console.print(Panel(
                    "[bold yellow]⚠️ İnternet bağlantısı yok![/bold yellow]\n\n"
                    "[dim]Sürüm indirmek için internet gerekli.[/dim]",
                    border_style="yellow",
                    padding=(1, 2)
                ))
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")

def main():
    """Main function"""
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
