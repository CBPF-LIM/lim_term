"""
Configuration Manager for saving/loading user preferences
"""
import os
import yaml
from typing import Optional


class ConfigManager:
    """Manages user configuration persistence"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        self.config_file = os.path.join(self.config_dir, "user_config.yml")
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        if not os.path.exists(self.config_dir):
            try:
                os.makedirs(self.config_dir)
            except Exception as e:
                print(f"Error creating config directory: {e}")
    
    def _load_config(self) -> dict:
        """Load the configuration file"""
        if not os.path.exists(self.config_file):
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}
    
    def _save_config(self, config: dict):
        """Save the configuration file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                yaml.safe_dump(config, file, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def load_language(self) -> Optional[str]:
        """Load the saved language preference"""
        config = self._load_config()
        return config.get('language')
    
    def save_language(self, language_code: str):
        """Save the language preference"""
        config = self._load_config()
        config['language'] = language_code
        self._save_config(config)
    
    def load_setting(self, key: str, default=None):
        """Load a specific setting"""
        config = self._load_config()
        return config.get(key, default)
    
    def save_setting(self, key: str, value):
        """Save a specific setting"""
        config = self._load_config()
        config[key] = value
        self._save_config(config)
