"""
Mod management system
"""

import os
import requests
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import time

class ModManager:
    """Enhanced mod management system"""
    
    def __init__(self, console: Console, minecraft_dir: Path):
        self.console = console
        self.minecraft_dir = minecraft_dir
        self.mods_dir = minecraft_dir / "mods"
        self.mods_dir.mkdir(exist_ok=True)
        
        # Mod sources
        self.modrinth_api = "https://api.modrinth.com/v2"
        self.curseforge_api = "https://api.curseforge.com/v1"
        
        # Popular mods cache
        self.popular_mods_cache = []
        self.cache_time = 0
        self.cache_duration = 3600  # 1 hour
        
    def get_popular_mods(self) -> List[Dict]:
        """Get popular mods from Modrinth"""
        current_time = time.time()
        
        # Use cache if available and not expired
        if self.popular_mods_cache and (current_time - self.cache_time) < self.cache_duration:
            return self.popular_mods_cache
            
        try:
            # Popular mods list (you can expand this)
            popular_mod_ids = [
                "fabric-api", "optifabric", "sodium", "lithium", "phosphor",
                "iris", "sodium-extra", "lambdabettergrass", "cull-leaves",
                "dynamic-fps", "ferrite-core", "krypton", "lazydfu"
            ]
            
            mods = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}")
            ) as progress:
                
                task = progress.add_task("Popüler modlar yükleniyor...", total=len(popular_mod_ids))
                
                for mod_id in popular_mod_ids:
                    try:
                        response = requests.get(f"{self.modrinth_api}/project/{mod_id}", timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            mods.append({
                                'id': mod_id,
                                'name': data.get('title', mod_id),
                                'description': data.get('description', ''),
                                'downloads': data.get('downloads', 0),
                                'source': 'modrinth'
                            })
                    except:
                        pass
                    progress.advance(task)
            
            self.popular_mods_cache = mods
            self.cache_time = current_time
            
            return mods
            
        except Exception as e:
            self.console.print(f"[red]Popüler modlar yüklenemedi: {e}[/red]")
            return []
    
    def get_installed_mods(self) -> List[Dict]:
        """Get installed mods"""
        mods = []
        for mod_file in self.mods_dir.glob("*.jar"):
            mods.append({
                'filename': mod_file.name,
                'filepath': mod_file,
                'size': mod_file.stat().st_size,
                'modified': mod_file.stat().st_mtime
            })
        return sorted(mods, key=lambda x: x['modified'], reverse=True)
    
    def search_mods(self, query: str) -> List[Dict]:
        """Search for mods"""
        try:
            response = requests.get(
                f"{self.modrinth_api}/search",
                params={'query': query, 'limit': 20},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                mods = []
                for hit in data.get('hits', []):
                    mods.append({
                        'id': hit.get('project_id'),
                        'name': hit.get('title', ''),
                        'description': hit.get('description', ''),
                        'downloads': hit.get('downloads', 0),
                        'source': 'modrinth'
                    })
                return mods
        except Exception as e:
            self.console.print(f"[red]Mod arama hatası: {e}[/red]")
            
        return []
    
    def download_mod(self, mod_data: Dict) -> bool:
        """Download mod from Modrinth"""
        try:
            # Get latest version
            response = requests.get(
                f"{self.modrinth_api}/project/{mod_data['id']}/version",
                timeout=10
            )
            
            if response.status_code == 200:
                versions = response.json()
                if versions:
                    latest_version = versions[0]
                    files = latest_version.get('files', [])
                    if files:
                        file_url = files[0]['url']
                        filename = files[0]['filename']
                        
                        # Download file
                        file_response = requests.get(file_url, stream=True, timeout=30)
                        file_response.raise_for_status()
                        
                        filepath = self.mods_dir / filename
                        
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            BarColumn(),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
                        ) as progress:
                            
                            task = progress.add_task(f"Mod indiriliyor: {filename}", total=100)
                            
                            total_size = int(file_response.headers.get('content-length', 0))
                            downloaded = 0
                            
                            with open(filepath, 'wb') as f:
                                for chunk in file_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        if total_size > 0:
                                            progress.update(task, completed=int(downloaded / total_size * 100))
                            
                            progress.update(task, completed=100)
                        
                        self.console.print(f"[green]✅ Mod indirildi: {filename}[/green]")
                        return True
                        
        except Exception as e:
            self.console.print(f"[red]❌ Mod indirme hatası: {e}[/red]")
            
        return False
    
    def remove_mod(self, mod_file: Path) -> bool:
        """Remove mod file"""
        try:
            mod_file.unlink()
            self.console.print(f"[green]✅ Mod silindi: {mod_file.name}[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]❌ Mod silme hatası: {e}[/red]")
            return False
    
    def create_mod_menu_items(self, navigator) -> List:
        """Create mod menu items for keyboard navigation"""
        from ..ui import MenuItem
        
        items = []
        
        # Search mods
        items.append(MenuItem(
            "1",
            "Mod Ara",
            "Modrinth'ten mod ara ve indir",
            callback=self._search_mods_callback,
            color="cyan"
        ))
        
        # Popular mods
        items.append(MenuItem(
            "2",
            "Popüler Modlar",
            "Popüler modları gör ve indir",
            callback=self._popular_mods_callback,
            color="green"
        ))
        
        # Installed mods
        items.append(MenuItem(
            "3",
            "Yüklü Modlar",
            "Yüklü modları yönet",
            callback=self._installed_mods_callback,
            color="blue"
        ))
        
        return items
    
    def _search_mods_callback(self):
        """Callback for mod search"""
        query = input("\n[cyan]Mod ara: [/cyan]").strip()
        if query:
            mods = self.search_mods(query)
            if mods:
                self._show_mods_list(mods, f"'{query}' Arama Sonuçları")
            else:
                self.console.print(f"[red]❌ '{query}' için mod bulunamadı![/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _popular_mods_callback(self):
        """Callback for popular mods"""
        mods = self.get_popular_mods()
        if mods:
            self._show_mods_list(mods, "Popüler Modlar")
        else:
            self.console.print("[red]❌ Popüler modlar yüklenemedi![/red]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _installed_mods_callback(self):
        """Callback for installed mods"""
        mods = self.get_installed_mods()
        if mods:
            self._show_installed_mods_list(mods, "Yüklü Modlar")
        else:
            self.console.print("[yellow]⚠️ Henüz mod yüklenmemiş![/yellow]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_mods_list(self, mods: List[Dict], title: str):
        """Show mods list with keyboard navigation"""
        from ..ui import KeyboardNavigator, MenuItem
        
        navigator = KeyboardNavigator(self.console)
        
        # Create menu items for each mod
        items = []
        for i, mod in enumerate(mods[:20]):  # Limit to 20 mods
            downloads_str = f"{mod['downloads']:,}" if mod['downloads'] > 0 else "Bilinmiyor"
            description = f"{downloads_str} indirme"
            
            items.append(MenuItem(
                str(i + 1),
                mod['name'],
                description,
                callback=lambda m=mod: self._download_mod_callback(m),
                color="white"
            ))
        
        # Show menu
        navigator.show_menu(title, items, show_exit=True)
    
    def _show_installed_mods_list(self, mods: List[Dict], title: str):
        """Show installed mods list with keyboard navigation"""
        from ..ui import KeyboardNavigator, MenuItem
        
        navigator = KeyboardNavigator(self.console)
        
        # Create menu items for each mod
        items = []
        for i, mod in enumerate(mods[:20]):  # Limit to 20 mods
            size_mb = mod['size'] / (1024 * 1024)
            description = f"{size_mb:.1f} MB"
            
            items.append(MenuItem(
                str(i + 1),
                mod['filename'],
                description,
                callback=lambda m=mod: self._remove_mod_callback(m),
                color="red"
            ))
        
        # Show menu
        navigator.show_menu(title, items, show_exit=True)
    
    def _download_mod_callback(self, mod_data: Dict):
        """Callback for downloading mod"""
        if self.download_mod(mod_data):
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _remove_mod_callback(self, mod_data: Dict):
        """Callback for removing mod"""
        if self.remove_mod(mod_data['filepath']):
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None

__all__ = ['ModManager']
