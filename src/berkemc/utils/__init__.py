"""
Utility functions and helpers
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console

class SystemUtils:
    """System utility functions"""
    
    @staticmethod
    def find_java() -> Optional[str]:
        """Find Java executable - Minecraft compatible versions prioritized (17-21)"""
        # Check JAVA_HOME first
        if os.environ.get('JAVA_HOME'):
            java_home_bin = os.path.join(os.environ['JAVA_HOME'], 'bin', 'java')
            if os.path.exists(java_home_bin):
                return java_home_bin
        
        # Try Java paths (Minecraft compatible versions first)
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
            if java_path.startswith("/"):
                if os.path.exists(java_path):
                    return java_path
            elif shutil.which(java_path):
                return shutil.which(java_path)
                
        return None
    
    @staticmethod
    def check_java_version(java_executable: str) -> Optional[str]:
        """Check Java version"""
        try:
            result = subprocess.run([java_executable, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            version_output = result.stderr
            
            import re
            version_match = re.search(r'version "(\d+)\.(\d+)\.(\d+)', version_output)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3))
                return f"{major}.{minor}.{patch}"
            return None
        except Exception:
            return None
    
    @staticmethod
    def is_java_compatible(java_executable: str = None, min_version: int = 17) -> bool:
        """Check if Java is compatible with Minecraft"""
        if not java_executable:
            java_executable = SystemUtils.find_java()
        
        version = SystemUtils.check_java_version(java_executable)
        if not version:
            return False
        
        try:
            major_version = int(version.split('.')[0])
            return major_version >= min_version
        except:
            return False
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get system information"""
        try:
            import psutil
            return {
                "memory": f"{psutil.virtual_memory().total // (1024**3)} GB",
                "cpu_cores": psutil.cpu_count(),
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
    
    @staticmethod
    def is_terminal_compatible() -> bool:
        """Check if terminal supports advanced features"""
        return sys.stdout.isatty() and os.environ.get('TERM') not in ['dumb', 'unknown']

class FileUtils:
    """File utility functions"""
    
    @staticmethod
    def ensure_directory(path: Path) -> Path:
        """Ensure directory exists"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_size(filepath: Path) -> str:
        """Get human readable file size"""
        if not filepath.exists():
            return "0 B"
        
        size = filepath.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @staticmethod
    def safe_remove(filepath: Path) -> bool:
        """Safely remove file"""
        try:
            if filepath.exists():
                filepath.unlink()
                return True
        except Exception:
            pass
        return False

class NetworkUtils:
    """Network utility functions"""
    
    @staticmethod
    def check_internet_connection() -> bool:
        """Check internet connection"""
        try:
            import requests
            response = requests.get("https://www.google.com", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    @staticmethod
    def download_file(url: str, filepath: Path, console: Console = None) -> bool:
        """Download file with progress"""
        try:
            import requests
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            if console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
                ) as progress:
                    
                    task = progress.add_task("İndiriliyor...", total=100)
                    
                    with open(filepath, 'wb') as f:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress.update(task, completed=int(downloaded / total_size * 100))
                    
                    progress.update(task, completed=100)
            else:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            return True
            
        except Exception as e:
            if console:
                console.print(f"[red]İndirme hatası: {e}[/red]")
            return False

class ValidationUtils:
    """Validation utility functions"""
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate Minecraft username"""
        if not username or len(username) < 3 or len(username) > 16:
            return False
        
        # Check for valid characters
        import re
        return bool(re.match(r'^[a-zA-Z0-9_]+$', username))
    
    @staticmethod
    def validate_memory(memory: str) -> bool:
        """Validate memory setting"""
        if memory == "auto":
            return True
        
        try:
            # Extract number and unit
            import re
            match = re.match(r'(\d+)([GM]?)', memory.upper())
            if match:
                value = int(match.group(1))
                unit = match.group(2) or 'G'
                
                if unit == 'G' and 1 <= value <= 32:
                    return True
                elif unit == 'M' and 512 <= value <= 32768:
                    return True
        except:
            pass
        
        return False
    
    @staticmethod
    def validate_version_id(version_id: str) -> bool:
        """Validate Minecraft version ID"""
        if not version_id:
            return False
        
        # Basic version format check
        import re
        return bool(re.match(r'^[a-zA-Z0-9._-]+$', version_id))

__all__ = [
    'SystemUtils',
    'FileUtils', 
    'NetworkUtils',
    'ValidationUtils'
]
