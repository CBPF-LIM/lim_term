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
from .osc_trigger import OscTrigger
from .osc_plotter import OscPlotter


class OscTab:
    """Oscilloscope-inspired data capture and visualization tab."""
    
    def __init__(self, parent, data_tab):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.config_manager = get_config_manager()
        
        # Oscilloscope state
        self.is_armed = False
        self.trigger_data = []
        self.capture_start_time = None
        self.capture_count = 0  # Track number of captures
        
        # Create helper modules
        self.trigger_manager = None  # Will be initialized after widgets
        self.plotter = None  # Will be initialized after widgets
        
        self._create_widgets()
        self._setup_trigger_monitoring()
    
    def _create_widgets(self):
        """Create the oscilloscope interface."""
        # Main controls frame
        controls_frame = ttk.LabelFrame(self.frame, text=t("ui.osc_tab.oscilloscope_controls"))
        controls_frame.grid(column=0, row=0, columnspan=4, padx=10, pady=5, sticky="ew")
        
        # Trigger settings
        trigger_frame = ttk.LabelFrame(controls_frame, text=t("ui.osc_tab.trigger_settings"))
        trigger_frame.grid(column=0, row=0, padx=5, pady=5, sticky="ew")
        
        # Trigger source (column selection)
        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_source")).grid(column=0, row=0, padx=5, pady=2, sticky="w")
        self.trigger_source = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.source_column", 
            default_value="2",
            width=8,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_source.grid(column=1, row=0, padx=5, pady=2)
        
        # Trigger level
        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_level")).grid(column=0, row=1, padx=5, pady=2, sticky="w")
        self.trigger_level = PrefEntry(
            trigger_frame,
            pref_key="osc.trigger.level",
            default_value="0.0",
            width=8,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_level.grid(column=1, row=1, padx=5, pady=2)
        
        # Trigger edge
        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_edge")).grid(column=0, row=2, padx=5, pady=2, sticky="w")
        self.trigger_edge = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.edge",
            default_value=t("ui.osc_tab.trigger_edges.rising"),
            state="readonly",
            values=[
                t("ui.osc_tab.trigger_edges.rising"),
                t("ui.osc_tab.trigger_edges.falling"),
                t("ui.osc_tab.trigger_edges.both")
            ],
            width=10,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_edge.grid(column=1, row=2, padx=5, pady=2)
        
        # Trigger mode
        ttk.Label(trigger_frame, text=t("ui.osc_tab.trigger_mode")).grid(column=0, row=3, padx=5, pady=2, sticky="w")
        self.trigger_mode = PrefCombobox(
            trigger_frame,
            pref_key="osc.trigger.mode",
            default_value=t("ui.osc_tab.trigger_modes.continuous"),
            state="readonly",
            values=[
                t("ui.osc_tab.trigger_modes.continuous"),
                t("ui.osc_tab.trigger_modes.single")
            ],
            width=10,
            on_change=self._on_trigger_setting_change
        )
        self.trigger_mode.grid(column=1, row=3, padx=5, pady=2)
        
        # Capture settings
        capture_frame = ttk.LabelFrame(controls_frame, text=t("ui.osc_tab.capture_settings")) 
        capture_frame.grid(column=1, row=0, padx=5, pady=5, sticky="ew")
        
        # Window size
        ttk.Label(capture_frame, text=t("ui.osc_tab.window_size")).grid(column=0, row=0, padx=5, pady=2, sticky="w")
        self.window_size = PrefEntry(
            capture_frame,
            pref_key="osc.capture.window_size",
            default_value="100",
            width=8,
            on_change=self._on_capture_setting_change
        )
        self.window_size.grid(column=1, row=0, padx=5, pady=2)
        
        # Manual save controls
        save_controls_frame = ttk.Frame(capture_frame)
        save_controls_frame.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        self.save_png_button = ttk.Button(
            save_controls_frame,
            text=t("ui.osc_tab.save_png"),
            command=self._save_png
        )
        self.save_png_button.pack(side="left", padx=2)
        
        self.save_data_button = ttk.Button(
            save_controls_frame,
            text=t("ui.osc_tab.save_data"),
            command=self._save_data
        )
        self.save_data_button.pack(side="left", padx=2)
        
        # Control buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(column=2, row=0, padx=5, pady=5, sticky="nsew")
        
        self.arm_button = ttk.Button(
            button_frame, 
            text=t("ui.osc_tab.arm"), 
            command=self._toggle_arm
        )
        self.arm_button.pack(pady=2, fill="x")
        
        self.single_shot_button = ttk.Button(
            button_frame,
            text=t("ui.osc_tab.single_shot"),
            command=self._single_shot_capture
        )
        self.single_shot_button.pack(pady=2, fill="x")
        
        self.clear_button = ttk.Button(
            button_frame,
            text=t("ui.osc_tab.clear_data"), 
            command=self._clear_capture_data
        )
        self.clear_button.pack(pady=2, fill="x")
        
        # Status display
        status_frame = ttk.LabelFrame(controls_frame, text=t("ui.osc_tab.status"))
        status_frame.grid(column=3, row=0, padx=5, pady=5, sticky="nsew")
        
        self.status_label = ttk.Label(status_frame, text=t("ui.osc_tab.ready"), foreground="blue")
        self.status_label.pack(pady=5)
        
        self.samples_label = ttk.Label(status_frame, text=f"{t('ui.osc_tab.samples')} 0", font=("TkDefaultFont", 8))
        self.samples_label.pack()
        
        self.freq_label = ttk.Label(status_frame, text=t("ui.osc_tab.frequency_unknown"), font=("TkDefaultFont", 8))
        self.freq_label.pack()
        
        self.capture_count_label = ttk.Label(status_frame, text=f"{t('ui.osc_tab.captures')} 0", font=("TkDefaultFont", 8))
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
        
        # Initialize helper modules now that widgets exist
        self.trigger_manager = OscTrigger(
            self.data_tab, self.trigger_source, self.trigger_level, 
            self.trigger_edge, self.trigger_mode
        )
        self.plotter = OscPlotter(
            self.graph_manager, self.trigger_source, self.trigger_level, 
            self.window_size
        )
    
    def _setup_trigger_monitoring(self):
        """Set up periodic trigger monitoring."""
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self._check_trigger_conditions()
            self.frame.after(50, self._setup_trigger_monitoring)  # Check every 50ms
    
    def _check_trigger_conditions(self):
        """Check if trigger conditions are met."""
        if not hasattr(self, 'trigger_manager') or not self.trigger_manager:
            return
            
        if self.trigger_manager.check_trigger_conditions():
            self._trigger_detected()
    
    def _trigger_detected(self):
        """Handle trigger detection."""
        if not self.is_armed or not hasattr(self, 'frame') or not self.frame.winfo_exists():
            return
            
        self.capture_start_time = time.time()
        
        # Clear the chart for new capture
        if hasattr(self, 'graph_manager'):
            self.graph_manager.clear()
            self.graph_manager.canvas.draw_idle()
        
        # Update status
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=t("ui.osc_tab.triggered"), foreground="red")
        
        # Start capture
        self._start_capture()
    
    def _start_capture(self):
        """Start data capture after trigger."""
        try:
            window_size = int(self.window_size.get_value())
            self.samples_needed = window_size  # How many samples we need total
            
            # Update status immediately
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text=t("ui.osc_tab.capturing"), foreground="red")
            
            # Start monitoring for new data
            self._continue_capture()
                
        except Exception as e:
            print(f"Capture start error: {e}")
            self._disarm()
    
    def _continue_capture(self):
        """Continue capturing data in real-time after trigger."""
        if not self.trigger_manager.is_triggered or not hasattr(self, 'frame') or not self.frame.winfo_exists():
            return
            
        try:
            # Get current data buffer
            current_data = self.data_tab.get_data()
            
            # Get all data that came AFTER the trigger point
            trigger_point = self.trigger_manager.get_trigger_point_index()
            new_data_after_trigger = current_data[trigger_point:]
            
            # Check if we have enough data
            window_size = int(self.window_size.get_value())
            if len(new_data_after_trigger) >= window_size:
                # We have enough data - complete the capture
                self.trigger_data = new_data_after_trigger[:window_size]  # Take exactly what we need
                self._complete_capture()
            else:
                # Still collecting data - plot what we have so far
                self.trigger_data = new_data_after_trigger
                if hasattr(self, 'plotter'):
                    self.plotter.plot_realtime_data(self.trigger_data)
                
                # Update progress
                progress = (len(new_data_after_trigger) / window_size) * 100
                if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
                    self.samples_label.config(text=f"{t('ui.osc_tab.samples')} {len(new_data_after_trigger)}/{window_size} ({progress:.0f}%)")
                
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
            y_data = None
            if hasattr(self, 'plotter'):
                y_data = self.plotter.plot_final_data(self.trigger_data)
            
            # Calculate and display frequency
            if y_data:
                self._calculate_frequency(y_data)
            
            # Update capture count
            self.capture_count += 1
            if hasattr(self, 'capture_count_label') and self.capture_count_label.winfo_exists():
                self.capture_count_label.config(text=f"{t('ui.osc_tab.captures')} {self.capture_count}")
            
            # Update status
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text=t("ui.osc_tab.captured"), foreground="green")
            if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
                self.samples_label.config(text=f"{t('ui.osc_tab.samples')} {len(self.trigger_data)}")
            
            # Handle different trigger modes
            trigger_mode = self.trigger_mode.get_value()
            
            if trigger_mode == t("ui.osc_tab.trigger_modes.single"):
                self._disarm()  # Single shot - disarm after capture
            elif trigger_mode == t("ui.osc_tab.trigger_modes.continuous"):
                # Continuous mode - re-arm automatically after brief delay
                if hasattr(self, 'frame') and self.frame.winfo_exists():
                    self.frame.after(200, self._auto_rearm)  # Re-arm after 200ms
            
        except Exception as e:
            print(t("ui.osc_tab.capture_completion_error", error=str(e)))
            self._disarm()
    
    def _auto_rearm(self):
        """Re-arm for auto mode after a delay."""
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            # Clear previous capture for new trigger
            self._clear_capture_data()
            self._arm()
    
    def _calculate_frequency(self, y_data):
        """Calculate approximate frequency of the signal."""
        try:
            if len(y_data) < 10:  # Need sufficient data points
                self.freq_label.config(text=t("ui.osc_tab.frequency_unknown"))
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
                
                # Display relative frequency information
                self.freq_label.config(text=t("ui.osc_tab.frequency_cycles", cycles=f"{cycles:.1f}"))
            else:
                self.freq_label.config(text=t("ui.osc_tab.frequency_unknown"))
                
        except Exception as e:
            self.freq_label.config(text=t("ui.osc_tab.frequency_error"))
    
    def _save_png(self):
        """Save only the screenshot."""
        if not self.trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            # Create oscilloscope captures directory
            capture_dir = "osc_captures"
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)
            
            # Generate timestamp filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = os.path.join(capture_dir, f"osc_capture_{timestamp}.png")
            
            # Save screenshot as PNG
            self.graph_manager.figure.savefig(image_filename, dpi=300, bbox_inches="tight")
            
            # Notify user
            self.data_tab.add_message(t("ui.osc_tab.png_saved", filename=f"osc_capture_{timestamp}.png"))
            
        except Exception as e:
            print(f"Save PNG error: {e}")
            self.data_tab.add_message(t("ui.osc_tab.save_error", error=str(e)))
    
    def _save_data(self):
        """Save only the captured data."""
        if not self.trigger_data:
            return
            
        try:
            # Create oscilloscope captures directory
            capture_dir = "osc_captures"
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)
            
            # Generate timestamp filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            data_filename = os.path.join(capture_dir, f"osc_capture_{timestamp}.txt")
            
            # Save data as text file
            with open(data_filename, "w", encoding="utf-8") as f:
                for line in self.trigger_data:
                    f.write(line + "\n")
            
            # Notify user
            self.data_tab.add_message(t("ui.osc_tab.data_saved", filename=f"osc_capture_{timestamp}.txt"))
            
        except Exception as e:
            print(f"Save data error: {e}")
            self.data_tab.add_message(t("ui.osc_tab.save_error", error=str(e)))
    
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
        
        # Use trigger manager for state management
        if hasattr(self, 'trigger_manager'):
            self.trigger_manager.arm()
        
        trigger_mode = self.trigger_mode.get_value()
        if trigger_mode == t("ui.osc_tab.trigger_modes.single"):
            self._clear_capture_data()  # Clear data for single shot
        
        if hasattr(self, 'arm_button') and self.arm_button.winfo_exists():
            self.arm_button.config(text=t("ui.osc_tab.disarm"))
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=t("ui.osc_tab.armed"), foreground="orange")
        if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
            self.samples_label.config(text=f"{t('ui.osc_tab.samples')} 0")
    
    def _disarm(self):
        """Disarm the oscilloscope."""
        self.is_armed = False
        
        # Use trigger manager for state management
        if hasattr(self, 'trigger_manager'):
            self.trigger_manager.disarm()
        
        if hasattr(self, 'arm_button') and self.arm_button.winfo_exists():
            self.arm_button.config(text=t("ui.osc_tab.arm"))
        if hasattr(self, 'status_label') and self.status_label.winfo_exists():
            self.status_label.config(text=t("ui.osc_tab.ready"), foreground="blue")
    
    def _single_shot_capture(self):
        """Perform a single-shot capture."""
        # Clear any existing data first
        self._clear_capture_data()
        
        # Arm for single capture
        self._arm()
    
    def _clear_capture_data(self):
        """Clear captured data and graph."""
        self.trigger_data = []
        
        # Clear and update the graph immediately
        if hasattr(self, 'graph_manager'):
            self.graph_manager.clear()
            self.graph_manager.update()
            self.graph_manager.canvas.draw_idle()  # Force immediate canvas update
        
        # Reset status displays
        if hasattr(self, 'samples_label') and self.samples_label.winfo_exists():
            self.samples_label.config(text=f"{t('ui.osc_tab.samples')} 0")
        if hasattr(self, 'freq_label') and self.freq_label.winfo_exists():
            self.freq_label.config(text=t("ui.osc_tab.frequency_unknown"))
        
        if not self.is_armed:
            if hasattr(self, 'status_label') and self.status_label.winfo_exists():
                self.status_label.config(text=t("ui.osc_tab.ready"), foreground="blue")
    
    def _on_trigger_setting_change(self):
        """Handle trigger setting changes."""
        # Reset trigger state when settings change
        if hasattr(self, 'trigger_manager') and self.trigger_manager and self.is_armed:
            self.trigger_manager.reset_trigger_state()
    
    def _on_capture_setting_change(self):
        """Handle capture setting changes."""
        pass  # Settings are automatically saved by preference widgets
    
    def get_frame(self):
        """Get the tab frame."""
        return self.frame
    
    def cleanup(self):
        """Clean up resources."""
        self._disarm()
