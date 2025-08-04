"""
Oscilloscope plotting and visualization utilities.

This module provides plotting functionality for the oscilloscope tab.
"""

from ..i18n import t

class OscPlotter:
    """Handles oscilloscope data plotting and visualization."""
    
    def __init__(self, graph_manager, trigger_source, trigger_level, window_size):
        self.graph_manager = graph_manager
        self.trigger_source = trigger_source
        self.trigger_level = trigger_level
        self.window_size = window_size
    
    def plot_realtime_data(self, trigger_data):
        """Plot captured data during real-time capture."""
        if not trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            # Use sample number as X-axis and trigger source column as Y-axis
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            # Extract data for plotting
            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)
            
            if x_data and y_data:
                # Clear and plot current data
                self.graph_manager.clear()
                self.graph_manager.plot_line(x_data, y_data, color="blue", marker="o")
                
                # Add visual elements
                self._add_trigger_level_line()
                self._add_trigger_point_marker()
                self._add_expected_window(len(x_data))
                self._set_plot_labels(trigger_col, t("ui.osc_tab.capture_live_title"))
                
                # Update canvas
                self.graph_manager.canvas.draw_idle()
                
        except Exception as e:
            print(f"Real-time plot error: {e}")
    
    def plot_final_data(self, trigger_data):
        """Plot final captured data after capture completion."""
        if not trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            # Use sample number as X-axis and trigger source column as Y-axis
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            # Extract data for plotting
            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)
            
            if x_data and y_data:
                # Clear and plot final data
                self.graph_manager.clear()
                self.graph_manager.plot_line(x_data, y_data, color="blue", marker="o")
                
                # Add visual elements
                self._add_trigger_level_line(max_x=max(x_data) if x_data else 1)
                self._add_trigger_point_marker()
                self._set_plot_labels(trigger_col, t("ui.osc_tab.capture_complete_title"))
                
                # Force immediate update
                self.graph_manager.update()
                self.graph_manager.canvas.draw_idle()
                
                return y_data  # Return for frequency calculation
                
        except Exception as e:
            print(f"Final plot error: {e}")
            return None
    
    def _extract_plot_data(self, trigger_data, trigger_col):
        """Extract X and Y data from trigger data for plotting."""
        x_data = []  # Sample numbers starting from 0 (trigger point)
        y_data = []  # Values from trigger column
        
        for i, line in enumerate(trigger_data):
            try:
                values = line.split()
                if trigger_col < len(values):
                    x_data.append(i)  # Sample number starting from 0
                    y_data.append(float(values[trigger_col]))
            except (ValueError, IndexError):
                continue
                
        return x_data, y_data
    
    def _add_trigger_level_line(self, max_x=None):
        """Add horizontal trigger level line to plot."""
        trigger_level = float(self.trigger_level.get_value())
        window_size = int(self.window_size.get_value())
        
        if max_x is None:
            max_x = window_size
            
        trigger_line_x = [0, max_x]
        trigger_line_y = [trigger_level, trigger_level]
        self.graph_manager.ax.plot(trigger_line_x, trigger_line_y, 
                                 color="red", linestyle="--", alpha=0.7, 
                                 label=t("ui.osc_tab.trigger_level_line"))
    
    def _add_trigger_point_marker(self):
        """Add vertical line marking the trigger point at x=0."""
        self.graph_manager.ax.axvline(x=0, color="red", linestyle=":", 
                                    alpha=0.7, label=t("ui.osc_tab.trigger_point_line"))
    
    def _add_expected_window(self, current_samples):
        """Add gray line showing expected window size."""
        window_size = int(self.window_size.get_value())
        trigger_level = float(self.trigger_level.get_value())
        
        if current_samples < window_size:
            remaining_x = list(range(current_samples, window_size))
            remaining_y = [trigger_level] * len(remaining_x)
            self.graph_manager.ax.plot(remaining_x, remaining_y, 
                                     color="gray", linestyle=":", alpha=0.5, 
                                     label=t("ui.osc_tab.expected_window"))
    
    def _set_plot_labels(self, trigger_col, title):
        """Set plot labels and formatting."""
        self.graph_manager.ax.set_xlabel(t("ui.osc_tab.samples_after_trigger"))
        self.graph_manager.ax.set_ylabel(t("ui.osc_tab.column_label", column=trigger_col + 1))
        self.graph_manager.ax.set_xlim(0, int(self.window_size.get_value()))
        self.graph_manager.ax.set_title(title)
        self.graph_manager.ax.legend()
        self.graph_manager.ax.grid(True, alpha=0.3)
