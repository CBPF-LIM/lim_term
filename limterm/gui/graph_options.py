from ..config import COLOR_KEYS, MARKER_MAPPING
from ..i18n import t
from ..utils.ui_builder import build_from_spec


class GraphOptionsWindow:
    def __init__(self, parent, serial_gui):

        self.window = build_from_spec(
            parent,
            {
                "widget": "Toplevel",
                "options": {"title": "${ui.graph_tab.graph_options_title}"},
            },
            self,
        )
        self.serial_gui = serial_gui

        self._create_widgets()
        self._load_current_settings()

    def _get_translated_graph_types(self):
        return [t("ui.graph_types.line"), t("ui.graph_types.scatter")]

    def _get_translated_colors(self):
        return [t(f"ui.colors.{color}") for color in COLOR_KEYS]

    def _get_translated_markers(self):
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
        marker_mapping = {}
        for key, value in MARKER_MAPPING.items():
            marker_mapping[t(f"ui.markers.{key}")] = value
        return marker_mapping.get(translated_marker, "o")

    def _get_translated_marker(self, original_marker):
        for key, value in MARKER_MAPPING.items():
            if value == original_marker:
                return t(f"ui.markers.{key}")
        return t("ui.markers.circle")

    def _create_widgets(self):
        spec = {
            "widget": "Frame",
            "name": "root",
            "layout": {
                "method": "pack",
                "fill": "both",
                "expand": True,
                "padx": 10,
                "pady": 10,
            },
            "children": [
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.type_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 0,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Combobox",
                    "name": "graph_type_combobox",
                    "options": {
                        "state": "readonly",
                        "values": self._get_translated_graph_types(),
                    },
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 0,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.color_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 1,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Combobox",
                    "name": "color_combobox",
                    "options": {
                        "state": "readonly",
                        "values": self._get_translated_colors(),
                    },
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 1,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.window_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 2,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Entry",
                    "name": "data_window_entry",
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 2,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.min_y_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 3,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Entry",
                    "name": "min_y_entry",
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 3,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.max_y_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 4,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Entry",
                    "name": "max_y_entry",
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 4,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Label",
                    "options": {"text": "${ui.graph_tab.point_label}"},
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 5,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Combobox",
                    "name": "dot_type_combobox",
                    "options": {
                        "state": "readonly",
                        "values": self._get_translated_markers(),
                    },
                    "layout": {
                        "method": "grid",
                        "column": 1,
                        "row": 5,
                        "padx": 5,
                        "pady": 5,
                    },
                },
                {
                    "widget": "Button",
                    "name": "apply_button",
                    "options": {
                        "text": "${ui.graph_tab.apply_button}",
                        "command": _apply_settings,
                    },
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 6,
                        "columnspan": 2,
                        "padx": 5,
                        "pady": 10,
                    },
                },
            ],
        }
        build_from_spec(self.window, spec, self)
        if hasattr(self, "data_window_entry"):
            try:
                self.data_window_entry.insert(0, "0")
            except Exception:
                pass

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
            self.window.destroy()

        except Exception as e:
            print(t("errors.config_save_error", error=str(e)))
