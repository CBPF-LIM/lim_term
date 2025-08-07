"""
Oscilloscope-inspired data capture and visualization tab.

This module provides oscilloscope functionality including:
- Trigger detection with configurable level and edge detection
- One-shot capture mode with pre-trigger data
- Auto-save of captured data and screenshots
- Real-time status monitoring
"""

import tkinter as tk
from tkinter import ttk
import time
import os
import logging
from ..core import GraphManager
from ..i18n import t, get_config_manager
from .preference_widgets import PrefEntry, PrefCombobox

logger = logging.getLogger(__name__)


class OscTab:
    """Oscilloscope-inspired data capture and visualization tab."""

    def __init__(self, parent, data_tab):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.config_manager = get_config_manager()

        self.is_armed = False
        self.trigger_data = []
        self.trigger_sets = []  # Store multiple trigger sets for gradient display
        self.max_sets = 10  # Maximum number of sets to keep
        self.capture_start_time = None
        self.capture_count = 0
        self.last_trigger_time = 0  # Add cooldown tracking

        self.osc_refresh_rate_ms = 33
        self.refresh_timer_id = None
        self.pending_callbacks = []
        self.is_tab_active = False

        self._create_widgets()
        self._setup_trigger_monitoring()

    def _create_widgets(self):
        """Create the oscilloscope interface."""
        main_controls_frame = ttk.Frame(self.frame)
        main_controls_frame.grid(column=0, row=0, padx=10, pady=5, sticky="ew")

        arm_frame = ttk.LabelFrame(
            main_controls_frame, text=t("ui.osc_tab.oscilloscope_controls")
        )
        arm_frame.grid(column=0, row=0, padx=5, pady=5, sticky="ew")

        self.arm_button = ttk.Button(
            arm_frame, text=t("ui.osc_tab.arm"), command=self._toggle_arm
        )
        self.arm_button.pack(pady=5, fill="x")

        self.settings_button = ttk.Button(
            arm_frame, text=t("ui.osc_tab.show_settings"), command=self._toggle_settings
        )
        self.settings_button.pack(pady=2, fill="x")

        status_frame = ttk.LabelFrame(main_controls_frame, text=t("ui.osc_tab.status"))
        status_frame.grid(column=1, row=0, padx=5, pady=5, sticky="nsew")

        self.status_label = ttk.Label(
            status_frame, text=t("ui.osc_tab.ready"), foreground="blue"
        )
        self.status_label.pack(pady=5)

        self.freq_label = ttk.Label(
            status_frame,
            text=t("ui.osc_tab.frequency_unknown"),
            font=("TkDefaultFont", 8),
        )
        self.freq_label.pack()

        self.settings_frame = ttk.LabelFrame(
            main_controls_frame, text=t("ui.osc_tab.oscilloscope_settings")
        )
        self.settings_frame.grid(column=2, row=0, padx=5, pady=5, sticky="ew")

        self.settings_visible = self.config_manager.load_setting(
            "osc.ui.settings_visible", True
        )

        self._create_settings_widgets()

        if not self.settings_visible:
            self.settings_frame.grid_remove()
            self.settings_button.config(text=t("ui.osc_tab.show_settings"))

        main_controls_frame.columnconfigure(0, weight=0)
        main_controls_frame.columnconfigure(1, weight=0)
        main_controls_frame.columnconfigure(2, weight=1)

        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(
            column=0, row=1, columnspan=4, padx=10, pady=10, sticky="nsew"
        )

        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def _create_settings_widgets(self):
        """Create the settings widgets inside the collapsible frame."""
        settings_container = ttk.Frame(self.settings_frame)
        settings_container.pack(fill="both", expand=True, padx=5, pady=5)

        trigger_frame = ttk.LabelFrame(settings_container, text=t("ui.osc_tab.trigger"))
        trigger_frame.grid(column=0, row=0, padx=5, pady=5, sticky="ew")

        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_source")).grid(
            column=0, row=0, padx=5, pady=2, sticky="w"
        )
        self.trigger_source = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.source_column",
            default_value="2",
            width=8,
            on_change=self._on_trigger_setting_change,
        )
        self.trigger_source.grid(column=1, row=0, padx=5, pady=2)

        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_level")).grid(
            column=0, row=1, padx=5, pady=2, sticky="w"
        )
        self.trigger_level = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.level",
            default_value="0.0",
            width=8,
            on_change=self._on_trigger_setting_change,
        )
        self.trigger_level.grid(column=1, row=1, padx=5, pady=2)

        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_edge")).grid(
            column=0, row=2, padx=5, pady=2, sticky="w"
        )
        self.trigger_edge = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.edge",
            default_value="rising",
            state="readonly",
            values=[
                t("ui.osc_tab.trigger_edges.rising"),
                t("ui.osc_tab.trigger_edges.falling"),
                t("ui.osc_tab.trigger_edges.both"),
            ],
            value_mapping={
                t("ui.osc_tab.trigger_edges.rising"): "rising",
                t("ui.osc_tab.trigger_edges.falling"): "falling",
                t("ui.osc_tab.trigger_edges.both"): "both",
            },
            width=10,
            on_change=self._on_trigger_setting_change,
        )
        self.trigger_edge.grid(column=1, row=2, padx=5, pady=2)

        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_mode")).grid(
            column=0, row=3, padx=5, pady=2, sticky="w"
        )
        self.trigger_mode = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.mode",
            default_value="continuous",
            state="readonly",
            values=[
                t("ui.osc_tab.trigger_modes.continuous"),
                t("ui.osc_tab.trigger_modes.single"),
            ],
            value_mapping={
                t("ui.osc_tab.trigger_modes.continuous"): "continuous",
                t("ui.osc_tab.trigger_modes.single"): "single",
            },
            width=10,
            on_change=self._on_trigger_setting_change,
        )
        self.trigger_mode.grid(column=1, row=3, padx=5, pady=2)

        capture_frame = ttk.LabelFrame(settings_container, text=t("ui.osc_tab.capture"))
        capture_frame.grid(column=0, row=1, padx=5, pady=5, sticky="ew")

        ttk.Label(capture_frame, text=t("ui.osc_tab.window_size")).grid(
            column=0, row=0, padx=5, pady=2, sticky="w"
        )
        self.window_size = PrefEntry(
            capture_frame,
            pref_key="osc.capture.window_size",
            default_value="100",
            width=8,
            on_change=self._on_capture_setting_change,
        )
        self.window_size.grid(column=1, row=0, padx=5, pady=2)

        save_controls_frame = ttk.Frame(capture_frame)
        save_controls_frame.grid(
            column=0, row=1, columnspan=2, padx=5, pady=5, sticky="ew"
        )

        self.save_png_button = ttk.Button(
            save_controls_frame, text=t("ui.osc_tab.save_png"), command=self._save_png
        )
        self.save_png_button.pack(side="left", padx=2)

        self.save_data_button = ttk.Button(
            save_controls_frame, text=t("ui.osc_tab.save_data"), command=self._save_data
        )
        self.save_data_button.pack(side="left", padx=2)

        self.clear_button = ttk.Button(
            save_controls_frame, text=t("ui.osc_tab.clear"), command=self._clear_display
        )
        self.clear_button.pack(side="left", padx=2)

        settings_container.columnconfigure(0, weight=1)

    def _toggle_settings(self):
        """Toggle the visibility of the settings frame."""
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

    def _setup_trigger_monitoring(self):
        if self._is_frame_valid() and self.is_armed:
            if self.data_tab.get_data():
                self._check_trigger_conditions()
            
            self.refresh_timer_id = self.frame.after(
                self.osc_refresh_rate_ms, self._setup_trigger_monitoring
            )

    def _stop_refresh_timer(self):
        """Stop the refresh timer."""
        if self.refresh_timer_id:
            try:
                self.frame.after_cancel(self.refresh_timer_id)
            except:
                pass
            self.refresh_timer_id = None

    def _schedule_after(self, delay, callback):
        """Schedule a callback and track it for cleanup."""
        callback_id = self.frame.after(delay, callback)
        self.pending_callbacks.append(callback_id)
        return callback_id

    def _cancel_all_callbacks(self):
        for callback_id in self.pending_callbacks[:]:
            try:
                self.frame.after_cancel(callback_id)
                self.pending_callbacks.remove(callback_id)
            except:
                pass

    def _is_widget_valid(self, widget_name):
        return hasattr(self, widget_name) and getattr(self, widget_name).winfo_exists()

    def _is_frame_valid(self):
        return hasattr(self, "frame") and self.frame.winfo_exists()

    def set_tab_active(self, is_active):
        self.is_active = is_active
        if not is_active:
            self._stop_refresh_timer()
        elif self._is_frame_valid():
            self._setup_trigger_monitoring()

    def _check_trigger_conditions(self):
        """Check if trigger conditions are met with simple data processing."""
        if not self.is_armed:
            return

        try:
            # Add cooldown period to prevent rapid triggers
            current_time = time.time()
            if current_time - self.last_trigger_time < 1.0:  # 1 second cooldown
                return
                
            # Get current data buffer
            data_lines = self.data_tab.get_data()
            if not data_lines or len(data_lines) < 10:
                return
                
            # Parse trigger settings
            try:
                column = int(self.trigger_source.get_value())
                trigger_level = float(self.trigger_level.get_value())
                window_size = int(self.window_size.get_value())
            except (ValueError, AttributeError):
                return
            
            # Parse data values for the trigger column (from end to start - time arrival order)
            values = []
            for line in reversed(data_lines[-200:]):  # Check last 200 lines
                try:
                    parts = line.strip().split()
                    if len(parts) > column:
                        value = float(parts[column])
                        values.append(value)
                except (ValueError, IndexError):
                    continue
            
            if len(values) < window_size:
                return
            
            # Reverse back to correct time order for processing
            values.reverse()
            
            # Simple rising edge detection on recent data
            trigger_edge = self.trigger_edge.get_value()
            for i in range(len(values) - window_size, len(values) - 1):
                if i <= 0:
                    continue
                    
                triggered = False
                if trigger_edge == "rising" and values[i-1] <= trigger_level < values[i]:
                    triggered = True
                elif trigger_edge == "falling" and values[i-1] >= trigger_level > values[i]:
                    triggered = True
                elif trigger_edge == "both" and (
                    (values[i-1] <= trigger_level < values[i]) or 
                    (values[i-1] >= trigger_level > values[i])
                ):
                    triggered = True
                    
                if triggered:
                    # Extract window starting from trigger point
                    # This ensures x=0 corresponds to the trigger point where y≈trigger_level
                    start_idx = i  # Start exactly at trigger point
                    end_idx = min(len(values), i + window_size)  # Window size after trigger
                    
                    window_data = values[start_idx:end_idx]
                    if len(window_data) >= window_size // 2:
                        self._process_triggered_data(window_data, 0)
                        
                        self._schedule_after(500, self._pause_callback)
                        break
                        
        except Exception as e:
            logger.error(f"Error in simple trigger detection: {e}")

    def _process_triggered_data(self, window_data, trigger_point):
        """Process triggered data and plot it with color gradient."""
        try:
            # Update last trigger time for cooldown
            self.last_trigger_time = time.time()
            
            # Add this set to our collection
            self.trigger_sets.append(window_data.copy())
            
            # Keep only the last max_sets
            if len(self.trigger_sets) > self.max_sets:
                self.trigger_sets.pop(0)  # Remove oldest
            
            # Clear for single shot mode or when first trigger in continuous mode
            trigger_mode = self.trigger_mode.get_value()
            if trigger_mode == "single" or len(self.trigger_sets) == 1:
                self.graph_manager.clear()
            
            # Plot all sets with color gradient (oldest to newest)
            self._plot_all_sets()
            
            if self._is_widget_valid("status_label"):
                self.status_label.config(text=t("ui.osc_tab.triggered"), foreground="red")
            
            self._schedule_after(300, self._update_status_to_armed)
            
        except Exception as e:
            logger.error(f"Error processing triggered data: {e}")

    def _update_status_to_armed(self):
        if self.is_armed and self._is_widget_valid("status_label"):
            self.status_label.config(text=t("ui.osc_tab.armed"), foreground="orange")

    def _pause_callback(self):
        pass

    def _plot_all_sets(self):
        """Plot all trigger sets with color gradient from oldest (light) to newest (dark)."""
        try:
            if not self.trigger_sets:
                return
                
            # Clear the plot
            self.graph_manager.clear()
            
            # Calculate colors - from light (old) to dark (new)
            num_sets = len(self.trigger_sets)
            
            # Plot sets from oldest to newest so newer ones are drawn on top
            for i, window_data in enumerate(self.trigger_sets):
                # Calculate intensity - older sets are lighter
                intensity = 0.3 + (i / (num_sets - 1)) * 0.7 if num_sets > 1 else 1.0
                
                # Create x-axis data starting from 0
                x_data = list(range(len(window_data)))
                
                # Create hex color from light blue (old) to dark blue (new)
                blue_value = int(255 * intensity)
                color = f"#{0:02x}{0:02x}{blue_value:02x}"  # RGB in hex format
                
                # Remove markers for cleaner look with multiple overlapping lines
                self.graph_manager.plot_line(x_data, window_data, color=color)
                # Override the marker setting
                self.graph_manager.ax.lines[-1].set_marker('')
            
            # Add trigger level line on top
            if self.trigger_sets:
                trigger_level = float(self.trigger_level.get_value())
                max_length = max(len(data) for data in self.trigger_sets)
                trigger_x = [0, max_length - 1]
                trigger_y = [trigger_level, trigger_level]
                self.graph_manager.plot_line(trigger_x, trigger_y, color='red')
                # Remove marker from trigger line too
                self.graph_manager.ax.lines[-1].set_marker('')
            
            # Set proper axis labels and limits
            self.graph_manager.set_labels(
                title=t("ui.osc_tab.oscilloscope_capture_title"),
                xlabel=t("ui.osc_tab.samples_label"), 
                ylabel=t("ui.osc_tab.value_label")
            )
            
            # Update the display
            self.graph_manager.update()
            
        except Exception as e:
            logger.error(f"Error plotting all sets: {e}")

    def _calculate_frequency(self, y_data):
        try:
            if len(y_data) < 10:
                self.freq_label.config(text=t("ui.osc_tab.frequency_unknown"))
                return

            mean_val = sum(y_data) / len(y_data)
            crossings = 0

            for i in range(1, len(y_data)):
                if (y_data[i - 1] <= mean_val < y_data[i]) or (
                    y_data[i - 1] >= mean_val > y_data[i]
                ):
                    crossings += 1

            if crossings > 2:
                cycles = crossings / 2
                self.freq_label.config(
                    text=t("ui.osc_tab.frequency_cycles", cycles=f"{cycles:.1f}")
                )
            else:
                self.freq_label.config(text=t("ui.osc_tab.frequency_unknown"))

        except Exception as e:
            self.freq_label.config(text=t("ui.osc_tab.frequency_error"))

    def _clear_display(self):
        """Clear the oscilloscope display and accumulated trigger sets."""
        try:
            self.trigger_sets.clear()
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
        """Toggle armed state."""
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

        if self._is_widget_valid("arm_button"):
            self.arm_button.config(text=t("ui.osc_tab.disarm"))
        if self._is_widget_valid("status_label"):
            self.status_label.config(text=t("ui.osc_tab.armed"), foreground="orange")
            
        self._setup_trigger_monitoring()

    def _disarm(self):
        self.is_armed = False
        self._stop_refresh_timer()

        if self._is_widget_valid("arm_button"):
            self.arm_button.config(text=t("ui.osc_tab.arm"))
        if self._is_widget_valid("status_label"):
            self.status_label.config(text=t("ui.osc_tab.ready"), foreground="blue")

    def _on_trigger_setting_change(self):
        pass

    def _on_capture_setting_change(self):
        pass

    def get_frame(self):
        """Get the tab frame."""
        return self.frame

    def cleanup(self):
        """Clean up resources."""
        self._stop_refresh_timer()
        self._cancel_all_callbacks()
        self._disarm()
