import tkinter as tk
from tkinter import ttk
from ..config import COLOR_KEYS, MARKER_MAPPING
from ..i18n import t


class GraphOptionsWindow:
    def __init__(self, parent, serial_gui):
        self.window = tk.Toplevel(parent)
        self.window.title(t("ui.graph_tab.graph_options_title"))
        self.serial_gui = serial_gui

        self._create_widgets()
        self._load_current_settings()

    def _get_translated_graph_types(self):
        """Get translated graph type options"""
        return [t("ui.graph_types.line"), t("ui.graph_types.scatter")]

    def _get_translated_colors(self):
        """Get translated color options"""
        return [t(f"ui.colors.{color}") for color in COLOR_KEYS]

    def _get_translated_markers(self):
        """Get translated marker options"""
        marker_keys = [
            "circle",
            "square",
            "triangle",
            "diamond",
            "star",
            "plus",
            "x",
            "vline",
            "hline",
            "hexagon",
        ]
        return [t(f"ui.markers.{marker}") for marker in marker_keys]

    def _get_original_marker(self, translated_marker):
        """Convert translated marker back to matplotlib marker"""
        marker_mapping = {}
        for key, value in MARKER_MAPPING.items():
            marker_mapping[t(f"ui.markers.{key}")] = value
        return marker_mapping.get(translated_marker, "o")

    def _get_translated_marker(self, original_marker):
        """Convert matplotlib marker to translated marker"""
        for key, value in MARKER_MAPPING.items():
            if value == original_marker:
                return t(f"ui.markers.{key}")
        return t("ui.markers.circle")

    def _create_widgets(self):
        ttk.Label(self.window, text=t("ui.graph_tab.type_label")).grid(
            column=0, row=0, padx=10, pady=10
        )
        self.graph_type_combobox = ttk.Combobox(
            self.window, state="readonly", values=self._get_translated_graph_types()
        )
        self.graph_type_combobox.grid(column=1, row=0, padx=10, pady=10)

        ttk.Label(self.window, text=t("ui.graph_tab.color_label")).grid(
            column=0, row=1, padx=10, pady=10
        )
        self.color_combobox = ttk.Combobox(
            self.window, state="readonly", values=self._get_translated_colors()
        )
        self.color_combobox.grid(column=1, row=1, padx=10, pady=10)

        ttk.Label(self.window, text=t("ui.graph_tab.window_label")).grid(
            column=0, row=2, padx=10, pady=10
        )
        self.data_window_entry = ttk.Entry(self.window)
        self.data_window_entry.grid(column=1, row=2, padx=10, pady=10)
        self.data_window_entry.insert(0, "0")

        ttk.Label(self.window, text=t("ui.graph_tab.min_y_label")).grid(
            column=0, row=3, padx=10, pady=10
        )
        self.min_y_entry = ttk.Entry(self.window)
        self.min_y_entry.grid(column=1, row=3, padx=10, pady=10)

        ttk.Label(self.window, text=t("ui.graph_tab.max_y_label")).grid(
            column=0, row=4, padx=10, pady=10
        )
        self.max_y_entry = ttk.Entry(self.window)
        self.max_y_entry.grid(column=1, row=4, padx=10, pady=10)

        ttk.Label(self.window, text=t("ui.graph_tab.point_label")).grid(
            column=0, row=5, padx=10, pady=10
        )
        self.dot_type_combobox = ttk.Combobox(
            self.window, state="readonly", values=self._get_translated_markers()
        )
        self.dot_type_combobox.grid(column=1, row=5, padx=10, pady=10)

        self.apply_button = ttk.Button(
            self.window,
            text=t("ui.graph_tab.apply_button"),
            command=self._apply_settings,
        )
        self.apply_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10)

    def _load_current_settings(self):
        settings = self.serial_gui.graph_settings

        self.graph_type_combobox.set(settings.get("type", t("ui.graph_types.line")))
        self.color_combobox.set(settings.get("color", t("ui.colors.blue")))
        self.data_window_entry.delete(0, "end")
        self.data_window_entry.insert(0, str(settings.get("data_window", "0")))
        self.min_y_entry.delete(0, "end")
        self.min_y_entry.insert(0, settings.get("min_y", ""))
        self.max_y_entry.delete(0, "end")
        self.max_y_entry.insert(0, settings.get("max_y", ""))

        current_dot_type = settings.get("dot_type", "o")
        translated_marker = self._get_translated_marker(current_dot_type)
        self.dot_type_combobox.set(translated_marker)

    def _apply_settings(self):
        try:
            settings = {}

            if self.graph_type_combobox.get():
                settings["type"] = self.graph_type_combobox.get()
            if self.color_combobox.get():
                settings["color"] = self.color_combobox.get()
            if self.data_window_entry.get():
                settings["data_window"] = int(self.data_window_entry.get())
            if self.min_y_entry.get():
                settings["min_y"] = self.min_y_entry.get()
            if self.max_y_entry.get():
                settings["max_y"] = self.max_y_entry.get()
            if self.dot_type_combobox.get():
                settings["dot_type"] = self._get_original_marker(
                    self.dot_type_combobox.get()
                )

            self.serial_gui.update_graph_settings(settings)
            print("Configurações aplicadas:", settings)
            self.window.destroy()

        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")
