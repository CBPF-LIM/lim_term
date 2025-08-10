import tkinter as tk
from tkinter import ttk
import time
import os
import logging
from ..core import GraphManager
from ..i18n import t, get_config_manager
from .preference_widgets import PrefEntry, PrefCombobox
from ..utils import widget_exists, safe_after, safe_after_cancel
from ..utils.ui_builder import build_from_yaml

logger = logging.getLogger(__name__)


class OscTab:

    def __init__(self, parent, data_tab):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.config_manager = get_config_manager()

        self.is_armed = False
        self.trigger_sets = []
        self.max_sets = 4

        self.update_interval_ms = 33
        self.update_timer_id = None

        self.most_recent_trigger_idx = None
        self.current_values = []

        self._create_widgets()
        self._start_update_loop()

    def _create_widgets(self):
        import os as _os

        yaml_path = _os.path.join(
            _os.path.dirname(__file__), "..", "ui", "layouts", "osc_tab.yml"
        )
        yaml_path = _os.path.abspath(yaml_path)

        build_from_yaml(self.frame, yaml_path, self)

        self.settings_visible = self.config_manager.load_setting(
            "osc.ui.settings_visible", False
        )

        if not self.settings_visible and hasattr(self, "settings_frame"):
            self.settings_frame.grid_remove()
            if hasattr(self, "settings_button"):
                self.settings_button.config(text=t("ui.osc_tab.show_settings"))
        else:
            if hasattr(self, "settings_button"):
                self.settings_button.config(text=t("ui.osc_tab.hide_settings"))

        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(
            column=0, row=2, padx=10, pady=10, sticky="nsew"
        )

        self.frame.rowconfigure(2, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def _toggle_settings(self):
        if self.settings_visible:
            self.settings_frame.grid_remove()
            self.settings_button.config(text=t("ui.osc_tab.show_settings"))
            self.settings_visible = False
        else:
            self.settings_frame.grid()
            self.settings_button.config(text=t("ui.osc_tab.hide_settings"))
            self.settings_visible = True

        self.config_manager.save_setting(
            "osc.ui.settings_visible", self.settings_visible
        )

    def _start_update_loop(self):
        if not widget_exists(self.frame):
            return
        if self.is_armed:
            self._process_data_directly()
            self._plot_sets()
        self.update_timer_id = safe_after(
            self.frame, self.update_interval_ms, self._start_update_loop
        )

    def _process_data_directly(self):
        try:

            data_lines = self.data_tab.get_data()
            if not data_lines or len(data_lines) < 10:
                return

            try:
                column = int(self.trigger_source.get_value())
                trigger_level = float(self.trigger_level.get_value())
                window_size = int(self.window_size.get_value())
                trigger_edge = self.trigger_edge.get_value()
            except (ValueError, AttributeError):
                return

            values = []
            for line in reversed(data_lines[-200:]):
                try:
                    parts = line.strip().split()
                    if len(parts) > column:
                        value = float(parts[column])
                        values.append(value)
                except (ValueError, IndexError):
                    continue

            if len(values) < window_size + 5:
                return

            values.reverse()

            complete_sets = []
            most_recent_trigger_idx = None

            i = 1
            while i < len(values) - 1:

                triggered = False
                if (
                    trigger_edge == "rising"
                    and values[i - 1] <= trigger_level < values[i]
                ):
                    triggered = True
                elif (
                    trigger_edge == "falling"
                    and values[i - 1] >= trigger_level > values[i]
                ):
                    triggered = True
                elif trigger_edge == "both" and (
                    (values[i - 1] <= trigger_level < values[i])
                    or (values[i - 1] >= trigger_level > values[i])
                ):
                    triggered = True

                if triggered:
                    most_recent_trigger_idx = i

                    if i + window_size <= len(values):

                        window_data = values[i : i + window_size]
                        complete_sets.append(window_data)
                        i += window_size // 2
                    else:

                        break
                else:
                    i += 1

            if complete_sets:
                self.trigger_sets.extend(complete_sets)

                if len(self.trigger_sets) > self.max_sets - 1:
                    self.trigger_sets = self.trigger_sets[-(self.max_sets - 1) :]

            self.most_recent_trigger_idx = most_recent_trigger_idx
            self.current_values = values

        except Exception as e:
            logger.error(f"Error in direct data processing: {e}")

    def _plot_sets(self):
        try:
            self.graph_manager.clear()

            for window_data in self.trigger_sets:
                x_data = list(range(len(window_data)))
                self.graph_manager.plot_line(x_data, window_data, color="blue")

            if hasattr(self, "most_recent_trigger_idx") and hasattr(
                self, "current_values"
            ):
                if self.most_recent_trigger_idx is not None and self.current_values:

                    incomplete_data = self.current_values[
                        self.most_recent_trigger_idx :
                    ]

                    try:
                        window_size = int(self.window_size.get_value())
                        if len(incomplete_data) > window_size:
                            incomplete_data = incomplete_data[:window_size]
                    except (ValueError, AttributeError):
                        pass

                    if len(incomplete_data) > 1:
                        x_data = list(range(len(incomplete_data)))

                        self.graph_manager.plot_line(
                            x_data, incomplete_data, color="#1760ff"
                        )

            if self.trigger_sets or (
                hasattr(self, "most_recent_trigger_idx")
                and self.most_recent_trigger_idx
            ):
                trigger_level = float(self.trigger_level.get_value())

                all_lengths = [len(data) for data in self.trigger_sets]
                if (
                    hasattr(self, "current_values")
                    and hasattr(self, "most_recent_trigger_idx")
                    and self.most_recent_trigger_idx
                ):
                    incomplete_len = (
                        len(self.current_values) - self.most_recent_trigger_idx
                    )

                    try:
                        window_size = int(self.window_size.get_value())
                        incomplete_len = min(incomplete_len, window_size)
                    except (ValueError, AttributeError):
                        pass

                    if incomplete_len > 0:
                        all_lengths.append(incomplete_len)

                if all_lengths:
                    max_length = max(all_lengths)
                    if max_length > 0:
                        trigger_x = [0, max_length - 1]
                        trigger_y = [trigger_level, trigger_level]
                        self.graph_manager.plot_line(trigger_x, trigger_y, color="red")

            self.graph_manager.set_labels(
                title=t("ui.osc_tab.oscilloscope_capture_title"),
                xlabel=t("ui.osc_tab.samples_label"),
                ylabel=t("ui.osc_tab.value_label"),
            )

            self.graph_manager.update()

        except Exception as e:
            logger.error(f"Error plotting sets: {e}")

    def _stop_update_loop(self):
        if self.update_timer_id:
            safe_after_cancel(self.frame, self.update_timer_id)
            self.update_timer_id = None

    def _is_widget_valid(self, widget_name):
        return hasattr(self, widget_name) and widget_exists(getattr(self, widget_name))

    def _is_frame_valid(self):
        return hasattr(self, "frame") and widget_exists(self.frame)

    def set_tab_active(self, is_active):
        self.is_active = is_active
        if not is_active:
            self._stop_update_loop()
        elif self._is_frame_valid():
            self._start_update_loop()

    def _clear_display(self):
        try:
            self.trigger_sets.clear()
            self.most_recent_trigger_idx = None
            self.current_values = []
            if hasattr(self, "graph_manager"):
                self.graph_manager.clear()
                self.graph_manager.update()
        except Exception as e:
            logger.error(f"Clear display error: {e}")

    def _save_png(self):
        if not self.trigger_sets or not hasattr(self, "graph_manager"):
            return

        try:
            capture_dir = "osc_captures"
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(capture_dir, f"osc_capture_{timestamp}.png")

            self.graph_manager.figure.savefig(
                image_filename, dpi=300, bbox_inches="tight"
            )

            self.data_tab.add_message(
                t("ui.osc_tab.png_saved", filename=f"osc_capture_{timestamp}.png")
            )

        except Exception as e:
            logger.error(f"Save PNG error: {e}")
            self.data_tab.add_message(t("ui.osc_tab.save_error", error=str(e)))

    def _save_data(self):
        if not self.trigger_sets:
            return

        try:
            capture_dir = "osc_captures"
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            data_filename = os.path.join(capture_dir, f"osc_capture_{timestamp}.txt")

            with open(data_filename, "w", encoding="utf-8") as f:
                for i, trigger_set in enumerate(self.trigger_sets):
                    f.write(f"# Trigger Set {i+1}\n")
                    for j, value in enumerate(trigger_set):
                        f.write(f"{j}\t{value}\n")
                    f.write("\n")

            self.data_tab.add_message(
                t("ui.osc_tab.data_saved", filename=f"osc_capture_{timestamp}.txt")
            )

        except Exception as e:
            logger.error(f"Save data error: {e}")
            self.data_tab.add_message(t("ui.osc_tab.save_error", error=str(e)))

    def _toggle_arm(self):
        if self.is_armed:
            self._disarm()
        else:
            self._arm()

    def _arm(self):
        if not self._is_frame_valid():
            return

        self.is_armed = True

        trigger_mode = self.trigger_mode.get_value()
        if trigger_mode == "single":
            self.graph_manager.clear()
            self.trigger_sets.clear()
            self.most_recent_trigger_idx = None
            self.current_values = []

        if self._is_widget_valid("arm_button"):
            self.arm_button.config(text=t("ui.osc_tab.disarm"))
        if self._is_widget_valid("status_label"):
            self.status_label.config(text=t("ui.osc_tab.armed"), foreground="orange")

    def _disarm(self):
        self.is_armed = False

        if self._is_widget_valid("arm_button"):
            self.arm_button.config(text=t("ui.osc_tab.arm"))
        if self._is_widget_valid("status_label"):
            self.status_label.config(text=t("ui.osc_tab.ready"), foreground="blue")

    def get_frame(self):
        return self.frame

    def cleanup(self):
        self._stop_update_loop()
        self.is_armed = False

        if hasattr(self, "trigger_sets"):
            self.trigger_sets.clear()
