import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Union
import yaml
from ..i18n import t
import importlib
import os
import sys

WidgetSpec = Dict[str, Any]


def _resolve_i18n(value: Any) -> Any:
    if isinstance(value, str):
        if value.startswith("${") and value.endswith("}"):
            key = value[2:-1]
            return t(key)
        return value
    if isinstance(value, list):
        return [_resolve_i18n(v) for v in value]
    if isinstance(value, dict):
        return {
            (_resolve_i18n(k) if isinstance(k, str) else k): _resolve_i18n(v)
            for k, v in value.items()
        }
    return value


def _apply_layout(widget, layout: Dict[str, Any]):
    if not layout:
        return
    method = layout.get("method", "grid")
    params = {k: v for k, v in layout.items() if k != "method"}
    if method == "grid":
        widget.grid(**params)
    elif method == "pack":
        widget.pack(**params)
    elif method == "place":
        widget.place(**params)


def _get_widget_class(widget_type: str):
    mapping = {
        "Frame": ttk.Frame,
        "LabelFrame": ttk.LabelFrame,
        "Label": ttk.Label,
        "Button": ttk.Button,
        "Separator": ttk.Separator,
        "Combobox": ttk.Combobox,
        "Entry": ttk.Entry,
        "Text": tk.Text,
        "Scrollbar": tk.Scrollbar,
        "Notebook": ttk.Notebook,
        "PanedWindow": ttk.Panedwindow,
        "Canvas": tk.Canvas,
    }
    return mapping.get(widget_type)


def _resolve_option_references(options: Dict[str, Any], context: Any) -> Dict[str, Any]:
    def resolve_ref(val):
        if isinstance(val, str) and "." in val and not val.startswith("${"):
            parts = val.split(".")
            obj = context
            for p in parts:
                if hasattr(obj, p):
                    obj = getattr(obj, p)
                else:
                    return val
            return obj
        return val

    return {k: resolve_ref(v) for k, v in options.items()}


def build_widget(parent, spec: WidgetSpec, context) -> Any:
    widget_type = spec.get("widget")
    name = spec.get("name")
    layout = spec.get("layout", {})
    options = _resolve_i18n(spec.get("options", {}))

    handler_keys = [
        "command",
        "on_change",
    ]
    for hk in handler_keys:
        if hk in options and isinstance(options[hk], str):
            if hasattr(context, options[hk]):
                options[hk] = getattr(context, options[hk])
            else:
                options.pop(hk)

    base_pkg = context.__class__.__module__.rsplit(".", 1)[0]
    pref_mod_name = base_pkg + ".preference_widgets"
    try:
        pref_mod = importlib.import_module(pref_mod_name)
    except Exception:
        pref_mod = None
    PrefEntry = getattr(pref_mod, "PrefEntry", None) if pref_mod else None
    PrefCombobox = getattr(pref_mod, "PrefCombobox", None) if pref_mod else None
    PrefCheckbutton = getattr(pref_mod, "PrefCheckbutton", None) if pref_mod else None

    widget = None
    cls = _get_widget_class(widget_type)
    if cls is not None:
        options = _resolve_option_references(options, context)
        widget = cls(parent, **options)
    elif widget_type == "PrefEntry" and PrefEntry is not None:
        widget = PrefEntry(parent, **options)
    elif widget_type == "PrefCombobox" and PrefCombobox is not None:
        widget = PrefCombobox(parent, **options)
    elif widget_type == "PrefCheckbutton" and PrefCheckbutton is not None:
        widget = PrefCheckbutton(parent, **options)
    else:
        raise ValueError(f"Unsupported widget type: {widget_type}")

    if name:
        setattr(context, name, widget)

    for bind_spec in spec.get("bindings", []):
        ev = bind_spec.get("event")
        handler_name = bind_spec.get("handler")
        if ev and handler_name and hasattr(context, handler_name):
            try:
                widget.bind(ev, getattr(context, handler_name))
            except Exception:
                pass

    for child in spec.get("children", []):
        build_widget(widget, child, context)

    _apply_layout(widget, layout)
    return widget


def build_from_yaml(parent, yaml_path: str, context) -> Any:
    with open(yaml_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return build_widget(parent, spec, context)


def build_from_layout_name(parent, name: str, context) -> Any:
    mod_name = context.__class__.__module__
    mod = sys.modules.get(mod_name)
    base_dir = None
    if mod and hasattr(mod, "__file__") and mod.__file__:
        base_dir = os.path.dirname(os.path.abspath(mod.__file__))
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    package_root = os.path.dirname(base_dir)
    yaml_path = os.path.join(package_root, "ui", "layouts", f"{name}.yml")
    yaml_path = os.path.abspath(yaml_path)

    return build_from_yaml(parent, yaml_path, context)
