import tkinter as tk
from tkinter import ttk
from ..core import GraphManager
from ..utils import DataParser
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN, MARKER_MAPPING
from ..i18n import t, get_config_manager
from .preference_widgets import PrefEntry, PrefCombobox, PrefCheckbutton


class GraphTab:
    def __init__(self, parent, data_tab, open_options_callback):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.graph_settings = {}
        self.options_visible = False
        self.is_paused = False

        self.refresh_rate_ms = 33
        self.refresh_timer_id = None
        self.refresh_counter = 0
        self.debug_refresh = False
        self.last_render_time = 0
        self.series_widgets = []

        self._create_widgets()

    def _create_widgets(self):
        top_row = ttk.Frame(self.frame)
        top_row.grid(column=0, row=0, sticky="w", padx=10, pady=10)

        self.x_label = ttk.Label(top_row, text=t("ui.graph_tab.column_x"))
        self.x_label.pack(side="left", padx=(0, 5))
        self.x_column_entry = PrefEntry(
            top_row,
            pref_key="graph.general.x_column",
            default_value=str(DEFAULT_X_COLUMN),
            width=10,
            on_change=self._on_setting_change,
        )
        self.x_column_entry.pack(side="left", padx=(0, 15))

        self.plot_button = ttk.Button(
            top_row, text=t("ui.graph_tab.update_graph"), command=self.plot_graph
        )
        self.plot_button.pack(side="left", padx=(0, 10))

        self.pause_button = ttk.Button(
            top_row, text=t("ui.graph_tab.pause"), command=self._toggle_pause
        )
        self.pause_button.pack(side="left", padx=(0, 10))

        self.options_button = ttk.Button(
            top_row, text=t("ui.graph_tab.show_options"), command=self._toggle_options
        )
        self.options_button.pack(side="left", padx=(0, 10))

        self.save_button = ttk.Button(
            top_row, text=t("ui.graph_tab.save_png"), command=self._save_chart
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.y_columns_frame = ttk.LabelFrame(
            self.frame, text=t("ui.graph_tab.y_columns")
        )
        self.y_columns_frame.grid(
            column=0, row=1, columnspan=4, padx=10, pady=5, sticky="ew"
        )

        self.y_entries = []
        for i in range(1, 6):
            y_frame = ttk.Frame(self.y_columns_frame)
            y_frame.grid(column=i - 1, row=0, padx=5, pady=5, sticky="w")

            y_label = ttk.Label(y_frame, text=t(f"ui.graph_tab.column_y{i}"))
            y_label.pack(side="top")
            y_entry = PrefEntry(
                y_frame,
                pref_key=f"graph.general.y{i}_column",
                default_value="",
                width=8,
                on_change=self._on_setting_change,
            )
            y_entry.pack(side="top")
            self.y_entries.append(y_entry)

        self.options_frame = ttk.LabelFrame(
            self.frame, text=t("ui.graph_tab.options_frame")
        )
        self._create_options_widgets()

        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(
            column=0, row=4, columnspan=4, padx=10, pady=10, sticky="nsew"
        )

        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)

    def _create_options_widgets(self):
        global_frame = ttk.LabelFrame(
            self.options_frame, text=t("ui.graph_tab.global_settings")
        )
        global_frame.grid(column=0, row=0, columnspan=6, padx=5, pady=5, sticky="ew")

        self.group_label = ttk.Label(
            global_frame, text=t("ui.graph_tab.visualization_group_label")
        )
        self.group_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.group_combobox = PrefCombobox(
            global_frame,
            pref_key="graph.general.visualization_group",
            default_value="Time Series",
            state="readonly",
            values=["Time Series", "Stacked"],
            width=15,
            on_change=self._on_group_change,
        )
        self.group_combobox.grid(column=1, row=0, padx=5, pady=5, sticky="w")

        self.window_label = ttk.Label(global_frame, text=t("ui.graph_tab.window_label"))
        self.window_label.grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.data_window_entry = PrefEntry(
            global_frame,
            pref_key="graph.general.window_size",
            default_value="50",
            width=12,
            on_change=self._on_setting_change,
        )
        self.data_window_entry.grid(column=3, row=0, padx=5, pady=5, sticky="w")

        self.fps_label = ttk.Label(
            global_frame, text=t("ui.graph_tab.refresh_rate_label")
        )
        self.fps_label.grid(column=4, row=0, padx=5, pady=5, sticky="w")

        fps_frame = ttk.Frame(global_frame)
        fps_frame.grid(column=5, row=0, padx=5, pady=5, sticky="w")

        self.fps_combobox = PrefCombobox(
            fps_frame,
            pref_key="graph.general.refresh_rate",
            default_value="30",
            state="readonly",
            values=["1", "5", "10", "15", "20", "30"],
            width=5,
            on_change=self._on_fps_change,
        )
        self.fps_combobox.pack(side="left")

        self.fps_debug_label = ttk.Label(
            fps_frame, text="(33ms)", font=("TkDefaultFont", 8)
        )
        self.fps_debug_label.pack(side="left", padx=(5, 0))

        self.min_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.min_y_label"))
        self.min_y_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.min_y_entry = PrefEntry(
            global_frame,
            pref_key="graph.general.min_y",
            default_value="",
            width=12,
            on_change=self._on_setting_change,
        )
        self.min_y_entry.grid(column=1, row=1, padx=5, pady=5, sticky="w")

        self.max_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.max_y_label"))
        self.max_y_label.grid(column=2, row=1, padx=5, pady=5, sticky="w")
        self.max_y_entry = PrefEntry(
            global_frame,
            pref_key="graph.general.max_y",
            default_value="",
            width=12,
            on_change=self._on_setting_change,
        )
        self.max_y_entry.grid(column=3, row=1, padx=5, pady=5, sticky="w")

        colors_label = ttk.Label(global_frame, text=t("ui.graph_tab.color_label"))
        colors_label.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.y_color_combos = []
        default_colors = ["blue", "red", "green", "orange", "magenta"]

        colors_frame = ttk.Frame(global_frame)
        colors_frame.grid(column=1, row=2, columnspan=3, padx=5, pady=5, sticky="w")

        for i in range(5):
            y_frame = ttk.Frame(colors_frame)
            y_frame.grid(column=i, row=0, padx=2, pady=2)

            ttk.Label(y_frame, text=f"Y{i+1}").pack()
            color_combo = PrefCombobox(
                y_frame,
                pref_key=f"graph.general.y{i+1}_color",
                default_value=default_colors[i],
                state="readonly",
                values=self._get_translated_colors(),
                width=8,
                value_mapping=self._get_color_mapping(),
                on_change=lambda idx=i: self._on_color_setting_change(idx),
            )
            color_combo.pack()
            self.y_color_combos.append(color_combo)

        self.series_config_frame = ttk.LabelFrame(
            self.options_frame, text=t("ui.graph_tab.series_settings")
        )
        self.series_config_frame.grid(
            column=0, row=1, columnspan=6, padx=5, pady=5, sticky="ew"
        )

        self._create_series_widgets()

    def _create_series_row(self, parent, row, label, index):
        ttk.Label(parent, text=label).grid(column=0, row=row, padx=5, pady=2)

        type_combo = ttk.Combobox(
            parent,
            state="readonly",
            values=self._get_translated_graph_types(),
            width=10,
        )
        type_combo.grid(column=1, row=row, padx=5, pady=2)
        type_combo.set(t("ui.graph_types.line"))
        type_combo.bind(
            "<<ComboboxSelected>>",
            lambda e, idx=index: self._on_series_setting_change(idx),
        )

        color_combo = ttk.Combobox(
            parent, state="readonly", values=self._get_translated_colors(), width=10
        )
        color_combo.grid(column=2, row=row, padx=5, pady=2)

        default_colors = [
            t("ui.colors.blue"),
            t("ui.colors.red"),
            t("ui.colors.green"),
            t("ui.colors.orange"),
            t("ui.colors.magenta"),
            t("ui.colors.cyan"),
        ]
        color_combo.set(default_colors[index % len(default_colors)])
        color_combo.bind(
            "<<ComboboxSelected>>",
            lambda e, idx=index: self._on_series_setting_change(idx),
        )

        marker_combo = ttk.Combobox(
            parent, state="readonly", values=self._get_translated_markers(), width=10
        )
        marker_combo.grid(column=3, row=row, padx=5, pady=2)
        marker_combo.set(t("ui.markers.circle"))
        marker_combo.bind(
            "<<ComboboxSelected>>",
            lambda e, idx=index: self._on_series_setting_change(idx),
        )

        self.series_widgets.append(
            {"type": type_combo, "color": color_combo, "marker": marker_combo}
        )

    def _toggle_options(self):
        if self.options_visible:
            self.options_frame.grid_remove()
            self.options_button.config(text=t("ui.graph_tab.show_options"))
            self.options_visible = False
        else:
            self.options_frame.grid(
                column=0, row=2, columnspan=4, padx=10, pady=10, sticky="ew"
            )
            self.options_button.config(text=t("ui.graph_tab.hide_options"))
            self.options_visible = True

    def _on_series_setting_change(self, series_index):
        self._on_setting_change()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text=t("ui.graph_tab.resume"))
        else:
            self.pause_button.config(text=t("ui.graph_tab.pause"))

    def _save_chart(self):
        """Save the current chart as PNG by directly saving the existing figure"""
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title=t("ui.graph_tab.save_dialog_title"),
        )

        if file_path:
            try:
                self.graph_manager.figure.savefig(
                    file_path, dpi=300, bbox_inches="tight"
                )
                self.data_tab.add_message(
                    t("ui.graph_tab.graph_saved").format(path=file_path)
                )
            except Exception as e:
                self.data_tab.add_message(t("ui.data_tab.error_saving").format(error=e))

    def _on_setting_change(self, event=None):
        pass

    def plot_graph(self):
        try:
            if (
                not hasattr(self, "x_column_entry")
                or not self.x_column_entry.winfo_exists()
            ):
                return
            if (
                not hasattr(self, "data_window_entry")
                or not self.data_window_entry.winfo_exists()
            ):
                return
            if (
                not hasattr(self, "group_combobox")
                or not self.group_combobox.winfo_exists()
            ):
                return

            x_col = int(self.x_column_entry.get_value()) - 1

            if x_col < 0:
                raise ValueError(t("ui.graph_tab.positive_numbers"))

            data_lines = self.data_tab.get_data()
            if not data_lines:
                return

            data_window_str = self.data_window_entry.get_value()
            data_window = int(data_window_str) if data_window_str else 0
            if data_window > 0:
                data_lines = data_lines[-data_window:]

            x_data, _ = DataParser.extract_columns(data_lines, x_col, 0)
            if not x_data:
                self.data_tab.add_message(t("ui.graph_tab.could_not_extract_data"))
                return

            group = self.group_combobox.get_value()

            if group == "Stacked":
                self._plot_stacked_chart(x_data, data_lines, x_col)
            else:
                self._plot_time_series_chart(x_data, data_lines, x_col)

        except tk.TclError as e:
            pass
        except ValueError as e:
            self.data_tab.add_message(t("ui.graph_tab.parameter_error").format(error=e))
        except Exception as e:
            self.data_tab.add_message(t("ui.graph_tab.graph_error").format(error=e))

    def _plot_time_series_chart(self, x_data, data_lines, x_col):
        """Plot time series chart using preference widgets for value access."""
        y_series_data = []
        settings_list = []
        has_data = False

        for i, y_entry in enumerate(self.y_entries):
            y_col_str = y_entry.get_value().strip()
            if y_col_str:
                try:
                    y_col = int(y_col_str) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            y_series_data.append(y_data)
                            settings = self._get_series_settings(i)
                            settings["has_data"] = True
                            settings_list.append(settings)
                            has_data = True
                except ValueError:
                    pass

        if not has_data:
            return

        title = t("ui.graph_tab.chart_title")
        xlabel = t("ui.graph_tab.chart_xlabel").format(column=x_col + 1)
        ylabel = t("ui.graph_tab.chart_ylabel").format(column="Multi")

        if settings_list:
            min_y = self.min_y_entry.get_value().strip()
            max_y = self.max_y_entry.get_value().strip()
            settings_list[0]["min_y"] = min_y
            settings_list[0]["max_y"] = max_y

        self.graph_manager.plot_multi_series(
            x_data, y_series_data, settings_list, x_col, title, xlabel, ylabel
        )

    def _plot_stacked_chart(self, x_data, data_lines, x_col):
        y_series_data = []
        colors = []
        has_data = False

        for i, y_entry in enumerate(self.y_entries):
            y_col_str = y_entry.get_value().strip()
            if y_col_str:
                try:
                    y_col = int(y_col_str) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            y_series_data.append(y_data)

                            color = self._get_stacked_color(i)
                            colors.append(color)
                            has_data = True
                        else:
                            y_series_data.append([])
                            colors.append("#cccccc")
                    else:
                        y_series_data.append([])
                        colors.append("#cccccc")
                except ValueError:
                    y_series_data.append([])
                    colors.append("#cccccc")
            else:
                y_series_data.append([])
                colors.append("#cccccc")

        if not has_data:
            return

        normalize_100 = self.normalize_100_checkbox.get_value()

        title = t("ui.graph_tab.stacked_chart_title")
        xlabel = t("ui.graph_tab.chart_xlabel").format(column=x_col + 1)
        ylabel = (
            t("ui.graph_tab.stacked_chart_ylabel_percent")
            if normalize_100
            else t("ui.graph_tab.stacked_chart_ylabel")
        )

        self.graph_manager.plot_stacked_series(
            x_data, y_series_data, colors, normalize_100, title, xlabel, ylabel
        )

    def _get_series_settings(self, series_index):
        """Get series settings using preference widget API for type-safe value access."""
        color = self._get_stacked_color(series_index)

        if series_index < len(self.series_widgets):
            widgets = self.series_widgets[series_index]

            if "type" in widgets:
                type_value = widgets["type"].get_value()
                marker_value = widgets["marker"].get_value()

                return {
                    "type": type_value,
                    "color": color,
                    "marker": self._get_original_marker_from_internal(marker_value),
                }
            else:
                return {"type": "line", "color": color, "marker": "o"}

        return {"type": "line", "color": color, "marker": "o"}

    def update_graph_settings(self, settings):
        self.graph_settings.update(settings)

        if "type" in settings:
            self.graph_type_combobox.set(settings["type"])
        if "color" in settings:
            self.color_combobox.set(settings["color"])
        if "data_window" in settings:
            self.data_window_entry.delete(0, "end")
            self.data_window_entry.insert(0, str(settings["data_window"]))
        if "min_y" in settings:
            self.min_y_entry.delete(0, "end")
            self.min_y_entry.insert(0, settings["min_y"])
        if "max_y" in settings:
            self.max_y_entry.delete(0, "end")
            self.max_y_entry.insert(0, settings["max_y"])
        if "dot_type" in settings:
            translated_marker = self._get_translated_marker_from_original(
                settings["dot_type"]
            )
            self.dot_type_combobox.set(translated_marker)

        if self.data_tab.get_data() and not self.is_paused:
            self.plot_graph()

    def _get_translated_graph_types(self):
        """Get translated graph type labels."""
        return [t("ui.graph_types.line"), t("ui.graph_types.scatter")]

    def _get_graph_type_mapping(self):
        """Get mapping from translated labels to internal values."""
        return {
            t("ui.graph_types.line"): "line",
            t("ui.graph_types.scatter"): "scatter",
        }

    def _get_translated_colors(self):
        """Get translated color labels."""
        color_keys = [
            "blue",
            "cyan",
            "teal",
            "green",
            "lime",
            "yellow",
            "amber",
            "orange",
            "red",
            "magenta",
            "indigo",
            "violet",
            "turquoise",
            "aquamarine",
            "springgreen",
            "chartreuse",
            "gold",
            "coral",
            "crimson",
            "pink",
        ]
        return [t(f"ui.colors.{color}") for color in color_keys]

    def _get_color_mapping(self):
        """Get mapping from translated color labels to internal values."""
        color_keys = [
            "blue",
            "cyan",
            "teal",
            "green",
            "lime",
            "yellow",
            "amber",
            "orange",
            "red",
            "magenta",
            "indigo",
            "violet",
            "turquoise",
            "aquamarine",
            "springgreen",
            "chartreuse",
            "gold",
            "coral",
            "crimson",
            "pink",
        ]
        return {t(f"ui.colors.{color}"): color for color in color_keys}

    def _get_translated_markers(self):
        """Get translated marker labels."""
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

    def _get_marker_mapping(self):
        """Get mapping from translated marker labels to internal values."""
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
        return {t(f"ui.markers.{marker}"): marker for marker in marker_keys}

    def _get_original_marker_from_internal(self, internal_marker):
        """Convert internal marker name to matplotlib marker symbol."""
        marker_mapping = {
            "circle": "o",
            "square": "s",
            "triangle": "^",
            "diamond": "D",
            "star": "*",
            "plus": "+",
            "x": "x",
            "vline": "|",
            "hline": "_",
            "hexagon": "h",
        }
        return marker_mapping.get(internal_marker, "o")

    def _get_original_marker(self, translated_marker):
        """Convert translated marker to matplotlib marker symbol."""
        marker_mapping = {
            t("ui.markers.circle"): "o",
            t("ui.markers.square"): "s",
            t("ui.markers.triangle"): "^",
            t("ui.markers.diamond"): "D",
            t("ui.markers.star"): "*",
            t("ui.markers.plus"): "+",
            t("ui.markers.x"): "x",
            t("ui.markers.vline"): "|",
            t("ui.markers.hline"): "_",
            t("ui.markers.hexagon"): "h",
        }
        return marker_mapping.get(translated_marker, "o")

    def _get_translated_marker_from_original(self, original_marker):
        """Convert matplotlib marker to translated marker text"""
        for key, value in MARKER_MAPPING.items():
            if value == original_marker:
                return t(f"ui.markers.{key}")
        return t("ui.markers.circle")

    def _get_original_graph_type(self, translated_type):
        type_mapping = {
            t("ui.graph_types.line"): "line",
            t("ui.graph_types.scatter"): "scatter",
        }
        return type_mapping.get(translated_type, "line")

    def _get_original_color_from_internal(self, internal_color):
        """Convert internal color name to hex color."""
        color_mapping = {
            "blue": "#1f77b4",
            "cyan": "#17becf",
            "teal": "#008080",
            "green": "#2ca02c",
            "lime": "#32cd32",
            "yellow": "#ffff00",
            "amber": "#ffc000",
            "orange": "#ff7f0e",
            "red": "#d62728",
            "magenta": "#ff00ff",
            "indigo": "#4b0082",
            "violet": "#9467bd",
            "turquoise": "#40e0d0",
            "aquamarine": "#7fffd4",
            "springgreen": "#00ff7f",
            "chartreuse": "#7fff00",
            "gold": "#ffd700",
            "coral": "#ff7f50",
            "crimson": "#dc143c",
            "pink": "#ffc0cb",
        }
        return color_mapping.get(internal_color, "#1f77b4")

    def _get_original_color(self, translated_color):
        color_mapping = {
            t("ui.colors.blue"): "#1f77b4",
            t("ui.colors.cyan"): "#17becf",
            t("ui.colors.teal"): "#008080",
            t("ui.colors.green"): "#2ca02c",
            t("ui.colors.lime"): "#32cd32",
            t("ui.colors.yellow"): "#ffff00",
            t("ui.colors.amber"): "#ffc000",
            t("ui.colors.orange"): "#ff7f0e",
            t("ui.colors.red"): "#d62728",
            t("ui.colors.magenta"): "#ff00ff",
            t("ui.colors.indigo"): "#4b0082",
            t("ui.colors.violet"): "#9467bd",
            t("ui.colors.turquoise"): "#40e0d0",
            t("ui.colors.aquamarine"): "#7fffd4",
            t("ui.colors.springgreen"): "#00ff7f",
            t("ui.colors.chartreuse"): "#7fff00",
            t("ui.colors.gold"): "#ffd700",
            t("ui.colors.coral"): "#ff7f50",
            t("ui.colors.crimson"): "#dc143c",
            t("ui.colors.pink"): "#ffc0cb",
        }
        return color_mapping.get(translated_color, "#1f77b4")

    def _on_group_change(self, event=None):
        """Called when the visualization group changes. Preferences are automatically saved."""
        self._create_series_widgets()
        self._on_setting_change()

    def _create_series_widgets(self):
        for widget in self.series_config_frame.winfo_children():
            widget.destroy()

        group = self.group_combobox.get_value()

        if group == "Time Series":
            self._create_time_series_widgets()
        elif group == "Stacked":
            self._create_stacked_widgets()

    def _create_time_series_widgets(self):
        self.series_config_frame.config(text=t("ui.graph_tab.time_series_settings"))

        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.series_label")).grid(
            column=0, row=0, padx=5, pady=5
        )
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.type_label")).grid(
            column=1, row=0, padx=5, pady=5
        )
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.point_label")).grid(
            column=2, row=0, padx=5, pady=5
        )

        self.series_widgets = []
        for i in range(1, 6):
            self._create_time_series_row(self.series_config_frame, i, f"Y{i}", i - 1)

    def _create_time_series_row(self, parent, row, label, index):
        """Create a time series configuration row using preference widgets."""
        ttk.Label(parent, text=label).grid(column=0, row=row, padx=5, pady=2)

        type_combo = PrefCombobox(
            parent,
            pref_key=f"graph.time_series.y{index+1}_type",
            default_value="line",
            state="readonly",
            values=self._get_translated_graph_types(),
            width=10,
            value_mapping=self._get_graph_type_mapping(),
            on_change=lambda idx=index: self._on_series_setting_change(idx),
        )
        type_combo.grid(column=1, row=row, padx=5, pady=2)

        marker_combo = PrefCombobox(
            parent,
            pref_key=f"graph.time_series.y{index+1}_marker",
            default_value="circle",
            state="readonly",
            values=self._get_translated_markers(),
            width=10,
            value_mapping=self._get_marker_mapping(),
            on_change=lambda idx=index: self._on_series_setting_change(idx),
        )
        marker_combo.grid(column=2, row=row, padx=5, pady=2)

        self.series_widgets.append({"type": type_combo, "marker": marker_combo})

    def _create_stacked_widgets(self):
        self.series_config_frame.config(text=t("ui.graph_tab.stacked_settings"))

        self.normalize_100_checkbox = PrefCheckbutton(
            self.series_config_frame,
            pref_key="graph.group.stacked.normalize_100",
            default_value=False,
            text=t("ui.graph_tab.normalize_100_percent"),
            on_change=self._on_setting_change,
        )
        self.normalize_100_checkbox.grid(column=0, row=0, columnspan=4, padx=5, pady=10)

        self.series_widgets = []

    def _get_stacked_color(self, series_index):
        """Get color for stacked chart series using preference widget API."""
        if series_index < len(self.y_color_combos):
            internal_color = self.y_color_combos[series_index].get_value()
            return self._get_original_color_from_internal(internal_color)

        default_colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#ff00ff"]
        return default_colors[series_index % len(default_colors)]

    def get_frame(self):
        return self.frame

    def _on_color_setting_change(self, color_index):
        """Called when a color setting changes. Preferences are automatically saved."""

        self._on_setting_change()

    def _start_refresh_timer(self):
        self._refresh_chart()

    def _refresh_chart(self):
        try:
            if not self.is_paused:
                data_lines = self.data_tab.get_data()
                if data_lines:
                    if self.debug_refresh:
                        self.refresh_counter += 1
                        fps_actual = 1000 / self.refresh_rate_ms
                        print(
                            f"Chart refresh #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Fixed Rate"
                        )

                    self.plot_graph()
                else:
                    pass
            else:
                pass

        except Exception as e:
            if self.debug_refresh:
                print(f"Chart refresh error: {e}")
        finally:
            if hasattr(self, "frame") and self.frame.winfo_exists():
                self.refresh_timer_id = self.frame.after(
                    self.refresh_rate_ms, self._refresh_chart
                )

    def _stop_refresh_timer(self):
        if self.refresh_timer_id:
            try:
                self.frame.after_cancel(self.refresh_timer_id)
            except:
                pass
            self.refresh_timer_id = None

    def _set_refresh_rate(self, fps):
        self.refresh_rate_ms = int(1000 / fps)

    def cleanup(self):
        self._stop_refresh_timer()

    def __del__(self):
        try:
            self.cleanup()
        except:
            pass

    def _on_fps_change(self, event=None):
        """Called when FPS setting changes. Preferences are automatically saved."""
        try:
            fps = int(self.fps_combobox.get_value())
            self._set_refresh_rate(fps)

            self.fps_debug_label.config(text=f"({self.refresh_rate_ms}ms)")

            import time

            self.last_render_time = time.time()
            self.refresh_counter = 0

        except ValueError:
            pass

    def set_tab_active(self, is_active):
        """Set whether this tab is currently active (optimization for rendering)."""
        self.is_tab_active = is_active
        if not is_active:
            # Stop expensive operations when tab is not visible
            self._stop_refresh_timer()
        else:
            # Resume operations when tab becomes active
            if hasattr(self, 'frame') and self.frame.winfo_exists():
                self._start_refresh_timer()

    def should_render_now(self, current_time):
        if self.is_paused or not getattr(self, 'is_tab_active', True):
            return False

        refresh_interval = self.refresh_rate_ms / 1000.0

        return (current_time - self.last_render_time) >= refresh_interval

    def render_frame(self):
        import time

        try:
            data_lines = self.data_tab.get_data()
            if data_lines:
                self.refresh_counter += 1

                if self.debug_refresh:
                    fps_actual = 1000 / self.refresh_rate_ms
                    print(
                        f"Render frame #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Game Loop Style"
                    )

                self.plot_graph()

            self.last_render_time = time.time()

        except Exception as e:
            if self.debug_refresh:
                print(f"Render frame error: {e}")

            self.last_render_time = time.time()

    def _on_normalize_change(self):
        """Handle immediate change when normalization checkbox is clicked"""
        try:
            self._save_stacked_preferences()

            self._on_setting_change()
        except Exception as e:
            print(f"Note: Could not save normalization preference: {e}")
