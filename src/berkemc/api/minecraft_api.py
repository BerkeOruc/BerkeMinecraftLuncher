"""
Minecraft API integration
"""

import requests
import json
import time
from typing import Dict, List, Optional
from rich.console import Console

class MinecraftAPI:
    """Minecraft API integration"""
    
    def __init__(self, console: Console):
        self.console = console
        self.base_url = "https://launchermeta.mojang.com/mc/game"
        self.assets_url = "https://resources.download.minecraft.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BerkeMinecraftLauncher/4.0.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def get_version_manifest(self) -> Optional[Dict]:
        """Get Minecraft version manifest"""
        try:
            response = self.session.get(f"{self.base_url}/version_manifest.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.console.print(f"[red]Version manifest alınamadı: {e}[/red]")
            return None
    
    def get_version_info(self, version_id: str) -> Optional[Dict]:
        """Get specific version information"""
        try:
            manifest = self.get_version_manifest()
            if not manifest:
                return None
            
            for version in manifest.get('versions', []):
                if version['id'] == version_id:
                    # Get detailed version info
                    response = self.session.get(version['url'], timeout=10)
                    response.raise_for_status()
                    return response.json()
            
            return None
        except requests.RequestException as e:
            self.console.print(f"[red]Version bilgisi alınamadı: {e}[/red]")
            return None
    
    def get_player_profile(self, username: str) -> Optional[Dict]:
        """Get player profile from Mojang API"""
        try:
            response = self.session.get(
                f"https://api.mojang.com/users/profiles/minecraft/{username}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            self.console.print(f"[red]Oyuncu profili alınamadı: {e}[/red]")
            return None
    
    def get_player_skin(self, uuid: str) -> Optional[str]:
        """Get player skin URL"""
        try:
            # Format UUID for skin URL
            formatted_uuid = uuid.replace('-', '')
            return f"https://crafatar.com/skins/{formatted_uuid}"
        except:
            return None

__all__ = ['MinecraftAPI']
