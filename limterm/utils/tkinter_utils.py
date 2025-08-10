import tkinter as tk
from typing import Callable, Optional


def widget_exists(widget) -> bool:
    try:
        return bool(widget) and widget.winfo_exists()
    except tk.TclError:
        return False


def safe_after(widget, delay_ms: int, callback: Callable) -> Optional[str]:
    if widget_exists(widget):
        try:
            return widget.after(delay_ms, callback)
        except tk.TclError:
            return None
    return None


def safe_after_cancel(widget, after_id) -> bool:
    if after_id and widget_exists(widget):
        try:
            widget.after_cancel(after_id)
            return True
        except tk.TclError:
            return False
    return False
