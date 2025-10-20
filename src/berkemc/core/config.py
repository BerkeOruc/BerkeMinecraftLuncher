"""
Configuration management
"""

import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "username": "BerkePlayer",
            "memory": "auto",
            "java_args": [],
            "current_skin": "default",
            "window_width": 1280,
            "window_height": 720,
            "fullscreen": False,
            "optimize_graphics": True,
            "enable_mods": False,
            "mod_loader": "none",
            "language": "tr"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Add missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except json.JSONDecodeError:
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()

__all__ = ['ConfigManager']
