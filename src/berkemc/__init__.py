"""
BerkeMC - Advanced Minecraft Launcher
Arch Linux için optimize edilmiş terminal tabanlı Minecraft launcher'ı
"""

__version__ = "4.0.0"
__author__ = "Berke"
__email__ = "berke@example.com"

from .core.launcher import MinecraftLauncher
from .core.config import ConfigManager
from .core.version import VersionManager

__all__ = [
    'MinecraftLauncher',
    'ConfigManager', 
    'VersionManager',
    '__version__',
    '__author__',
    '__email__'
]
