"""Configuration management"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from PyQt6.QtCore import QSettings

class Config:
    def __init__(self):
        self.settings = QSettings('RcloneTray', 'RcloneTray')
        self.load_defaults()

    def load_defaults(self):
        """Load default settings if not exist"""
        defaults = {
            # Mount Settings
            'mount_base_dir': str(Path.home() / 'mnt'),
            'mount_options': '--vfs-cache-mode=full',
            'auto_mount': False,
            'mount_on_startup': False,
            
            # Interface Settings
            'start_minimized': True,
            'show_notifications': True,
            'dark_mode': True,
            'minimize_to_tray': True,
            
            # Advanced Settings
            'rclone_path': 'rclone',
            'config_path': str(Path.home() / '.config' / 'rclone' / 'rclone.conf'),
            'log_level': 'INFO',
            'check_updates': True,
            'buffer_size': '256M',
            'transfers': 4,
            
            # Remote Settings
            'remotes': {},  # Store per-remote settings
            'last_used_remote': '',
            
            # Network Settings
            'bandwidth_limit': '0',  # 0 means unlimited
            'timeout': 30,
            'retries': 3,
            'low_level_retries': 10,
        }
        
        # Only set defaults if they don't exist
        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value with proper type conversion"""
        value = self.settings.value(key, default)
        
        # Handle type conversion based on default value type
        if default is not None:
            if isinstance(default, bool):
                return value.lower() == 'true' if isinstance(value, str) else bool(value)
            elif isinstance(default, int):
                return int(value)
            elif isinstance(default, float):
                return float(value)
        
        return value

    def set(self, key: str, value: Any):
        """Set a setting value"""
        self.settings.setValue(key, value)
        self.settings.sync()

    def get_remote_settings(self, remote: str) -> Dict[str, Any]:
        """Get settings for a specific remote"""
        remotes = self.settings.value('remotes', {})
        return remotes.get(remote, {})

    def set_remote_settings(self, remote: str, settings: Dict[str, Any]):
        """Set settings for a specific remote"""
        remotes = self.settings.value('remotes', {})
        remotes[remote] = settings
        self.settings.setValue('remotes', remotes)
        self.settings.sync()

    def get_mount_options(self, remote: Optional[str] = None) -> str:
        """Get mount options, optionally for a specific remote"""
        base_options = self.get('mount_options', '--vfs-cache-mode=full')
        if remote:
            remote_settings = self.get_remote_settings(remote)
            remote_options = remote_settings.get('mount_options', '')
            if remote_options:
                return f"{base_options} {remote_options}"
        return base_options

    def export_settings(self, path: Path):
        """Export settings to a file"""
        settings = {}
        for key in self.settings.allKeys():
            settings[key] = self.settings.value(key)
        
        with open(path, 'w') as f:
            json.dump(settings, f, indent=2)

    def import_settings(self, path: Path):
        """Import settings from a file"""
        with open(path) as f:
            settings = json.load(f)
        
        for key, value in settings.items():
            self.settings.setValue(key, value)
        self.settings.sync()
