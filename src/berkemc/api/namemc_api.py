"""
NameMC API integration
"""

import requests
import time
from typing import Dict, List, Optional
from rich.console import Console

class NameMCAPI:
    """NameMC API integration for skin management"""
    
    def __init__(self, console: Console):
        self.console = console
        self.base_url = "https://api.namemc.com"
        self.crafatar_url = "https://crafatar.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BerkeMinecraftLauncher/4.0.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def search_player(self, username: str) -> Optional[Dict]:
        """Search for player on NameMC"""
        try:
            # First get UUID from Mojang
            response = self.session.get(
                f"https://api.mojang.com/users/profiles/minecraft/{username}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                uuid = data.get('id')
                
                if uuid:
                    # Format UUID for skin URL
                    formatted_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
                    
                    return {
                        'username': username,
                        'uuid': formatted_uuid,
                        'skin_url': f"{self.crafatar_url}/skins/{formatted_uuid}",
                        'avatar_url': f"{self.crafatar_url}/avatars/{formatted_uuid}",
                        'source': 'namemc'
                    }
            
            return None
            
        except requests.RequestException as e:
            self.console.print(f"[red]Oyuncu arama hatası: {e}[/red]")
            return None
    
    def get_popular_players(self) -> List[str]:
        """Get list of popular Minecraft players"""
        return [
            "Dream", "Technoblade", "TommyInnit", "WilburSoot", "Philza",
            "GeorgeNotFound", "Sapnap", "BadBoyHalo", "Skeppy", "a6d",
            "CaptainSparklez", "PewDiePie", "StampyLongHead", "DanTDM",
            "PopularMMOs", "SSundee", "PrestonPlayz", "UnspeakableGaming",
            "MrBeast", "PewDiePie", "Markiplier", "Jacksepticeye"
        ]
    
    def get_player_skins(self, usernames: List[str]) -> List[Dict]:
        """Get skins for multiple players"""
        skins = []
        
        for username in usernames:
            skin_data = self.search_player(username)
            if skin_data:
                skins.append(skin_data)
            time.sleep(0.1)  # Rate limiting
        
        return skins
    
    def download_skin(self, skin_data: Dict, filepath: str) -> bool:
        """Download skin from URL"""
        try:
            response = self.session.get(skin_data['skin_url'], stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return True
            
        except requests.RequestException as e:
            self.console.print(f"[red]Skin indirme hatası: {e}[/red]")
            return False

__all__ = ['NameMCAPI']
