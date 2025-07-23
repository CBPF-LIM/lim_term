"""
Configuration Manager for saving/loading user preferences
"""
import os
import yaml
from typing import Optional, Any, Dict


class ConfigManager:
    """Manages user configuration persistence"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        self.config_file = os.path.join(self.config_dir, "prefs.yml")
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
    
    def _get_nested_value(self, data: dict, path: str, default=None):
        """Get value from nested dictionary using dot notation path"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    def _set_nested_value(self, data: dict, path: str, value: Any):
        """Set value in nested dictionary using dot notation path"""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def load_tab_setting(self, tab_name: str, key: str, default=None) -> Any:
        """Load a specific tab setting supporting nested keys with dot notation"""
        config = self._load_config()
        tabs = config.get('tabs', {})
        
        # Handle nested tab names (e.g., 'graph.general', 'graph.group.ts')
        if '.' in tab_name:
            return self._get_nested_value(tabs, f"{tab_name}.{key}", default)
        else:
            tab_config = tabs.get(tab_name, {})
            return tab_config.get(key, default)
    
    def save_tab_setting(self, tab_name: str, key: str, value: Any):
        """Save a specific tab setting supporting nested keys with dot notation"""
        config = self._load_config()
        if 'tabs' not in config:
            config['tabs'] = {}
        
        # Handle nested tab names (e.g., 'graph.general', 'graph.group.ts')
        if '.' in tab_name:
            self._set_nested_value(config['tabs'], f"{tab_name}.{key}", value)
        else:
            if tab_name not in config['tabs']:
                config['tabs'][tab_name] = {}
            config['tabs'][tab_name][key] = value
        
        self._save_config(config)
    
    def load_tab_settings(self, tab_name: str) -> Dict[str, Any]:
        """Load all settings for a specific tab supporting nested keys"""
        config = self._load_config()
        tabs = config.get('tabs', {})
        
        # Handle nested tab names
        if '.' in tab_name:
            return self._get_nested_value(tabs, tab_name, {})
        else:
            return tabs.get(tab_name, {})
    
    def save_tab_settings(self, tab_name: str, settings: Dict[str, Any]):
        """Save all settings for a specific tab supporting nested keys"""
        config = self._load_config()
        if 'tabs' not in config:
            config['tabs'] = {}
        
        # Handle nested tab names
        if '.' in tab_name:
            self._set_nested_value(config['tabs'], tab_name, settings)
        else:
            config['tabs'][tab_name] = settings
        
        self._save_config(config)
    
    def load_setting(self, key: str, default=None):
        """Load a specific setting (legacy method)"""
        config = self._load_config()
        return config.get(key, default)
    
    def save_setting(self, key: str, value):
        """Save a specific setting (legacy method)"""
        config = self._load_config()
        config[key] = value
        self._save_config(config)
