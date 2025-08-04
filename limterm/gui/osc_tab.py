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
from ..core import GraphManager
from ..utils import DataParser
from ..i18n import t, get_config_manager
from .preference_widgets import PrefEntry, PrefCombobox, PrefCheckbutton


class OscTab:
    """Oscilloscope-inspired data capture and visualization tab."""
    
    def __init__(self, parent, data_tab):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.config_manager = get_config_manager()
        
        # Oscilloscope state
        self.is_armed = False
        self.is_triggered = False
        self.trigger_data = []
        self.capture_start_time = None
        self.last_trigger_check = 0
        self.arm_start_time = None  # For auto mode timeout
        self.capture_count = 0  # Track number of captures
        self.trigger_point_index = -1  # Index in data buffer where trigger occurred
        
        # Trigger detection state
        self.last_sample_value = None
        self.trigger_detected = False
        
        self._create_widgets()
        self._setup_trigger_monitoring()
    
    def _create_widgets(self):
        """Create the oscilloscope interface."""
        # Main controls frame
        controls_frame = ttk.LabelFrame(self.frame, text="Oscilloscope Controls")
        controls_frame.grid(column=0, row=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        # Trigger settings
        trigger_frame = ttk.LabelFrame(controls_frame, text="Trigger Settings")
        trigger_frame.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
        
        # Trigger source (column selection)
        ttk.Label(trigger_frame, text="Trigger Source:").grid(column=0, row=0, padx=5, pady=2, sticky="w")
        self.trigger_source = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.source_column", 
            default_value="2",
            width=8,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_source.grid(column=1, row=0, padx=5, pady=2)
        
        # Trigger level
        ttk.Label(trigger_frame, text="Trigger Level:").grid(column=0, row=1, padx=5, pady=2, sticky="w")
        self.trigger_level = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.level",
            default_value="0.0",
            width=8,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_level.grid(column=1, row=1, padx=5, pady=2)
        
        # Trigger edge
        ttk.Label(trigger_frame, text="Trigger Edge:").grid(column=0, row=2, padx=5, pady=2, sticky="w")
        self.trigger_edge = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.edge",
            default_value="Rising",
            state="readonly",
            values=["Rising", "Falling", "Both"],
            width=10,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_edge.grid(column=1, row=2, padx=5, pady=2)
        
        # Trigger mode
        ttk.Label(trigger_frame, text="Trigger Mode:").grid(column=0, row=3, padx=5, pady=2, sticky="w")
        self.trigger_mode = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.mode",
            default_value="Normal",
            state="readonly",
            values=["Normal", "Auto", "Single"],
            width=10,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_mode.grid(column=1, row=3, padx=5, pady=2)
        
        # Capture settings
        capture_frame = ttk.LabelFrame(controls_frame, text="Capture Settings") 
        capture_frame.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        
        # Window size
        ttk.Label(capture_frame, text="Window Size:").grid(column=0, row=0, padx=5, pady=2, sticky="w")
        self.window_size = PrefEntry(
            capture_frame,
            pref_key="osc.capture.window_size",
            default_value="100",
            width=8,
            on_change=self._on_capture_setting_change
        )
        self.window_size.grid(column=1, row=0, padx=5, pady=2)
        
        # Pre-trigger percentage
        ttk.Label(capture_frame, text="Pre-trigger %:").grid(column=0, row=1, padx=5, pady=2, sticky="w") 
        self.pre_trigger_percent = PrefEntry(
            capture_frame,
            pref_key="osc.capture.pre_trigger_percent",
            default_value="20",
            width=8,
            on_change=self._on_capture_setting_change
        )
        self.pre_trigger_percent.grid(column=1, row=1, padx=5, pady=2)
        
        # Auto-save captures
        self.auto_save_enabled = PrefCheckbutton(
            capture_frame,
            pref_key="osc.capture.auto_save",
            default_value=True,
            text="Auto-save captures",
            on_change=self._on_capture_setting_change
        )
        self.auto_save_enabled.grid(column=0, row=2, columnspan=2, padx=5, pady=2, sticky="w")
        
        # Control buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
        
        self.arm_button = ttk.Button(
            button_frame, 
            text="ARM", 
            command=self._toggle_arm
        )
        self.arm_button.pack(pady=2, fill="x")
        
        self.single_shot_button = ttk.Button(
            button_frame,
            text="Single Shot",
            command=self._single_shot_capture
        )
        self.single_shot_button.pack(pady=2, fill="x")
        
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear Data", 
            command=self._clear_capture_data
        )
        self.clear_button.pack(pady=2, fill="x")
        
        # Status display
        status_frame = ttk.LabelFrame(controls_frame, text="Status")
        status_frame.grid(column=3, row=0, padx=5, pady=5, sticky="nsew")
        
        self.status_label = ttk.Label(status_frame, text="Ready", foreground="blue")
        self.status_label.pack(pady=5)
        
        self.samples_label = ttk.Label(status_frame, text="Samples: 0", font=("TkDefaultFont", 8))
        self.samples_label.pack()
        
        self.freq_label = ttk.Label(status_frame, text="Frequency: --", font=("TkDefaultFont", 8))
        self.freq_label.pack()
        
        self.capture_count_label = ttk.Label(status_frame, text="Captures: 0", font=("TkDefaultFont", 8))
        self.capture_count_label.pack()
        
        # Make columns expandable
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=0)
        controls_frame.columnconfigure(3, weight=0)
        
        # Graph display
        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(
            column=0, row=1, columnspan=4, padx=10, pady=10, sticky="nsew"
        )
        
        # Make the graph area expandable
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)
    
    def _setup_trigger_monitoring(self):
        """Set up periodic trigger monitoring."""
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self._check_trigger_conditions()
            self.frame.after(50, self._setup_trigger_monitoring)  # Check every 50ms
    
    def _check_trigger_conditions(self):
        """Check if trigger conditions are met."""
        if not self.is_armed:
            return
            
        try:
            # Get current data from data tab
            data_lines = self.data_tab.get_data()
            if not data_lines:
                return
            
            # Check for auto mode timeout (force trigger after 2 seconds)
            trigger_mode = self.trigger_mode.get_value()
            if trigger_mode == "Auto" and self.arm_start_time:
                time_armed = time.time() - self.arm_start_time
                if time_armed > 2.0:  # 2 second timeout for auto mode
                    self._trigger_detected()
                    return
                
            # Get trigger settings
            trigger_col = int(self.trigger_source.get_value()) - 1
            trigger_level = float(self.trigger_level.get_value())
            trigger_edge = self.trigger_edge.get_value()
            
            # Get the latest sample
            latest_line = data_lines[-1]
            try:
                values = latest_line.split()
                if trigger_col < len(values):
                    current_value = float(values[trigger_col])
                    
                    # Check for trigger condition
                    if self.last_sample_value is not None:
                        triggered = False
                        
                        if trigger_edge == "Rising":
                            triggered = (self.last_sample_value <= trigger_level < current_value)
                        elif trigger_edge == "Falling": 
                            triggered = (self.last_sample_value >= trigger_level > current_value)
                        elif trigger_edge == "Both":
                            triggered = ((self.last_sample_value <= trigger_level < current_value) or 
                                       (self.last_sample_value >= trigger_level > current_value))
                        
                        if triggered and not self.trigger_detected:
                            self._trigger_detected()
                    
                    self.last_sample_value = current_value
                    
            except (ValueError, IndexError):
                pass  # Skip invalid data lines
                
        except Exception as e:
            print(f"Trigger monitoring error: {e}")
    
    def _trigger_detected(self):
        """Handle trigger detection."""
        if not self.is_armed or not hasattr(self, 'frame') or not self.frame.winfo_exists():
            return
            
        self.trigger_detected = True
        self.capture_start_time = time.time()
        
        # Simply remember where we are in the data buffer right now
        current_data = self.data_tab.get_data()
        self.trigger_point_index = len(current_data)  # Data after this point is what we want
        
        # Clear the chart for new capture
        if hasattr(self, 'graph_manager'):
            self.graph_manager.clear()
            self.graph_manager.canvas.draw_idle()
        
        # Update status
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text="TRIGGERED", foreground="red")
        
        # Start capture
        self._start_capture()
    
    def _start_capture(self):
        """Start data capture after trigger."""
        try:
            window_size = int(self.window_size.get_value())
            self.samples_needed = window_size  # How many samples we need total
            
            # Update status immediately
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="CAPTURING...", foreground="red")
            
            # Start monitoring for new data
            self._continue_capture()
                
        except Exception as e:
            print(f"Capture start error: {e}")
            self._disarm()
    
    def _continue_capture(self):
        """Continue capturing data in real-time after trigger."""
        if not self.trigger_detected or not hasattr(self, 'frame') or not self.frame.winfo_exists():
            return
            
        try:
            # Get current data buffer
            current_data = self.data_tab.get_data()
            
            # Get all data that came AFTER the trigger point
            new_data_after_trigger = current_data[self.trigger_point_index:]
            
            # Check if we have enough data
            window_size = int(self.window_size.get_value())
            if len(new_data_after_trigger) >= window_size:
                # We have enough data - complete the capture
                self.trigger_data = new_data_after_trigger[:window_size]  # Take exactly what we need
                self._complete_capture()
            else:
                # Still collecting data - plot what we have so far
                self.trigger_data = new_data_after_trigger
                self._plot_captured_data_realtime()
                
                # Update progress
                progress = (len(new_data_after_trigger) / window_size) * 100
                if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
                    self.samples_label.config(text=f"Samples: {len(new_data_after_trigger)}/{window_size} ({progress:.0f}%)")
                
                # Continue monitoring
                if hasattr(self, 'frame') and self.frame.winfo_exists():
                    self.frame.after(50, self._continue_capture)
                
        except Exception as e:
            print(f"Continue capture error: {e}")
            self._disarm()
    
    def _complete_capture(self):
        """Complete the capture and display results."""
        try:
            window_size = int(self.window_size.get_value())
            
            # Trim to exact window size if we got more data than needed
            if len(self.trigger_data) > window_size:
                self.trigger_data = self.trigger_data[:window_size]
            
            # Plot the final captured data
            self._plot_captured_data_final()
            
            # Auto-save if enabled
            if self.auto_save_enabled.get_value():
                self._save_capture()
            
            # Update capture count
            self.capture_count += 1
            if hasattr(self, 'capture_count_label') and self.capture_count_label.winfo_exists():
                self.capture_count_label.config(text=f"Captures: {self.capture_count}")
            
            # Update status
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="CAPTURED", foreground="green")
            if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
                self.samples_label.config(text=f"Samples: {len(self.trigger_data)}")
            
            # Handle different trigger modes
            trigger_mode = self.trigger_mode.get_value()
            
            if trigger_mode == "Single":
                self._disarm()  # Single shot - disarm after capture
            elif trigger_mode == "Auto":
                # Auto mode - re-arm automatically after delay
                if hasattr(self, 'frame') and self.frame.winfo_exists():
                    self.frame.after(500, self._auto_rearm)  # Re-arm after 500ms
            elif trigger_mode == "Normal":
                self._disarm()  # Normal mode - disarm after capture
            
        except Exception as e:
            print(f"Capture completion error: {e}")
            self._disarm()
    
    def _auto_rearm(self):
        """Re-arm for auto mode after a delay."""
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            # Clear previous capture for new trigger
            self._clear_capture_data()
            self._arm()
    
    def _plot_captured_data_realtime(self):
        """Plot the captured oscilloscope data in real-time during capture."""
        if not self.trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            # Use sample number as X-axis and trigger source column as Y-axis
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            # Extract data for plotting - this is NEW data collected AFTER trigger
            x_data = []  # Sample numbers starting from 0 (trigger point)
            y_data = []  # Values from trigger column
            
            for i, line in enumerate(self.trigger_data):
                try:
                    values = line.split()
                    if trigger_col < len(values):
                        x_data.append(i)  # Sample number starting from 0 (trigger is at x=0)
                        y_data.append(float(values[trigger_col]))
                except (ValueError, IndexError):
                    continue
            
            if x_data and y_data:
                # Clear and plot current data
                self.graph_manager.clear()
                self.graph_manager.plot_line(x_data, y_data, color="blue", marker="o")
                
                # Add trigger level line
                trigger_level = float(self.trigger_level.get_value())
                window_size = int(self.window_size.get_value())
                trigger_line_x = [0, window_size]  # From trigger point to end of window
                trigger_line_y = [trigger_level, trigger_level]
                self.graph_manager.ax.plot(trigger_line_x, trigger_line_y, 
                                         color="red", linestyle="--", alpha=0.7, label="Trigger Level")
                
                # Mark trigger point at x=0 (start of capture)
                self.graph_manager.ax.axvline(x=0, color="red", linestyle=":", alpha=0.7, label="Trigger Point")
                
                # Show expected window size with gray area for uncaptured data
                if len(x_data) < window_size:
                    remaining_x = list(range(len(x_data), window_size))
                    if y_data:
                        remaining_y = [trigger_level] * len(remaining_x)  # Use trigger level as guide
                        self.graph_manager.ax.plot(remaining_x, remaining_y, 
                                                 color="gray", linestyle=":", alpha=0.5, 
                                                 label="Expected Window")
                
                # Set axes labels and limits
                self.graph_manager.ax.set_xlabel("Samples After Trigger")
                self.graph_manager.ax.set_ylabel(f"Column {trigger_col + 1}")
                self.graph_manager.ax.set_xlim(0, window_size)
                self.graph_manager.ax.legend()
                self.graph_manager.ax.grid(True, alpha=0.3)
                
                # Update canvas
                self.graph_manager.canvas.draw_idle()
                
        except Exception as e:
            print(f"Real-time plot error: {e}")
    
    def _plot_captured_data_final(self):
        """Plot the final captured oscilloscope data."""
        if not self.trigger_data or not hasattr(self, 'graph_manager'):
            return
            
    def _plot_captured_data_final(self):
        """Plot the final captured oscilloscope data."""
        if not self.trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            # Use sample number as X-axis and trigger source column as Y-axis
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            # Extract data for plotting - this is NEW data collected AFTER trigger
            x_data = []  # Sample numbers starting from 0 (trigger point)
            y_data = []  # Values from trigger column
            
            for i, line in enumerate(self.trigger_data):
                try:
                    values = line.split()
                    if trigger_col < len(values):
                        x_data.append(i)  # Sample number starting from 0 (trigger is at x=0)
                        y_data.append(float(values[trigger_col]))
                except (ValueError, IndexError):
                    continue
            
            if x_data and y_data:
                # Clear and plot final data
                self.graph_manager.clear()
                self.graph_manager.plot_line(x_data, y_data, color="blue", marker="o")
                
                # Add trigger level line
                trigger_level = float(self.trigger_level.get_value())
                trigger_line_x = [0, max(x_data)] if x_data else [0, 1]
                trigger_line_y = [trigger_level, trigger_level]
                self.graph_manager.ax.plot(trigger_line_x, trigger_line_y, 
                                         color="red", linestyle="--", alpha=0.7, label="Trigger Level")
                
                # Mark trigger point at x=0 (start of capture)
                self.graph_manager.ax.axvline(x=0, color="red", linestyle=":", alpha=0.7, label="Trigger Point")
                
                self.graph_manager.set_labels(
                    title="Oscilloscope Capture - Complete",
                    xlabel="Samples After Trigger",
                    ylabel=f"Channel {self.trigger_source.get_value()}"
                )
                self.graph_manager.ax.legend()
                self.graph_manager.ax.grid(True, alpha=0.3)
                
                # Force immediate update
                self.graph_manager.update()
                self.graph_manager.canvas.draw_idle()
                
                # Calculate and display frequency
                self._calculate_frequency(y_data)
                
        except Exception as e:
            print(f"Final plot error: {e}")
    
    def _calculate_frequency(self, y_data):
        """Calculate approximate frequency of the signal."""
        try:
            if len(y_data) < 10:  # Need sufficient data points
                self.freq_label.config(text="Frequency: --")
                return
            
            # Simple zero-crossing frequency estimation
            mean_val = sum(y_data) / len(y_data)
            crossings = 0
            
            for i in range(1, len(y_data)):
                if (y_data[i-1] <= mean_val < y_data[i]) or (y_data[i-1] >= mean_val > y_data[i]):
                    crossings += 1
            
            if crossings > 2:
                # Estimate frequency (assuming uniform sampling)
                # This is a rough approximation
                cycles = crossings / 2  # Two crossings per cycle
                samples_per_cycle = len(y_data) / cycles
                
                # Display relative frequency information
                self.freq_label.config(text=f"~{cycles:.1f} cycles")
            else:
                self.freq_label.config(text="Frequency: --")
                
        except Exception as e:
            self.freq_label.config(text="Frequency: Error")
    
    def _save_capture(self):
        """Save captured data and screenshot."""
        if not self.trigger_data:
            return
            
        try:
            # Create oscilloscope captures directory
            capture_dir = "osc_captures"
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)
            
            # Generate timestamp filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_filename = f"osc_capture_{timestamp}"
            
            # Save data as text file
            data_filename = os.path.join(capture_dir, f"{base_filename}.txt")
            with open(data_filename, "w", encoding="utf-8") as f:
                for line in self.trigger_data:
                    f.write(line + "\n")
            
            # Save screenshot as PNG
            image_filename = os.path.join(capture_dir, f"{base_filename}.png")
            self.graph_manager.figure.savefig(image_filename, dpi=300, bbox_inches="tight")
            
            # Notify user
            self.data_tab.add_message(f"Oscilloscope capture saved: {base_filename}")
            
        except Exception as e:
            print(f"Save capture error: {e}")
            self.data_tab.add_message(f"Error saving capture: {e}")
    
    def _toggle_arm(self):
        """Toggle armed state."""
        if self.is_armed:
            self._disarm()
        else:
            self._arm()
    
    def _arm(self):
        """Arm the oscilloscope for trigger detection."""
        if not hasattr(self, 'frame') or not self.frame.winfo_exists():
            return
            
        self.is_armed = True
        self.trigger_detected = False
        self.last_sample_value = None
        self.arm_start_time = time.time()  # Record arm time for auto mode
        
        trigger_mode = self.trigger_mode.get_value()
        if trigger_mode == "Single":
            self._clear_capture_data()  # Clear data for single shot
        
        if hasattr(self, 'arm_button') and self.arm_button.winfo_exists():
            self.arm_button.config(text="DISARM")
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text="ARMED", foreground="orange")
        if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
            self.samples_label.config(text="Samples: 0")
    
    def _disarm(self):
        """Disarm the oscilloscope."""
        self.is_armed = False
        self.trigger_detected = False
        
        if hasattr(self, 'arm_button') and self.arm_button.winfo_exists():
            self.arm_button.config(text="ARM")
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text="Ready", foreground="blue")
    
    def _single_shot_capture(self):
        """Perform a single-shot capture."""
        # Clear any existing data first
        self._clear_capture_data()
        
        # Arm for single capture
        self._arm()
    
    def _clear_capture_data(self):
        """Clear captured data and graph."""
        self.trigger_data = []
        self.trigger_point_index = -1
        
        # Clear and update the graph immediately
        if hasattr(self, 'graph_manager'):
            self.graph_manager.clear()
            self.graph_manager.update()
            self.graph_manager.canvas.draw_idle()  # Force immediate canvas update
        
        # Reset status displays
        if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
            self.samples_label.config(text="Samples: 0")
        if hasattr(self, 'freq_label') and self.freq_label.winfo_exists():
            self.freq_label.config(text="Frequency: --")
        
        if not self.is_armed:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text="Ready", foreground="blue")
    
    def _on_trigger_setting_change(self):
        """Handle trigger setting changes."""
        # Reset trigger state when settings change
        if self.is_armed:
            self.last_sample_value = None
            self.trigger_detected = False
    
    def _on_capture_setting_change(self):
        """Handle capture setting changes."""
        pass  # Settings are automatically saved by preference widgets
    
    def get_frame(self):
        """Get the tab frame."""
        return self.frame
    
    def cleanup(self):
        """Clean up resources."""
        self._disarm()
