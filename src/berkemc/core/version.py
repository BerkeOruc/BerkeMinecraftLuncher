"""
Version management system
"""

import json
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

class VersionManager:
    """Minecraft version management system"""
    
    def __init__(self, console: Console, versions_dir: Path, cache_dir: Path):
        self.console = console
        self.versions_dir = versions_dir
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        
        # Minecraft API URLs
        self.version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        self.assets_url = "https://resources.download.minecraft.net"
        
        # Cache settings
        self.cache_duration = 3600  # 1 hour
        self.manifest_cache_file = self.cache_dir / "versions_manifest.json"
    
    def get_available_versions(self) -> List[Dict]:
        """Get available Minecraft versions with caching"""
        # Check cache
        if self.manifest_cache_file.exists():
            cache_age = time.time() - self.manifest_cache_file.stat().st_mtime
            if cache_age < self.cache_duration:
                try:
                    with open(self.manifest_cache_file, 'r') as f:
                        data = json.load(f)
                        return data.get("versions", [])
                except:
                    pass
        
        # Fetch from API
        try:
            response = requests.get(self.version_manifest_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Save to cache
            with open(self.manifest_cache_file, 'w') as f:
                json.dump(data, f)
            
            return data.get("versions", [])
            
        except requests.RequestException as e:
            self.console.print(f"[red]Sürüm listesi alınamadı: {e}[/red]")
            
            # Try to use cached version
            if self.manifest_cache_file.exists():
                try:
                    with open(self.manifest_cache_file, 'r') as f:
                        data = json.load(f)
                        return data.get("versions", [])
                except:
                    pass
            
            return []
    
    def get_installed_versions(self) -> List[str]:
        """Get list of installed versions"""
        versions = []
        for version_dir in self.versions_dir.iterdir():
            if version_dir.is_dir():
                jar_file = version_dir / f"{version_dir.name}.jar"
                if jar_file.exists():
                    versions.append(version_dir.name)
        return sorted(versions, reverse=True)
    
    def get_version_info(self, version_id: str) -> Optional[Dict]:
        """Get detailed information about a version"""
        try:
            # First check if we have it locally
            version_dir = self.versions_dir / version_id
            version_json_path = version_dir / f"{version_id}.json"
            
            if version_json_path.exists():
                with open(version_json_path, 'r') as f:
                    return json.load(f)
            
            # If not local, get from API
            versions = self.get_available_versions()
            for version in versions:
                if version['id'] == version_id:
                    return version
            
            return None
            
        except Exception as e:
            self.console.print(f"[red]Sürüm bilgisi alınamadı: {e}[/red]")
            return None
    
    def download_version(self, version_id: str) -> bool:
        """Download a Minecraft version"""
        try:
            # Get version info
            version_info = self.get_version_info(version_id)
            if not version_info:
                self.console.print(f"[red]❌ {version_id} sürümü bulunamadı![/red]")
                return False
            
            # Create version directory
            version_dir = self.versions_dir / version_id
            version_dir.mkdir(exist_ok=True)
            
            # Download version JSON
            version_json_url = version_info.get('url')
            if not version_json_url:
                self.console.print(f"[red]❌ {version_id} için URL bulunamadı![/red]")
                return False
            
            # Download version JSON
            response = requests.get(version_json_url, timeout=30)
            response.raise_for_status()
            version_data = response.json()
            
            # Save version JSON
            version_json_path = version_dir / f"{version_id}.json"
            with open(version_json_path, 'w') as f:
                json.dump(version_data, f)
            
            # Download JAR file
            jar_url = version_data.get('downloads', {}).get('client', {}).get('url')
            if not jar_url:
                self.console.print(f"[red]❌ {version_id} için JAR URL bulunamadı![/red]")
                return False
            
            jar_path = version_dir / f"{version_id}.jar"
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
            ) as progress:
                
                task = progress.add_task(f"{version_id} indiriliyor...", total=100)
                
                response = requests.get(jar_url, stream=True, timeout=60)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress.update(task, completed=int(downloaded / total_size * 100))
                
                progress.update(task, completed=100)
            
            self.console.print(f"[green]✅ {version_id} başarıyla indirildi![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ {version_id} indirme hatası: {e}[/red]")
            return False
    
    def delete_version(self, version_id: str) -> bool:
        """Delete an installed version"""
        try:
            version_dir = self.versions_dir / version_id
            if version_dir.exists():
                import shutil
                shutil.rmtree(version_dir)
                self.console.print(f"[green]✅ {version_id} sürümü silindi[/green]")
                return True
            else:
                self.console.print(f"[red]❌ {version_id} sürümü bulunamadı![/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]❌ Silme hatası: {e}[/red]")
            return False
    
    def get_popular_versions(self) -> List[str]:
        """Get list of popular Minecraft versions"""
        return [
            "1.20.4", "1.20.1", "1.19.4", "1.19.2", "1.18.2",
            "1.17.1", "1.16.5", "1.15.2", "1.14.4", "1.13.2",
            "1.12.2", "1.11.2", "1.10.2", "1.9.4", "1.8.9"
        ]
    
    def search_versions(self, query: str) -> List[Dict]:
        """Search for versions matching query"""
        versions = self.get_available_versions()
        matching_versions = []
        
        query_lower = query.lower()
        for version in versions:
            if (query_lower in version['id'].lower() or 
                query_lower in version.get('type', '').lower()):
                matching_versions.append(version)
        
        return matching_versions[:20]  # Limit to 20 results

__all__ = ['VersionManager']
