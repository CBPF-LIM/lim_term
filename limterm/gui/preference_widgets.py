"""
Preference-aware wrapper widgets that automatically save/load values from configuration.

This module provides wrapper classes around standard tkinter widgets that automatically
handle preference persistence without requiring manual event binding or save/load logic.
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Union, Dict, Callable
from ..i18n import get_config_manager


class PreferenceWidget:
    """
    Base wrapper class for tkinter widgets that automatically handles preference persistence.
    
    This wrapper:
    1. Creates the underlying tkinter widget with provided parameters
    2. Automatically loads initial value from preferences
    3. Binds to appropriate change events based on widget type
    4. Saves values to preferences immediately when changed
    5. Exposes all methods/properties of the underlying widget
    """
    
    def __init__(self, widget_class, parent, pref_key: str, default_value: Any = None, 
                 value_type: type = str, on_change: Optional[Callable] = None, **widget_kwargs):
        """
        Initialize a preference-aware widget wrapper.
        
        Args:
            widget_class: The tkinter widget class (e.g., tk.Entry, ttk.Combobox)
            parent: Parent tkinter widget
            pref_key: Dot-notation preference key (e.g., 'graph.general.x_column')
            default_value: Default value if not found in preferences
            value_type: Type for value conversion (str, int, float, bool)
            on_change: Optional callback when value changes (called after saving to prefs)
            **widget_kwargs: All other parameters passed to the widget constructor
        """
        self.pref_key = pref_key
        self.default_value = default_value
        self.value_type = value_type
        self.on_change = on_change
        self.config_manager = get_config_manager()
        self._tkinter_var = None  # Store reference to tkinter variable for widgets that need it
        
        # Parse the preference key into section and key
        self._parse_pref_key()
        
        # Create the underlying widget
        self.widget = widget_class(parent, **widget_kwargs)
        
        # Set up automatic preference handling
        self._setup_preference_handling()
        
        # Load initial value from preferences
        self._load_from_preferences()
    
    def _parse_pref_key(self):
        """Parse the dot-notation preference key into section and key parts."""
        parts = self.pref_key.split('.')
        if len(parts) < 2:
            raise ValueError(f"Preference key must have at least 2 parts separated by dots: {self.pref_key}")
        
        # Last part is the key, everything else is the section
        self.pref_section = '.'.join(parts[:-1])
        self.pref_name = parts[-1]
    
    def _setup_preference_handling(self):
        """Set up automatic change detection based on widget type."""
        widget_type = type(self.widget).__name__
        
        if widget_type in ['Entry']:
            # For Entry widgets, save on key release and focus out
            self.widget.bind('<KeyRelease>', self._on_change_event)
            self.widget.bind('<FocusOut>', self._on_change_event)
            
        elif widget_type in ['Combobox']:
            # For Combobox, save on selection change
            self.widget.bind('<<ComboboxSelected>>', self._on_change_event)
            
        elif widget_type in ['Checkbutton']:
            # For Checkbutton, we need to wrap the command
            # First, ensure the widget has a variable and store a reference to it
            var = self.widget.cget('variable')
            if not var or isinstance(var, str):
                # Create a new BooleanVar if none exists or if it's just a string name
                self._tkinter_var = tk.BooleanVar()
                self.widget.config(variable=self._tkinter_var)
            else:
                # Store reference to existing variable
                self._tkinter_var = var
            
            original_command = self.widget.cget('command') if self.widget.cget('command') else None
            self.widget.config(command=lambda: self._on_checkbutton_change(original_command))
            
        elif widget_type in ['Scale']:
            # For Scale, save on value change
            original_command = self.widget.cget('command') if self.widget.cget('command') else None
            self.widget.config(command=lambda val: self._on_scale_change(val, original_command))
            
        elif widget_type in ['Spinbox']:
            # For Spinbox, save on key release, focus out, and button clicks
            self.widget.bind('<KeyRelease>', self._on_change_event)
            self.widget.bind('<FocusOut>', self._on_change_event)
            self.widget.bind('<ButtonRelease-1>', self._on_change_event)
            
        else:
            # For other widgets, try to bind to common events
            try:
                self.widget.bind('<KeyRelease>', self._on_change_event)
                self.widget.bind('<FocusOut>', self._on_change_event)
            except tk.TclError:
                # Widget doesn't support these events, that's ok
                pass
    
    def _on_change_event(self, event=None):
        """Handle change events for most widget types."""
        try:
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")
    
    def _on_checkbutton_change(self, original_command):
        """Handle Checkbutton changes."""
        try:
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
            if original_command:
                original_command()
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")
    
    def _on_scale_change(self, value, original_command):
        """Handle Scale changes."""
        try:
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
            if original_command:
                original_command(value)
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")
    
    def _get_widget_value(self) -> Any:
        """Get the current value from the widget."""
        widget_type = type(self.widget).__name__
        
        if widget_type in ['Entry', 'Spinbox']:
            return self.widget.get()
            
        elif widget_type in ['Combobox']:
            return self.widget.get()
            
        elif widget_type in ['Checkbutton']:
            # For Checkbutton, use our stored variable reference
            if self._tkinter_var and hasattr(self._tkinter_var, 'get'):
                return self._tkinter_var.get()
            else:
                # Fallback: try to get variable from widget
                var = self.widget.cget('variable')
                if var and hasattr(var, 'get') and callable(var.get):
                    return var.get()
                else:
                    return False
                
        elif widget_type in ['Scale']:
            return self.widget.get()
            
        else:
            # Try common methods
            if hasattr(self.widget, 'get'):
                return self.widget.get()
            else:
                raise NotImplementedError(f"Don't know how to get value from {widget_type}")
    
    def _set_widget_value(self, value: Any):
        """Set the widget value."""
        widget_type = type(self.widget).__name__
        
        if widget_type in ['Entry', 'Spinbox']:
            self.widget.delete(0, tk.END)
            self.widget.insert(0, str(value))
            
        elif widget_type in ['Combobox']:
            self.widget.set(str(value))
            
        elif widget_type in ['Checkbutton']:
            # For Checkbutton, use our stored variable reference
            if self._tkinter_var and hasattr(self._tkinter_var, 'set'):
                try:
                    self._tkinter_var.set(bool(value))
                except Exception as e:
                    # Recreate the variable if there's an issue
                    self._tkinter_var = tk.BooleanVar(value=bool(value))
                    self.widget.config(variable=self._tkinter_var)
            else:
                # Create a new variable if something went wrong
                self._tkinter_var = tk.BooleanVar(value=bool(value))
                self.widget.config(variable=self._tkinter_var)
                
        elif widget_type in ['Scale']:
            self.widget.set(value)
            
        else:
            # Try common methods
            if hasattr(self.widget, 'set'):
                self.widget.set(value)
            elif hasattr(self.widget, 'delete') and hasattr(self.widget, 'insert'):
                self.widget.delete(0, tk.END)
                self.widget.insert(0, str(value))
            else:
                raise NotImplementedError(f"Don't know how to set value for {widget_type}")
    
    def _convert_value(self, value: Any) -> Any:
        """Convert value to the specified type."""
        if value is None:
            return self.default_value
            
        try:
            if self.value_type == bool:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                else:
                    return bool(value)
            elif self.value_type == int:
                return int(value)
            elif self.value_type == float:
                return float(value)
            else:
                return str(value)
        except (ValueError, TypeError):
            return self.default_value
    
    def _load_from_preferences(self):
        """Load the initial value from preferences."""
        try:
            saved_value = self.config_manager.load_tab_setting(
                self.pref_section, self.pref_name, self.default_value
            )
            converted_value = self._convert_value(saved_value)
            self._set_widget_value(converted_value)
        except Exception as e:
            print(f"Warning: Could not load preference {self.pref_key}: {e}")
            if self.default_value is not None:
                self._set_widget_value(self.default_value)
    
    def _save_to_preferences(self):
        """Save the current widget value to preferences."""
        try:
            current_value = self._get_widget_value()
            converted_value = self._convert_value(current_value)
            self.config_manager.save_tab_setting(
                self.pref_section, self.pref_name, converted_value
            )
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")
    
    def get_value(self):
        """Get the current widget value, converted to the specified type."""
        raw_value = self._get_widget_value()
        return self._convert_value(raw_value)
    
    def set_value(self, value):
        """Set the widget value and save to preferences."""
        converted_value = self._convert_value(value)
        self._set_widget_value(converted_value)
        self._save_to_preferences()
    
    def __getattr__(self, name):
        """Delegate all other attribute access to the underlying widget."""
        return getattr(self.widget, name)


# Convenience functions for common widget types
def PrefEntry(parent, pref_key: str, default_value: str = "", 
              on_change: Optional[Callable] = None, **kwargs) -> PreferenceWidget:
    """Create a preference-aware Entry widget."""
    return PreferenceWidget(tk.Entry, parent, pref_key, default_value, str, on_change, **kwargs)


def PrefCombobox(parent, pref_key: str, default_value: str = "", 
                 on_change: Optional[Callable] = None, **kwargs) -> PreferenceWidget:
    """Create a preference-aware Combobox widget."""
    return PreferenceWidget(ttk.Combobox, parent, pref_key, default_value, str, on_change, **kwargs)


def PrefCheckbutton(parent, pref_key: str, default_value: bool = False, 
                    on_change: Optional[Callable] = None, **kwargs) -> PreferenceWidget:
    """Create a preference-aware Checkbutton widget."""
    # Ensure we have a BooleanVar for the checkbutton
    if 'variable' not in kwargs:
        kwargs['variable'] = tk.BooleanVar()
    return PreferenceWidget(ttk.Checkbutton, parent, pref_key, default_value, bool, on_change, **kwargs)


def PrefScale(parent, pref_key: str, default_value: float = 0.0, 
              on_change: Optional[Callable] = None, **kwargs) -> PreferenceWidget:
    """Create a preference-aware Scale widget."""
    return PreferenceWidget(tk.Scale, parent, pref_key, default_value, float, on_change, **kwargs)


def PrefSpinbox(parent, pref_key: str, default_value: Union[int, float] = 0, 
                value_type: type = int, on_change: Optional[Callable] = None, **kwargs) -> PreferenceWidget:
    """Create a preference-aware Spinbox widget."""
    return PreferenceWidget(tk.Spinbox, parent, pref_key, default_value, value_type, on_change, **kwargs)
