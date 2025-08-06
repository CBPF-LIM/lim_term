"""
Oscilloscope plotting and visualization utilities.

This module provides plotting functionality for the oscilloscope tab.
"""

from ..i18n import t
import matplotlib.pyplot as plt
import numpy as np

class OscPlotter:
    """Handles oscilloscope data plotting and visualization."""
    
    def __init__(self, graph_manager, trigger_source, trigger_level, window_size):
        self.graph_manager = graph_manager
        self.trigger_source = trigger_source
        self.trigger_level = trigger_level
        self.window_size = window_size
        
        self.data_line = None
        self.trigger_level_line = None
        self.trigger_point_line = None
        self.expected_window_line = None
        
        self.use_lines_only = True
        self.persistent_plotting = True
        self.background = None
        
        self.set_buffer_size = 4
        self.capture_sets = []
        self.current_set_index = 0
        self.set_colors = self._generate_color_palette()
    
    def plot_realtime_data(self, trigger_data):
        """Plot captured data during real-time capture using optimized blitting."""
        if not trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)
            
            if x_data and y_data:
                self._plot_current_and_buffer_sets(x_data, y_data, trigger_col, 
                                                  t("ui.osc_tab.capture_live_title"))
                
        except Exception as e:
            print(f"Real-time plot error: {e}")
    
    def plot_final_data(self, trigger_data):
        """Plot final captured data after capture completion."""
        if not trigger_data or not hasattr(self, 'graph_manager'):
            return
            
        try:
            trigger_col = int(self.trigger_source.get_value()) - 1
            
            x_data, y_data = self._extract_plot_data(trigger_data, trigger_col)
            
            if x_data and y_data:
                self._add_to_buffer(x_data, y_data)
                
                self._plot_buffer_sets(trigger_col, t("ui.osc_tab.capture_complete_title"))
                
                return y_data
                
        except Exception as e:
            print(f"Final plot error: {e}")
            return None
    
    def _generate_color_palette(self):
        """Generate color palette: newest = red, oldest = black using RGB formula."""
        colors = []
        N = self.set_buffer_size
        for n in range(N):
            intensity = n / (N - 1) if N > 1 else 0
            color = (1, intensity, intensity)
            colors.append(color)
        return colors
    
    def _add_to_buffer(self, x_data, y_data):
        """Add completed capture to N-set ring buffer."""
        while len(self.capture_sets) < self.set_buffer_size:
            self.capture_sets.append(None)
        
        self.capture_sets[self.current_set_index] = (x_data, y_data)
        
        self.current_set_index = (self.current_set_index + 1) % self.set_buffer_size
    
    def _plot_current_and_buffer_sets(self, current_x, current_y, trigger_col, title):
        """Plot current incomplete capture plus buffered complete captures."""
        self.graph_manager.clear()
        
        plot_order = self._get_plot_order()
        
        for buffer_index, age in plot_order:
            if self.capture_sets[buffer_index] is not None:
                x_data, y_data = self.capture_sets[buffer_index]
                color = self.set_colors[age]
                self.graph_manager.ax.plot(x_data, y_data, color=color, 
                                         linewidth=1.0)
        
        if current_x and current_y:
            self.graph_manager.ax.plot(current_x, current_y, color='red', 
                                     linewidth=1.5)
        
        self._add_static_elements(trigger_col, title)
        
        self._update_axis_limits()
        
        self.graph_manager.canvas.draw_idle()
    
    def _plot_buffer_sets(self, trigger_col, title):
        """Plot all buffered complete captures with onion skin effect."""
        self.graph_manager.clear()
        
        plot_order = self._get_plot_order()
        
        for buffer_index, age in plot_order:
            if self.capture_sets[buffer_index] is not None:
                x_data, y_data = self.capture_sets[buffer_index]
                color = self.set_colors[age]
                self.graph_manager.ax.plot(x_data, y_data, color=color, 
                                         linewidth=1.0)
        
        self._add_static_elements(trigger_col, title)
        
        self._update_axis_limits()
        
        self.graph_manager.canvas.draw()
    
    def _get_plot_order(self):
        """Get plotting order: oldest first (background), newest last (top).
        Returns list of (buffer_index, age) tuples where age 0=newest."""
        plot_order = []
        
        for i in range(self.set_buffer_size):
            if self.capture_sets[i] is not None:
                if i == self.current_set_index:
                    continue
                
                steps_back = (self.current_set_index - i) % self.set_buffer_size
                if steps_back == 0:
                    steps_back = self.set_buffer_size
                
                age = steps_back - 1
                plot_order.append((i, age))
        
        plot_order.sort(key=lambda x: x[1], reverse=True)
        return plot_order
    
    def _add_static_elements(self, trigger_col, title):
        """Add static elements like trigger level line and labels."""
        trigger_level = float(self.trigger_level.get_value())
        
        all_x = []
        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, _ = capture_set
                all_x.extend(x_data)
        
        if all_x:
            min_x, max_x = min(all_x), max(all_x)
        else:
            min_x, max_x = 0, int(self.window_size.get_value())
        
        self.graph_manager.ax.plot([min_x, max_x], [trigger_level, trigger_level], 
                                 color="red", linestyle="--", alpha=0.8, 
                                 label=t("ui.osc_tab.trigger_level_line"))
        
        self.graph_manager.ax.set_xlabel(t("ui.osc_tab.samples_after_trigger"))
        self.graph_manager.ax.set_ylabel(t("ui.osc_tab.column_label", column=trigger_col + 1))
        self.graph_manager.ax.set_title(title)
        self.graph_manager.ax.grid(True, alpha=0.3)
    
    def _update_axis_limits(self):
        """Update axis limits to fit all buffered data automatically."""
        all_x = []
        all_y = []
        
        for capture_set in self.capture_sets:
            if capture_set is not None:
                x_data, y_data = capture_set
                all_x.extend(x_data)
                all_y.extend(y_data)
        
        if not all_x or not all_y:
            self.graph_manager.ax.set_xlim(0, int(self.window_size.get_value()))
            return
        
        x_margin = (max(all_x) - min(all_x)) * 0.05
        y_margin = (max(all_y) - min(all_y)) * 0.1
        
        self.graph_manager.ax.set_xlim(min(all_x) - x_margin, max(all_x) + x_margin)
        self.graph_manager.ax.set_ylim(min(all_y) - y_margin, max(all_y) + y_margin)
    
    def clear_all_data(self):
        """Clear all plotting data and reset for new session."""
        self.capture_sets = []
        self.current_set_index = 0
        self.data_line = None
        self.trigger_level_line = None
        self.trigger_point_line = None
        self.expected_window_line = None
        self.background = None
        
        if hasattr(self, 'graph_manager'):
            self.graph_manager.clear()
    def _extract_plot_data(self, trigger_data, trigger_col):
        """Extract X and Y data from trigger data for plotting."""
        x_data = []
        y_data = []
        
        for i, line in enumerate(trigger_data):
            try:
                values = line.split()
                if trigger_col < len(values):
                    x_data.append(i)
                    y_data.append(float(values[trigger_col]))
            except (ValueError, IndexError):
                continue
                
        return x_data, y_data
