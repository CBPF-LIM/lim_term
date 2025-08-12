import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Union, Dict, Callable
from ..i18n import get_config_manager


class PreferenceWidget:

    def __init__(
        self,
        widget_or_class,
        parent,
        pref_key: str,
        default_value: Any = None,
        value_type: type = str,
        on_change: Optional[Callable] = None,
        value_mapping: Optional[Dict[str, str]] = None,
        **widget_kwargs,
    ):
        self.pref_key = pref_key
        self.default_value = default_value
        self.value_type = value_type
        self.on_change = on_change
        self.config_manager = get_config_manager()
        self._tkinter_var = None
        self.value_mapping = value_mapping or {}
        self.reverse_mapping = (
            {v: k for k, v in self.value_mapping.items()} if value_mapping else {}
        )

        self._current_value: Any = default_value

        self._parse_pref_key()

                                                                                       
                                                                                           
                                                 
        try:
            if isinstance(widget_or_class, (tk.Widget, ttk.Widget)):
                self.widget = widget_or_class
            elif isinstance(widget_or_class, type):
                                                                                      
                self.widget = widget_or_class(parent, **widget_kwargs)
            else:
                                                           
                self.widget = widget_or_class
        except Exception:
                                                                   
            if callable(widget_or_class):
                self.widget = widget_or_class(parent, **widget_kwargs)
            else:
                raise

        self._setup_preference_handling()

        self._load_from_preferences()

    def _parse_pref_key(self):
        parts = self.pref_key.split(".")
        if len(parts) < 2:
            raise ValueError(
                f"Preference key must have at least 2 parts separated by dots: {self.pref_key}"
            )

        self.pref_section = ".".join(parts[:-1])
        self.pref_name = parts[-1]

    def _setup_preference_handling(self):
        widget_type = type(self.widget).__name__

        if widget_type in ["Entry"]:
            self.widget.bind("<KeyRelease>", self._on_change_event)
            self.widget.bind("<FocusOut>", self._on_change_event)

        elif widget_type in ["Combobox"]:
            self.widget.bind("<<ComboboxSelected>>", self._on_change_event)

        elif widget_type in ["Checkbutton"]:
            var = self.widget.cget("variable")
            if not var or isinstance(var, str):
                self._tkinter_var = tk.BooleanVar()
                self.widget.config(variable=self._tkinter_var)
            else:
                self._tkinter_var = var

            original_command = (
                self.widget.cget("command") if self.widget.cget("command") else None
            )
            self.widget.config(
                command=lambda: self._on_checkbutton_change(original_command)
            )

        elif widget_type in ["Scale"]:
            original_command = (
                self.widget.cget("command") if self.widget.cget("command") else None
            )
            self.widget.config(
                command=lambda val: self._on_scale_change(val, original_command)
            )

        elif widget_type in ["Spinbox"]:
            self.widget.bind("<KeyRelease>", self._on_change_event)
            self.widget.bind("<FocusOut>", self._on_change_event)
            self.widget.bind("<ButtonRelease-1>", self._on_change_event)

        else:
            try:
                self.widget.bind("<KeyRelease>", self._on_change_event)
                self.widget.bind("<FocusOut>", self._on_change_event)
            except tk.TclError:
                pass

    def _on_change_event(self, event=None):
        try:

            try:
                self._current_value = self._get_widget_value_direct()
            except Exception:
                pass
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")

    def _on_checkbutton_change(self, original_command):
        try:

            val = False
            try:
                if self._tkinter_var and hasattr(self._tkinter_var, "get"):
                    val = bool(self._tkinter_var.get())
                else:

                    val = bool(self.widget.instate(["selected"]))
            except Exception:
                pass
            self._current_value = val
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
            if original_command:
                original_command()
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")

    def _on_scale_change(self, value, original_command):
        try:
            try:
                self._current_value = self._get_widget_value_direct()
            except Exception:
                pass
            self._save_to_preferences()
            if self.on_change:
                self.on_change()
            if original_command:
                original_command(value)
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")

    def _get_widget_value_direct(self) -> Any:
        widget_type = type(self.widget).__name__

        if widget_type in ["Entry", "Spinbox"]:
            return self.widget.get()

        elif widget_type in ["Combobox"]:
            display_value = self.widget.get()

            if self.value_mapping and display_value in self.value_mapping:
                return self.value_mapping[display_value]
            return display_value

        elif widget_type in ["Checkbutton"]:
            if self._tkinter_var and hasattr(self._tkinter_var, "get"):
                return self._tkinter_var.get()
            else:
                var = self.widget.cget("variable")
                if var and hasattr(var, "get") and callable(var.get):
                    return var.get()
                else:
                    return False

        elif widget_type in ["Scale"]:
            return self.widget.get()

        else:
            if hasattr(self.widget, "get"):
                return self.widget.get()
            else:
                raise NotImplementedError(
                    f"Don't know how to get value from {widget_type}"
                )

    def _get_widget_value(self) -> Any:
        widget_type = type(self.widget).__name__

        if widget_type in ["Checkbutton"]:

            return bool(self._current_value)

        return self._get_widget_value_direct()

    def _set_widget_value(self, value: Any):
        widget_type = type(self.widget).__name__

        if widget_type in ["Entry", "Spinbox"]:
            self.widget.delete(0, tk.END)
            self.widget.insert(0, str(value))

        elif widget_type in ["Combobox"]:
            if self.reverse_mapping and value in self.reverse_mapping:
                display_value = self.reverse_mapping[value]
                self.widget.set(display_value)
            else:
                self.widget.set(str(value))

        elif widget_type in ["Checkbutton"]:

            if self._tkinter_var and hasattr(self._tkinter_var, "set"):
                try:
                    self._tkinter_var.set(bool(value))
                except Exception:
                    self._tkinter_var = tk.BooleanVar(value=bool(value))
                    self.widget.config(variable=self._tkinter_var)
            else:
                self._tkinter_var = tk.BooleanVar(value=bool(value))
                self.widget.config(variable=self._tkinter_var)

        elif widget_type in ["Scale"]:
            self.widget.set(value)

        else:
            if hasattr(self.widget, "set"):
                self.widget.set(value)
            elif hasattr(self.widget, "delete") and hasattr(self.widget, "insert"):
                self.widget.delete(0, tk.END)
                self.widget.insert(0, str(value))
            else:
                raise NotImplementedError(
                    f"Don't know how to set value for {widget_type}"
                )

        try:
            if widget_type == "Checkbutton":
                self._current_value = bool(value)
            else:
                self._current_value = self._convert_value(value)
        except Exception:
            self._current_value = value

    def _convert_value(self, value: Any) -> Any:
        if value is None:
            return self.default_value

        try:
            if self.value_type == bool:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
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
        try:
            current_value = self._get_widget_value()
            converted_value = self._convert_value(current_value)
            self.config_manager.save_tab_setting(
                self.pref_section, self.pref_name, converted_value
            )
        except Exception as e:
            print(f"Warning: Could not save preference {self.pref_key}: {e}")

    def get_value(self):
        raw_value = self._get_widget_value()
        return self._convert_value(raw_value)

    def set_value(self, value):
        converted_value = self._convert_value(value)
        self._set_widget_value(converted_value)
        self._save_to_preferences()

    def refresh_language_mapping(
        self, new_value_mapping: Optional[Dict[str, str]] = None
    ):
        if new_value_mapping is not None:
            self.value_mapping = new_value_mapping
            self.reverse_mapping = {v: k for k, v in self.value_mapping.items()}

            widget_type = type(self.widget).__name__
            if widget_type in ["Combobox"] and hasattr(self.widget, "configure"):
                new_values = list(self.value_mapping.keys())
                self.widget.configure(values=new_values)

                self._load_from_preferences()

    def __getattr__(self, name):
        return getattr(self.widget, name)


def PrefEntry(
    parent,
    pref_key: str,
    default_value: str = "",
    on_change: Optional[Callable] = None,
    **kwargs,
) -> PreferenceWidget:
    return PreferenceWidget(
        tk.Entry, parent, pref_key, default_value, str, on_change, **kwargs
    )


def PrefCombobox(
    parent,
    pref_key: str,
    default_value: str = "",
    on_change: Optional[Callable] = None,
    value_mapping: Optional[Dict[str, str]] = None,
    **kwargs,
) -> PreferenceWidget:
    return PreferenceWidget(
        ttk.Combobox,
        parent,
        pref_key,
        default_value,
        str,
        on_change,
        value_mapping,
        **kwargs,
    )


def PrefCheckbutton(
    parent,
    pref_key: str,
    default_value: bool = False,
    on_change: Optional[Callable] = None,
    **kwargs,
) -> PreferenceWidget:

    if "variable" not in kwargs:
        kwargs["variable"] = tk.BooleanVar()
    return PreferenceWidget(
        ttk.Checkbutton, parent, pref_key, default_value, bool, on_change, **kwargs
    )


def PrefScale(
    parent,
    pref_key: str,
    default_value: float = 0.0,
    on_change: Optional[Callable] = None,
    **kwargs,
) -> PreferenceWidget:
    return PreferenceWidget(
        tk.Scale, parent, pref_key, default_value, float, on_change, **kwargs
    )


def PrefSpinbox(
    parent,
    pref_key: str,
    default_value: Union[int, float] = 0,
    value_type: type = int,
    on_change: Optional[Callable] = None,
    **kwargs,
) -> PreferenceWidget:
    return PreferenceWidget(
        tk.Spinbox, parent, pref_key, default_value, value_type, on_change, **kwargs
    )
