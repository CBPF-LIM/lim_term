"""
Graph tab plotting module.
Handles chart creation and plotting logic.
"""

import time
from ..utils import DataParser


class GraphTabPlotter:
    """Manages chart plotting and rendering for the graph tab."""
    
    def __init__(self, graph_manager, data_tab):
        self.graph_manager = graph_manager
        self.data_tab = data_tab
        self.last_render_time = 0
        self.debug_refresh = False
        
    def plot_graph(self, settings):
        """Main plotting function."""
        if not self.data_tab.data:
            return False
            
        start_time = time.time()
        
        try:
            # Parse data
            x_col = settings.get('x_column', '1')
            chart_type = settings.get('chart_type', 'time_series')
            
            # Get data
            data_lines = [entry["value"] for entry in self.data_tab.data if entry["type"] == "data"]
            if not data_lines:
                return False
                
            x_data, data_columns = DataParser.parse_data_for_plotting(data_lines, x_col)
            if not x_data:
                return False
                
            # Plot based on chart type
            if chart_type == "time_series":
                self._plot_time_series_chart(x_data, data_lines, x_col, settings)
            elif chart_type == "stacked_area":
                self._plot_stacked_chart(x_data, data_lines, x_col, settings)
                
            # Update timing info
            self.last_render_time = time.time() - start_time
            if self.debug_refresh:
                print(f"Chart rendered in {self.last_render_time:.3f}s")
                
            return True
            
        except Exception as e:
            print(f"Error plotting graph: {e}")
            return False
    
    def _plot_time_series_chart(self, x_data, data_lines, x_col, settings):
        """Plot time series chart."""
        self.graph_manager.clear()
        
        # Get series data
        series_plotted = 0
        for i in range(5):
            series_settings = settings.get(f'series_{i}', {})
            if not series_settings.get('enabled', False):
                continue
                
            y_col = series_settings.get('column', '')
            if not y_col:
                continue
                
            try:
                # Parse and plot series
                _, data_columns = DataParser.parse_data_for_plotting(data_lines, x_col)
                y_col_index = int(y_col) - 1
                
                if y_col_index < len(data_columns):
                    y_data = data_columns[y_col_index]
                    
                    # Apply series settings
                    color = series_settings.get('color', 'blue')
                    marker = series_settings.get('marker', 'o')
                    plot_type = series_settings.get('type', 'Line')
                    
                    if plot_type == "Line":
                        self.graph_manager.plot_line(x_data, y_data, color=color, marker=marker)
                    else:
                        self.graph_manager.plot_scatter(x_data, y_data, color=color, marker=marker)
                        
                    series_plotted += 1
                    
            except (ValueError, IndexError):
                continue
                
        # Set labels and update
        self.graph_manager.set_labels(
            title="Time Series",
            xlabel=f"Column {x_col}",
            ylabel="Values"
        )
        self.graph_manager.update()
    
    def _plot_stacked_chart(self, x_data, data_lines, x_col, settings):
        """Plot stacked area chart."""
        self.graph_manager.clear()
        
        # Collect enabled series
        series_data = []
        series_labels = []
        
        for i in range(5):
            series_settings = settings.get(f'series_{i}', {})
            if not series_settings.get('enabled', False):
                continue
                
            y_col = series_settings.get('column', '')
            if not y_col:
                continue
                
            try:
                _, data_columns = DataParser.parse_data_for_plotting(data_lines, x_col)
                y_col_index = int(y_col) - 1
                
                if y_col_index < len(data_columns):
                    y_data = data_columns[y_col_index]
                    series_data.append(y_data)
                    series_labels.append(f"Series {y_col}")
                    
            except (ValueError, IndexError):
                continue
        
        if not series_data:
            return
            
        # Create stacked areas using pure Python
        self._create_stacked_areas(x_data, series_data, series_labels, settings)
        
        # Set labels and update
        self.graph_manager.set_labels(
            title="Stacked Area",
            xlabel=f"Column {x_col}",
            ylabel="Values"
        )
        self.graph_manager.update()
    
    def _create_stacked_areas(self, x_data, series_data, series_labels, settings):
        """Create stacked areas using matplotlib."""
        if not series_data or not x_data:
            return
            
        # Prepare data for stacking
        stacked_data = []
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        # Calculate cumulative values for stacking
        cumulative = [0] * len(x_data)
        
        for i, y_data in enumerate(series_data):
            if len(y_data) != len(x_data):
                continue
                
            # Get color for this series
            color = colors[i % len(colors)]
            if i < 5:
                series_settings = settings.get(f'series_{i}', {})
                color = series_settings.get('color', color)
            
            # Create stacked area
            bottom_values = cumulative.copy()
            top_values = [bottom + val for bottom, val in zip(cumulative, y_data)]
            
            # Plot filled area
            self.graph_manager.ax.fill_between(
                x_data, bottom_values, top_values,
                alpha=0.7, color=color, label=series_labels[i]
            )
            
            # Update cumulative for next layer
            cumulative = top_values
        
        # Add legend
        self.graph_manager.ax.legend()
    
    def save_chart(self, filename=None):
        """Save the current chart."""
        from tkinter import filedialog
        from ..i18n import t
        
        if not filename:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title=t("ui.graph_tab.save_dialog_title")
            )
            
        if filename:
            try:
                self.graph_manager.figure.savefig(filename, dpi=300, bbox_inches='tight')
                return True
            except Exception as e:
                print(f"Error saving chart: {e}")
                return False
        return False
    
    def plot_chart(self, graph_manager, x_data, data_lines, x_col, chart_type, plot_settings, y_entries, data_tab):
        """Main chart plotting method."""
        from ..i18n import t
        
        start_time = time.time()
        
        try:
            if chart_type == "Stacked":
                self._plot_stacked_chart_new(graph_manager, x_data, data_lines, x_col, plot_settings, y_entries, data_tab)
            else:
                self._plot_time_series_chart_new(graph_manager, x_data, data_lines, x_col, plot_settings, y_entries, data_tab)
                
            # Update timing info
            self.last_render_time = time.time() - start_time
            if self.debug_refresh:
                print(f"Chart rendered in {self.last_render_time:.3f}s")
                
        except Exception as e:
            data_tab.add_message(t("ui.graph_tab.graph_error").format(error=e))

    def _plot_time_series_chart_new(self, graph_manager, x_data, data_lines, x_col, plot_settings, y_entries, data_tab):
        """Plot time series chart with new interface."""
        from ..i18n import t
        
        y_series_data = []
        settings_list = []
        has_data = False

        # Extract Y column data
        for i, y_entry in enumerate(y_entries):
            y_col_text = y_entry.get().strip()
            if y_col_text:
                try:
                    y_col = int(y_col_text) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            y_series_data.append((y_data, y_col_text))
                            
                            # Get series settings
                            series_settings = plot_settings.get('series', [])
                            if i < len(series_settings):
                                settings_list.append(series_settings[i])
                            else:
                                # Default settings
                                settings_list.append({
                                    'type': 'line',
                                    'color': 'blue',
                                    'marker': 'o'
                                })
                            has_data = True
                except ValueError:
                    data_tab.add_message(t("ui.graph_tab.invalid_column").format(column=y_col_text))

        if not has_data:
            data_tab.add_message(t("ui.graph_tab.no_valid_y_columns"))
            return

        # Clear and plot using available methods
        graph_manager.clear()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        
        # Plot each series
        for i, (y_data, label) in enumerate(y_series_data):
            color = colors[i % len(colors)]
            
            # Get series settings if available
            if i < len(settings_list):
                settings = settings_list[i]
                color = settings.get('color', color)
                plot_type = settings.get('type', 'line')
                marker = settings.get('marker', 'o')  # Should already be converted
            else:
                plot_type = 'line'
                marker = 'o'
            
            # Plot using available methods
            if plot_type == 'line':
                graph_manager.plot_line(x_data, y_data, color=color, marker=marker)
            else:
                graph_manager.plot_scatter(x_data, y_data, color=color, marker=marker)
        
        # Set labels
        graph_manager.set_labels(
            title="Time Series",
            xlabel=f"Column {x_col + 1}",
            ylabel="Values"
        )
        graph_manager.update()

    def _plot_stacked_chart_new(self, graph_manager, x_data, data_lines, x_col, plot_settings, y_entries, data_tab):
        """Plot stacked chart with new interface."""
        from ..i18n import t
        
        y_series_data = []
        has_data = False

        # Extract Y column data for stacking
        for y_entry in y_entries:
            y_col_text = y_entry.get().strip()
            if y_col_text:
                try:
                    y_col = int(y_col_text) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            # Ensure data length matches x_data
                            if len(y_data) == len(x_data):
                                y_series_data.append((y_data, y_col_text))
                                has_data = True
                except ValueError:
                    data_tab.add_message(t("ui.graph_tab.invalid_column").format(column=y_col_text))

        if not has_data:
            data_tab.add_message(t("ui.graph_tab.no_valid_y_columns"))
            return

        # Clear and create stacked chart manually
        graph_manager.clear()
        
        # Get normalize setting
        normalize_100 = plot_settings.get('normalize_100', False)
        
        # Create stacked areas using matplotlib directly
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        cumulative = [0.0] * len(x_data)
        
        # If normalizing to 100%, calculate totals first
        if normalize_100 and y_series_data:
            totals = [0.0] * len(x_data)
            for y_data, _ in y_series_data:
                for j, val in enumerate(y_data):
                    if j < len(totals):
                        totals[j] += val
        
        for i, (y_data, label) in enumerate(y_series_data):
            color = colors[i % len(colors)]
            
            # Normalize data if requested
            if normalize_100 and y_series_data:
                normalized_data = []
                for j, val in enumerate(y_data):
                    if j < len(totals) and totals[j] > 0:
                        normalized_data.append((val / totals[j]) * 100)
                    else:
                        normalized_data.append(0)
                y_data = normalized_data
            
            # Calculate this layer's top values
            top_values = [cum + val for cum, val in zip(cumulative, y_data)]
            
            # Plot filled area using matplotlib directly
            graph_manager.ax.fill_between(
                x_data, cumulative, top_values,
                alpha=0.7, color=color, label=f"Y{label}"
            )
            
            # Update cumulative for next layer
            cumulative = top_values
        
        # Set labels and show legend
        ylabel = "Percentage (%)" if normalize_100 else "Values"
        graph_manager.set_labels(
            title="Stacked Chart",
            xlabel=f"Column {x_col + 1}",
            ylabel=ylabel
        )
        graph_manager.ax.legend()
        graph_manager.update()
