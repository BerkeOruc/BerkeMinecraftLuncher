"""
Java management system
"""

import os
import subprocess
import shutil
from typing import List, Optional, Dict
from rich.console import Console

class JavaManager:
    """Java management and detection system"""
    
    def __init__(self, console: Console):
        self.console = console
        self.java_executable = self._find_java()
    
    def _find_java(self) -> Optional[str]:
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
    
    def check_java_version(self) -> Optional[str]:
        """Check Java version"""
        if not self.java_executable:
            return None
            
        try:
            result = subprocess.run([self.java_executable, "-version"], 
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
        except Exception as e:
            self.console.print(f"[red]Java sürüm kontrolü başarısız: {e}[/red]")
            return None
    
    def get_available_java_versions(self) -> List[Dict]:
        """Get all available Java versions on system"""
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
                        java_path = os.path.join(java_dir, item, "bin", "java")
                        if os.path.exists(java_path):
                            version = self._get_java_version_from_path(java_path)
                            if version:
                                java_versions.append({
                                    'path': java_path,
                                    'version': version,
                                    'name': item
                                })
                except PermissionError:
                    continue
        
        return sorted(java_versions, key=lambda x: x['version'], reverse=True)
    
    def _get_java_version_from_path(self, java_path: str) -> Optional[str]:
        """Get Java version from specific path"""
        try:
            result = subprocess.run([java_path, "-version"], 
                                  capture_output=True, text=True, timeout=5)
            version_output = result.stderr
            
            import re
            version_match = re.search(r'version "(\d+)\.(\d+)\.(\d+)', version_output)
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3))
                return f"{major}.{minor}.{patch}"
        except:
            pass
        return None
    
    def is_java_compatible(self, min_version: int = 17) -> bool:
        """Check if Java is compatible with Minecraft"""
        version = self.check_java_version()
        if not version:
            return False
        
        try:
            major_version = int(version.split('.')[0])
            return major_version >= min_version
        except:
            return False
    
    def get_java_info(self) -> Dict:
        """Get comprehensive Java information"""
        info = {
            'executable': self.java_executable,
            'version': self.check_java_version(),
            'compatible': self.is_java_compatible(),
            'available_versions': self.get_available_java_versions()
        }
        return info

__all__ = ['JavaManager']
