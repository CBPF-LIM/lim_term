import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Union
import yaml
from ..i18n import t
import importlib

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
        # preference widgets are resolved in build_widget via context
    }
    return mapping.get(widget_type)


def build_widget(parent, spec: WidgetSpec, context) -> Any:
    widget_type = spec.get("widget")
    name = spec.get("name")
    layout = spec.get("layout", {})
    options = _resolve_i18n(spec.get("options", {}))

    # Resolve handlers by name from context
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

    # Preference widgets may be in the context module
    base_pkg = context.__class__.__module__.rsplit(".", 1)[0]  # e.g., 'limterm.gui'
    pref_mod_name = base_pkg + ".preference_widgets"
    try:
        pref_mod = importlib.import_module(pref_mod_name)
    except Exception:
        pref_mod = None
    PrefEntry = getattr(pref_mod, "PrefEntry", None) if pref_mod else None  # type: ignore
    PrefCombobox = getattr(pref_mod, "PrefCombobox", None) if pref_mod else None  # type: ignore
    PrefCheckbutton = getattr(pref_mod, "PrefCheckbutton", None) if pref_mod else None  # type: ignore

    widget = None
    cls = _get_widget_class(widget_type)
    if cls is not None:
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

    # Build children
    for child in spec.get("children", []):
        build_widget(widget, child, context)

    _apply_layout(widget, layout)
    return widget


def build_from_yaml(parent, yaml_path: str, context) -> Any:
    with open(yaml_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return build_widget(parent, spec, context)
