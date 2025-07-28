from .language_manager import LanguageManager
from .config_manager import ConfigManager


_language_manager = None
_config_manager = None


def get_language_manager():
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def get_config_manager():
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def t(key, **kwargs):
    return get_language_manager().translate(key, **kwargs)


def get_available_languages():
    return get_language_manager().get_available_languages()


def set_language(language_code):
    get_language_manager().set_language(language_code)
    get_config_manager().save_language(language_code)


def get_current_language():
    return get_language_manager().get_current_language()


def initialize():
    config_manager = get_config_manager()
    saved_language = config_manager.load_language()
    if saved_language:
        get_language_manager().set_language(saved_language)


__all__ = [
    "t",
    "get_available_languages",
    "set_language",
    "get_current_language",
    "get_config_manager",
    "initialize",
]
