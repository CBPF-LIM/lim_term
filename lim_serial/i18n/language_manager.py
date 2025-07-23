"""
Language Manager for handling translations
"""
import os
import yaml
from typing import Dict, Any, List, Optional


class LanguageManager:
    """Manages language loading and translation"""
    
    def __init__(self):
        self.languages = {}
        self.current_language = "en"
        self.fallback_language = "en"
        self.languages_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "languages")
        self._load_all_languages()
    
    def _load_all_languages(self):
        """Load all available language files"""
        if not os.path.exists(self.languages_dir):
            print(f"Warning: Languages directory not found: {self.languages_dir}")
            return
        
        for filename in os.listdir(self.languages_dir):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                language_code = os.path.splitext(filename)[0]
                try:
                    self._load_language(language_code)
                except Exception as e:
                    print(f"Error loading language {language_code}: {e}")
    
    def _load_language(self, language_code: str):
        """Load a specific language file"""
        file_path = os.path.join(self.languages_dir, f"{language_code}.yml")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.languages[language_code] = yaml.safe_load(file)
            except Exception as e:
                print(f"Error loading language file {file_path}: {e}")
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """Get list of available languages with their display names"""
        languages = []
        for code, data in self.languages.items():
            if data and 'language' in data:
                languages.append({
                    'code': code,
                    'name': data['language'].get('name', code.upper()),
                    'display_name': data['language'].get('name', code.upper())
                })
        return languages
    
    def set_language(self, language_code: str):
        """Set the current language"""
        if language_code in self.languages:
            self.current_language = language_code
        else:
            print(f"Warning: Language {language_code} not found, using {self.fallback_language}")
            self.current_language = self.fallback_language
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self.current_language
    
    def translate(self, key: str, **kwargs) -> str:
        """Translate a key with optional parameters"""
        # Try current language first
        translation = self._get_translation(key, self.current_language)
        
        # Fallback to English if not found
        if translation is None and self.current_language != self.fallback_language:
            translation = self._get_translation(key, self.fallback_language)
        
        # If still not found, return the key itself
        if translation is None:
            print(f"Warning: Translation not found for key: {key}")
            return key
        
        # Format with parameters if provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError) as e:
                print(f"Warning: Error formatting translation for key {key}: {e}")
                return translation
        
        return translation
    
    def _get_translation(self, key: str, language_code: str) -> Optional[str]:
        """Get translation for a specific key and language"""
        if language_code not in self.languages:
            return None
        
        # Navigate through nested keys (e.g., "ui.main_window.title")
        current = self.languages[language_code]
        keys = key.split('.')
        
        try:
            for k in keys:
                current = current[k]
            return str(current) if current is not None else None
        except (KeyError, TypeError):
            return None
