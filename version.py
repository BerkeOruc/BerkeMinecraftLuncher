#!/usr/bin/env python3
"""
Berke Minecraft Launcher - Version Information
"""

__version__ = "3.2.1"
__author__ = "Berke Oruç"
__email__ = "berke3oruc@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 Berke Oruç"
__url__ = "https://github.com/BerkeOruc/berkemc"

# Version info
VERSION_MAJOR = 3
VERSION_MINOR = 2
VERSION_PATCH = 1
VERSION_INFO = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

# Build info
BUILD_DATE = "2025-10-10"
BUILD_NUMBER = "20251010"

# Feature flags
FEATURES = {
    "mod_system": True,
    "skin_system": True,
    "performance_monitor": True,
    "java_management": True,
    "advanced_download": True,
    "window_fixes": True,
    "java_compatibility": True,  # Yeni!
    "mod_loader_support": True,  # Yeni!
    "skin_preview": True,  # Yeni!
    "first_run_setup": True,  # Yeni!
    "auto_update": True,  # Yeni!
    "desktop_integration": True,  # Yeni!
    "forge_support": True,  # Yeni!
    "fabric_support": True,  # Yeni!
    "optifine_support": True,  # Yeni!
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
