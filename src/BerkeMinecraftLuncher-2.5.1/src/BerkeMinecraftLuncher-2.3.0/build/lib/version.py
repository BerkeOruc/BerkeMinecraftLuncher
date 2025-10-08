#!/usr/bin/env python3
"""
Berke Minecraft Launcher - Version Information
"""

__version__ = "2.3.0"
__author__ = "Berke Oruç"
__email__ = "berke3oruc@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Berke Oruç"
__url__ = "https://github.com/berke0/BerkeMinecraftLuncher"

# Version info
VERSION_MAJOR = 2
VERSION_MINOR = 3
VERSION_PATCH = 0
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Build info
BUILD_DATE = "2025-10-04"
BUILD_NUMBER = "20251004"

# Feature flags
FEATURES = {
    "mod_system": True,
    "skin_system": True,
    "performance_monitor": True,
    "auto_update": False,  # Yakında!
    "forge_support": False,  # Yakında!
    "fabric_support": False,  # Yakında!
}

def get_version_string() -> str:
    """Tam sürüm string'i döndür"""
    return f"v{__version__}"

def get_full_version_string() -> str:
    """Detaylı sürüm bilgisi döndür"""
    return f"Berke Minecraft Launcher v{__version__} (Build {BUILD_NUMBER})"

def get_version_info() -> dict:
    """Tüm sürüm bilgilerini dict olarak döndür"""
    return {
        "version": __version__,
        "version_info": VERSION_INFO,
        "author": __author__,
        "license": __license__,
        "url": __url__,
        "build_date": BUILD_DATE,
        "build_number": BUILD_NUMBER,
        "features": FEATURES
    }

if __name__ == "__main__":
    print(get_full_version_string())
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print(f"URL: {__url__}")
