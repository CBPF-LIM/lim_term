import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Union
import yaml
from ..i18n import t
import importlib
import os
import sys
from tkinter import filedialog

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
        "Tk": tk.Tk,
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
        "Toplevel": tk.Toplevel,
        "Menu": tk.Menu,
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


def _bind_handlers_in_options(options: Dict[str, Any], context: Any, keys: List[str]):
    for hk in keys:
        if hk in options and isinstance(options[hk], str):
            if hasattr(context, options[hk]):
                options[hk] = getattr(context, options[hk])
            else:
                options.pop(hk)
    return options


def _fill_menu(
    menu_widget: tk.Menu,
    items: List[Dict[str, Any]],
    context: Any,
    variables_attr_name: Optional[str] = None,
):
    for item in items:
        item_type = item.get("type")
        if item_type == "separator":
            try:
                menu_widget.add_separator()
            except Exception:
                pass
            continue

        label = _resolve_i18n(item.get("label")) if item.get("label") else None

        if item_type == "command":
            cmd = item.get("command")
            if isinstance(cmd, str) and hasattr(context, cmd):
                cmd = getattr(context, cmd)
            try:
                menu_widget.add_command(label=label, command=cmd)
            except Exception:
                pass
        elif item_type == "checkbutton":

            initial = bool(item.get("initial", False))
            var = tk.BooleanVar(value=initial)

            vars_attr_local = item.get("variables_attr", variables_attr_name)
            var_key = item.get("var_key")
            if vars_attr_local and var_key:
                d = getattr(context, vars_attr_local, None)
                if not isinstance(d, dict):
                    setattr(context, vars_attr_local, {})
                    d = getattr(context, vars_attr_local)
                d[var_key] = var

            cmd = item.get("command")
            if isinstance(cmd, str) and hasattr(context, cmd):
                cmd = getattr(context, cmd)
            try:
                menu_widget.add_checkbutton(label=label, variable=var, command=cmd)
            except Exception:
                pass
        elif item_type == "cascade":

            submenu_spec = item.get("submenu")
            submenu = None
            if isinstance(submenu_spec, dict):

                submenu = _build_menu(menu_widget, submenu_spec, context)
            else:
                try:
                    submenu = tk.Menu(menu_widget, tearoff=0)
                except Exception:
                    submenu = None
            try:
                if submenu is not None:
                    menu_widget.add_cascade(label=label, menu=submenu)
            except Exception:
                pass
        else:

            pass


def _build_menu(widget_parent, spec: WidgetSpec, context):

    options = _resolve_i18n(spec.get("options", {}))
    menu_widget = tk.Menu(widget_parent, **options)

    if spec.get("attach_to_parent") and hasattr(widget_parent, "config"):
        try:
            widget_parent.config(menu=menu_widget)
        except Exception:
            pass

    items: List[Dict[str, Any]] = spec.get("items", []) or []

    variables_attr_name = spec.get("variables_attr")

    _fill_menu(menu_widget, items, context, variables_attr_name)

    name = spec.get("name")
    if name:
        setattr(context, name, menu_widget)
    return menu_widget


def _split_pref_options(options: Dict[str, Any]) -> (Dict[str, Any], Dict[str, Any]):
    pref_keys = {
        "pref_key",
        "default_value",
        "value_type",
        "on_change",
        "value_mapping",
    }
    widget_opts = {k: v for k, v in options.items() if k not in pref_keys}
    pref_opts = {k: v for k, v in options.items() if k in pref_keys}
    return widget_opts, pref_opts


def build_widget(parent, spec: WidgetSpec, context) -> Any:
    widget_type = spec.get("widget")
    name = spec.get("name")
    layout = spec.get("layout", {})
    options = _resolve_i18n(spec.get("options", {}))

    handler_keys = [
        "command",
        "on_change",
    ]
    options = _bind_handlers_in_options(options, context, handler_keys)

    base_pkg = context.__class__.__module__.rsplit(".", 1)[0]
    pref_mod_name = base_pkg + ".preference_widgets"
    try:
        pref_mod = importlib.import_module(pref_mod_name)
    except Exception:
        pref_mod = None
    PreferenceWidget = getattr(pref_mod, "PreferenceWidget", None) if pref_mod else None

    widget = None

    if widget_type == "Menu":
        widget = _build_menu(parent, spec, context)

        return widget

    cls = _get_widget_class(widget_type)

    if PreferenceWidget and widget_type in {
        "PrefEntry",
        "PrefCombobox",
        "PrefCheckbutton",
        "PrefScale",
        "PrefSpinbox",
    }:

        options = _resolve_option_references(options, context)
        widget_opts, pref_opts = _split_pref_options(options)

        base_cls_map = {
            "PrefEntry": tk.Entry,
            "PrefCombobox": ttk.Combobox,
            "PrefCheckbutton": ttk.Checkbutton,
            "PrefScale": tk.Scale,
            "PrefSpinbox": tk.Spinbox,
        }
        base_cls = base_cls_map[widget_type]
        base_widget = base_cls(parent, **widget_opts)

        pref_key = pref_opts.get("pref_key")
        default_value = pref_opts.get("default_value")
        value_type = pref_opts.get("value_type", str)
        on_change = pref_opts.get("on_change")
        value_mapping = pref_opts.get("value_mapping")

        widget = PreferenceWidget(
            base_widget,
            parent,
            pref_key=pref_key,
            default_value=default_value,
            value_type=value_type,
            on_change=on_change,
            value_mapping=value_mapping,
        )
    elif cls is not None:
        options = _resolve_option_references(options, context)

        _title = None
        if widget_type in {"Tk", "Toplevel"} and isinstance(options, dict):
            _title = options.pop("title", None)
        widget = cls(parent, **options)
        if _title and hasattr(widget, "title"):
            try:
                widget.title(_title)
            except Exception:
                pass
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

    parent_for_children = getattr(widget, "widget", widget)
    for child in spec.get("children", []):
        build_widget(parent_for_children, child, context)

    try:
        if not isinstance(parent, ttk.Notebook):
            _apply_layout(widget, layout)
    except Exception:

        try:
            _apply_layout(widget, layout)
        except Exception:
            pass
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


def extend_menu(
    menu_widget: tk.Menu,
    items: List[Dict[str, Any]],
    context: Any,
    variables_attr_name: Optional[str] = None,
) -> tk.Menu:
    try:
        _fill_menu(menu_widget, items or [], context, variables_attr_name)
    except Exception:
        pass
    return menu_widget


class _InfoDialogContext:
    def __init__(self, title: str, message: str):
        self._dialog = None
        self._title = title
        self._message = message

    def _on_ok(self):
        try:
            if self._dialog:
                self._dialog.destroy()
        except Exception:
            pass


def show_info_dialog(parent, title: str, message: str) -> None:
    ctx = _InfoDialogContext(title, message)
    try:

        build_from_layout_name(parent, "info_dialog", ctx)
        dlg = getattr(ctx, "_dialog", None)
        if dlg is not None:
            try:
                dlg.title(title)
            except Exception:
                pass

            try:
                frame = dlg.winfo_children()[0]
                label = frame.winfo_children()[0]
                if hasattr(label, "configure"):
                    label.configure(text=message)
            except Exception:
                pass
            try:
                dlg.transient(parent)
            except Exception:
                pass
            try:
                dlg.grab_set()
            except Exception:
                pass
            try:
                dlg.focus_set()
            except Exception:
                pass
            try:
                parent.wait_window(dlg)
            except Exception:
                pass
    except Exception:
        pass


class _YesNoDialogContext:
    def __init__(self, title: str, message: str):
        self._dialog = None
        self.result = False
        self._title = title
        self._message = message

    def _on_yes(self):
        self.result = True
        try:
            if self._dialog:
                self._dialog.destroy()
        except Exception:
            pass

    def _on_no(self):
        self.result = False
        try:
            if self._dialog:
                self._dialog.destroy()
        except Exception:
            pass


def ask_yes_no(parent, title: str, message: str) -> bool:
    ctx = _YesNoDialogContext(title, message)
    try:
        build_from_layout_name(parent, "yes_no_dialog", ctx)
        dlg = getattr(ctx, "_dialog", None)
        if dlg is not None:
            try:
                dlg.title(title)
            except Exception:
                pass
            try:
                frame = dlg.winfo_children()[0]
                label = frame.winfo_children()[0]
                if hasattr(label, "configure"):
                    label.configure(text=message)
            except Exception:
                pass
            try:
                dlg.transient(parent)
            except Exception:
                pass
            try:
                dlg.grab_set()
            except Exception:
                pass
            try:
                dlg.focus_set()
            except Exception:
                pass
            try:
                parent.wait_window(dlg)
            except Exception:
                pass
        return bool(getattr(ctx, "result", False))
    except Exception:
        return False


def ask_open_filename(
    parent=None,
    title: Optional[str] = None,
    initialdir: Optional[str] = None,
    filetypes: Optional[List[tuple]] = None,
    defaultextension: Optional[str] = None,
) -> Optional[str]:
    try:
        return (
            filedialog.askopenfilename(
                title=title or "",
                initialdir=initialdir or None,
                filetypes=filetypes or [("All files", "*.*")],
                defaultextension=defaultextension or None,
            )
            or None
        )
    except Exception:
        return None


def ask_save_as(
    parent=None,
    title: Optional[str] = None,
    initialdir: Optional[str] = None,
    initialfile: Optional[str] = None,
    filetypes: Optional[List[tuple]] = None,
    defaultextension: Optional[str] = None,
) -> Optional[str]:
    try:
        return (
            filedialog.asksaveasfilename(
                title=title or "",
                initialdir=initialdir or None,
                initialfile=initialfile or None,
                filetypes=filetypes or [("All files", "*.*")],
                defaultextension=defaultextension or None,
            )
            or None
        )
    except Exception:
        return None
