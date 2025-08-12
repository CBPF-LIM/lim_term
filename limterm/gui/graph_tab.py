from ..utils.ui_builder import build_from_layout_name, ask_save_as
from ..core import GraphManager
from ..utils import DataParser, FileManager
from ..config import DEFAULT_X_COLUMN
from ..i18n import t, get_config_manager
from .preference_widgets import PrefEntry, PrefCombobox, PrefCheckbutton
from ..utils import (
    get_translated_graph_types,
    get_graph_type_mapping,
    get_translated_colors,
    get_color_mapping,
    get_translated_markers,
    get_marker_mapping,
    get_original_marker_from_internal,
    get_default_series_hex_colors,
    widget_exists,
    safe_after,
    safe_after_cancel,
)
import time


class GraphTab:
    def __init__(self, parent, data_tab, open_options_callback):

        self.frame = build_from_layout_name(parent, "graph_tab", self)
        self.data_tab = data_tab
        self.config_manager = get_config_manager()
        self.graph_settings = {}
        self.options_visible = False
        self.is_paused = False

        self.refresh_rate_ms = 33
        self.refresh_timer_id = None
        self.refresh_counter = 0
        self.debug_refresh = False
        self.last_render_time = 0
        self.series_widgets = []

        self.y_entries = []
        for i in range(1, 6):
            entry = getattr(self, f"y{i}_entry", None)
            if entry is not None:
                self.y_entries.append(entry)

        self.y_color_combos = []
        for i in range(1, 6):
            combo = getattr(self, f"y{i}_color", None)
            if combo is not None:
                self.y_color_combos.append(combo)

        self.options_visible = self.config_manager.load_setting(
            "graph.ui.options_visible", False
        )
        if not self.options_visible and hasattr(self, "graph_settings_frame"):
            self.graph_settings_frame.grid_remove()
            if hasattr(self, "options_button"):
                self.options_button.config(text=t("ui.graph_tab.show_settings"))
        else:
            if hasattr(self, "options_button"):
                self.options_button.config(text=t("ui.graph_tab.hide_settings"))

        if hasattr(self, "series_config_frame"):
            self._create_series_widgets()

        self._create_chart_area()

        try:
            self.frame.rowconfigure(3, weight=1)
            self.frame.columnconfigure(0, weight=1)
        except Exception:
            pass

    def get_frame(self):
        return self.frame

    def _create_chart_area(self):

        chart_parent = getattr(self, "chart_frame", None)
        if not chart_parent or not widget_exists(chart_parent):

            return

        self.graph_manager = GraphManager(chart_parent)
        self.graph_manager.get_widget().pack(fill="both", expand=True)

    def _create_series_widgets(self):
        group = self.group_combobox.get_value()

        for child in self.series_config_frame.winfo_children():
            child.destroy()
        self.series_widgets = []

        if group == "time_series":
            self.series_config_frame.config(text=t("ui.graph_tab.time_series_settings"))
            for i in range(1, 6):
                self._create_time_series_row(
                    self.series_config_frame, i, f"Y{i}", i - 1
                )
        elif group == "stacked":
            self.series_config_frame.config(text=t("ui.graph_tab.stacked_settings"))

            # Build normalize to 100% checkbox via builder (YAML/dict spec)
            try:
                from ..utils.ui_builder import build_from_spec

                spec = {
                    "widget": "PrefCheckbutton",
                    "name": "normalize_100_checkbox",
                    "options": {
                        "pref_key": "graph.general.normalize_100",
                        "default_value": False,
                        "text": "${ui.graph_tab.normalize_100_percent}",
                        "on_change": "_on_setting_change",
                    },
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 0,
                        "columnspan": 4,
                        "padx": 5,
                        "pady": 10,
                        "sticky": "w",
                    },
                }
                build_from_spec(self.series_config_frame, spec, self)
            except Exception:
                pass

    def _create_time_series_row(self, parent, row, label, index):

        try:
            ctx = type("_RowCtx", (), {})()
            setattr(
                ctx,
                "_on_series_change",
                (lambda idx=index: (lambda: self._on_series_setting_change(idx)))(),
            )

            setattr(ctx, "row_index", row)
            row_widget = build_from_layout_name(parent, "graph_time_series_row", ctx)
            # Ensure proper layout since YAML variable rows may not be supported
            try:
                row_widget.grid(column=0, row=index, columnspan=4, sticky="w", padx=5, pady=2)
            except Exception:
                pass
            if hasattr(ctx, "type_combo") and hasattr(ctx, "marker_combo"):
                self.series_widgets.append(
                    {"type": ctx.type_combo, "marker": ctx.marker_combo}
                )
            return
        except Exception:
            pass

        return

    def _on_group_change(self, event=None):
        self._create_series_widgets()
        self._on_setting_change()

    def _get_stacked_color(self, series_index):
        if series_index < len(self.y_color_combos):
            internal_color = self.y_color_combos[series_index].get_value()

            return internal_color
        defaults = get_default_series_hex_colors()
        return defaults[series_index % len(defaults)]

    def _toggle_options(self):
        if self.options_visible:
            self.graph_settings_frame.grid_remove()
            self.options_button.config(text=t("ui.graph_tab.show_settings"))
            self.options_visible = False
        else:
            self.graph_settings_frame.grid(
                column=0, row=1, columnspan=4, padx=10, pady=5, sticky="ew"
            )
            self.options_button.config(text=t("ui.graph_tab.hide_settings"))
            self.options_visible = True

    def _on_series_setting_change(self, series_index):
        self._on_setting_change()

    def _on_color_setting_change(self, color_index):
        self._on_setting_change()

    def _toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text=t("ui.graph_tab.resume"))
        else:
            self.pause_button.config(text=t("ui.graph_tab.pause"))

    def _save_chart(self):
        file_path = ask_save_as(
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

    def _save_data(self):
        valid_lines = [
            item["value"] for item in self.data_tab.data if item["type"] == "data"
        ]
        if valid_lines:
            file_path = FileManager.save_data_to_file(valid_lines)
            if file_path:
                self.data_tab.add_message(
                    t("ui.data_tab.data_saved").format(path=file_path)
                )

    def _on_setting_change(self, event=None):
        pass

    def plot_graph(self):
        if not (hasattr(self, "x_column_entry") and widget_exists(self.x_column_entry)):
            return
        if not (
            hasattr(self, "data_window_entry") and widget_exists(self.data_window_entry)
        ):
            return
        if not (hasattr(self, "group_combobox") and widget_exists(self.group_combobox)):
            return

        try:
            x_col = int(self.x_column_entry.get_value()) - 1
        except ValueError as e:
            self.data_tab.add_message(
                t("ui.graph_tab.parameter_error").format(error=str(e))
            )
            return

        if x_col < 0:
            self.data_tab.add_message(
                t("ui.graph_tab.parameter_error").format(
                    error=t("ui.graph_tab.positive_numbers")
                )
            )
            return

        data_lines = self.data_tab.get_data()
        if not data_lines:
            return

        data_window_str = self.data_window_entry.get_value()
        try:
            data_window = int(data_window_str) if data_window_str else 0
        except ValueError:
            data_window = 0
        if data_window > 0:
            data_lines = data_lines[-data_window:]

        x_data, _ = DataParser.extract_columns(data_lines, x_col, 0)
        if not x_data:
            self.data_tab.add_message(t("ui.graph_tab.could_not_extract_data"))
            return

        group = self.group_combobox.get_value()

        if group == "stacked":
            self._plot_stacked_chart(x_data, data_lines, x_col)
        else:
            self._plot_time_series_chart(x_data, data_lines, x_col)

    def _plot_time_series_chart(self, x_data, data_lines, x_col):
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

        normalize_100 = getattr(self, "normalize_100_checkbox", None)
        normalize_100 = normalize_100.get_value() if normalize_100 else False

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
        color = self._get_stacked_color(series_index)

        if series_index < len(self.series_widgets):
            widgets = self.series_widgets[series_index]

            if "type" in widgets:
                type_value = widgets["type"].get_value()
                marker_value = (
                    widgets.get("marker").get_value()
                    if widgets.get("marker")
                    else "circle"
                )

                return {
                    "type": type_value,
                    "color": color,
                    "marker": get_original_marker_from_internal(marker_value),
                }
            else:
                return {"type": "line", "color": color, "marker": "o"}

        return {"type": "line", "color": color, "marker": "o"}

    def update_graph_settings(self, settings):
        self.graph_settings.update(settings)

        if "data_window" in settings and hasattr(self, "data_window_entry"):
            self.data_window_entry.delete(0, "end")
            self.data_window_entry.insert(0, str(settings["data_window"]))
        if "min_y" in settings and hasattr(self, "min_y_entry"):
            self.min_y_entry.delete(0, "end")
            self.min_y_entry.insert(0, settings["min_y"])
        if "max_y" in settings and hasattr(self, "max_y_entry"):
            self.max_y_entry.delete(0, "end")
            self.max_y_entry.insert(0, settings["max_y"])

        if self.data_tab.get_data() and not self.is_paused:
            self.plot_graph()

    def _start_refresh_timer(self):
        self._refresh_chart()

    def _refresh_chart(self):
        if not self.is_paused:
            data_lines = self.data_tab.get_data()
            if data_lines:
                if self.debug_refresh:
                    self.refresh_counter += 1
                    fps_actual = 1000 / self.refresh_rate_ms
                    print(
                        f"Chart refresh #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Fixed Rate"
                    )
                try:
                    self.plot_graph()
                except Exception as e:
                    if self.debug_refresh:
                        print(f"Chart refresh error: {e}")
        self.refresh_timer_id = safe_after(
            self.frame, self.refresh_rate_ms, self._refresh_chart
        )

    def _stop_refresh_timer(self):
        if self.refresh_timer_id:
            safe_after_cancel(self.frame, self.refresh_timer_id)
        self.refresh_timer_id = None

    def _set_refresh_rate(self, fps: float):
        if fps and fps > 0:
            self.refresh_rate_ms = int(1000 / fps)

    def cleanup(self):
        self._stop_refresh_timer()

    def __del__(self):
        try:
            self.cleanup()
        except Exception:
            pass

    def _on_fps_change(self, event=None):
        value = self.fps_combobox.get_value()
        try:
            fps = float(value)
        except ValueError:
            return
        self._set_refresh_rate(fps)
        self.fps_debug_label.config(text=f"({int(fps)} Hz = {self.refresh_rate_ms}ms)")
        self.last_render_time = time.time()
        self.refresh_counter = 0

    def set_tab_active(self, is_active):
        self.is_tab_active = is_active
        if not is_active:
            self._stop_refresh_timer()
        else:
            if widget_exists(self.frame):
                self._start_refresh_timer()

    def should_render_now(self, current_time):
        if self.is_paused or not getattr(self, "is_tab_active", True):
            return False
        refresh_interval = self.refresh_rate_ms / 1000.0
        return (current_time - self.last_render_time) >= refresh_interval

    def render_frame(self):
        data_lines = self.data_tab.get_data()
        if data_lines:
            self.refresh_counter += 1
            if self.debug_refresh:
                fps_actual = 1000 / self.refresh_rate_ms
                print(
                    f"Render frame #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Game Loop Style"
                )
            try:
                self.plot_graph()
            except Exception as e:
                if self.debug_refresh:
                    print(f"Render frame error: {e}")
        self.last_render_time = time.time()
