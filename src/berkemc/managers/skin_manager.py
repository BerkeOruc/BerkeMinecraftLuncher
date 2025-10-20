"""
Skin management with NameMC integration
"""

import os
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
import threading
import time

class SkinManager:
    """Enhanced skin management with NameMC integration"""
    
    def __init__(self, console: Console, skins_dir: Path):
        self.console = console
        self.skins_dir = skins_dir
        self.skins_dir.mkdir(exist_ok=True)
        
        # NameMC API endpoints
        self.namemc_api = "https://api.namemc.com"
        self.mojang_api = "https://api.mojang.com/users/profiles/minecraft"
        self.skin_api = "https://crafatar.com/skins"
        
        # Popular skins cache
        self.popular_skins_cache = []
        self.cache_time = 0
        self.cache_duration = 3600  # 1 hour
        
    def search_player_skin(self, username: str) -> Optional[Dict]:
        """Search for player skin on NameMC"""
        try:
            # First get UUID from Mojang
            response = requests.get(f"{self.mojang_api}/{username}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                uuid = data.get('id')
                
                if uuid:
                    # Format UUID for skin URL
                    formatted_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
                    skin_url = f"{self.skin_api}/{formatted_uuid}"
                    
                    return {
                        'username': username,
                        'uuid': formatted_uuid,
                        'skin_url': skin_url,
                        'source': 'namemc'
                    }
        except Exception as e:
            self.console.print(f"[red]Skin arama hatası: {e}[/red]")
            
        return None
    
    def download_skin(self, skin_data: Dict, filename: str = None) -> bool:
        """Download skin from URL"""
        try:
            if not filename:
                filename = f"{skin_data['username']}.png"
                
            filepath = self.skins_dir / filename
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            ) as progress:
                
                task = progress.add_task("Skin indiriliyor...", total=100)
                
                response = requests.get(skin_data['skin_url'], stream=True, timeout=30)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress.update(task, completed=int(downloaded / total_size * 100))
                
                progress.update(task, completed=100)
                
            self.console.print(f"[green]✅ Skin indirildi: {filename}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Skin indirme hatası: {e}[/red]")
            return False
    
    def get_popular_skins(self) -> List[Dict]:
        """Get popular skins from NameMC"""
        current_time = time.time()
        
        # Use cache if available and not expired
        if self.popular_skins_cache and (current_time - self.cache_time) < self.cache_duration:
            return self.popular_skins_cache
            
        try:
            # Popular Minecraft players (you can expand this list)
            popular_players = [
                "Dream", "Technoblade", "TommyInnit", "WilburSoot", "Philza",
                "GeorgeNotFound", "Sapnap", "BadBoyHalo", "Skeppy", "a6d",
                "CaptainSparklez", "PewDiePie", "StampyLongHead", "DanTDM",
                "PopularMMOs", "SSundee", "PrestonPlayz", "UnspeakableGaming"
            ]
            
            skins = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}")
            ) as progress:
                
                task = progress.add_task("Popüler skinler yükleniyor...", total=len(popular_players))
                
                for player in popular_players:
                    skin_data = self.search_player_skin(player)
                    if skin_data:
                        skins.append(skin_data)
                    progress.advance(task)
            
            self.popular_skins_cache = skins
            self.cache_time = current_time
            
            return skins
            
        except Exception as e:
            self.console.print(f"[red]Popüler skinler yüklenemedi: {e}[/red]")
            return []
    
    def get_local_skins(self) -> List[Dict]:
        """Get locally available skins"""
        skins = []
        for skin_file in self.skins_dir.glob("*.png"):
            skins.append({
                'filename': skin_file.name,
                'filepath': skin_file,
                'size': skin_file.stat().st_size,
                'source': 'local'
            })
        return skins
    
    def create_skin_menu_items(self, navigator) -> List:
        """Create skin menu items for keyboard navigation"""
        from ..ui import MenuItem
        
        items = []
        
        # Search player skin
        items.append(MenuItem(
            "1", 
            "Oyuncu Skin'i Ara", 
            "NameMC'den oyuncu skin'i ara ve indir",
            callback=self._search_player_callback,
            color="cyan"
        ))
        
        # Popular skins
        items.append(MenuItem(
            "2",
            "Popüler Skinler",
            "Popüler oyuncuların skinlerini gör",
            callback=self._popular_skins_callback,
            color="green"
        ))
        
        # Local skins
        items.append(MenuItem(
            "3",
            "Yerel Skinler",
            "İndirilen skinleri yönet",
            callback=self._local_skins_callback,
            color="blue"
        ))
        
        return items
    
    def _search_player_callback(self):
        """Callback for player search"""
        username = input("\n[cyan]Oyuncu adı: [/cyan]").strip()
        if username:
            skin_data = self.search_player_skin(username)
            if skin_data:
                if self.download_skin(skin_data):
                    input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
            else:
                self.console.print(f"[red]❌ '{username}' oyuncusu bulunamadı![/red]")
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _popular_skins_callback(self):
        """Callback for popular skins"""
        skins = self.get_popular_skins()
        if skins:
            self._show_skins_list(skins, "Popüler Skinler")
        else:
            self.console.print("[red]❌ Popüler skinler yüklenemedi![/red]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _local_skins_callback(self):
        """Callback for local skins"""
        skins = self.get_local_skins()
        if skins:
            self._show_skins_list(skins, "Yerel Skinler")
        else:
            self.console.print("[yellow]⚠️ Henüz skin indirilmemiş![/yellow]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None
    
    def _show_skins_list(self, skins: List[Dict], title: str):
        """Show skins list with keyboard navigation"""
        from ..ui import KeyboardNavigator, MenuItem
        
        navigator = KeyboardNavigator(self.console)
        
        # Create menu items for each skin
        items = []
        for i, skin in enumerate(skins[:20]):  # Limit to 20 skins
            if skin.get('source') == 'namemc':
                label = f"{skin['username']} (NameMC)"
                description = f"UUID: {skin['uuid'][:8]}..."
            else:
                label = skin['filename']
                size_mb = skin['size'] / (1024 * 1024)
                description = f"{size_mb:.1f} MB"
            
            items.append(MenuItem(
                str(i + 1),
                label,
                description,
                callback=lambda s=skin: self._download_skin_callback(s),
                color="white"
            ))
        
        # Show menu
        navigator.show_menu(title, items, show_exit=True)
    
    def _download_skin_callback(self, skin_data: Dict):
        """Callback for downloading skin"""
        if skin_data.get('source') == 'namemc':
            filename = f"{skin_data['username']}_namemc.png"
            if self.download_skin(skin_data, filename):
                input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        else:
            self.console.print(f"[green]✅ Skin zaten mevcut: {skin_data['filename']}[/green]")
            input("\n[dim]Devam etmek için Enter'a basın...[/dim]")
        return None

__all__ = ['SkinManager']
