import tkinter as tk
from tkinter import ttk
from ..core import GraphManager
from ..utils import DataParser
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN, MARKER_MAPPING
from ..i18n import t, get_config_manager
from .graph_tab_widgets import GraphTabWidgets
from .graph_tab_settings import GraphTabSettings
from .graph_tab_plotter import GraphTabPlotter


class GraphTab:


    def __init__(self, parent, data_tab, open_options_callback):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.graph_settings = {}
        self.options_visible = False
        self.is_paused = False
        self.config_manager = get_config_manager()

        # Refresh rate and timing
        self.refresh_rate_ms = 33
        self.refresh_timer_id = None
        self.refresh_counter = 0
        self.debug_refresh = False
        self.last_render_time = 0

        # Initialize modular components
        self._init_callbacks()
        self.widgets_manager = GraphTabWidgets(self.frame, self.callbacks)
        self.settings_manager = GraphTabSettings(self.config_manager)

        # Create UI first to have graph_manager available
        self._create_widgets()

        # Initialize plotter after graph_manager is created
        self.plotter = GraphTabPlotter(self.graph_manager, self.data_tab)

        # Load settings
        self._load_preferences()

    def _init_callbacks(self):
        """Initialize callback dictionary for widget interactions."""
        self.callbacks = {
            'on_setting_change': self._on_setting_change,
            'plot_graph': self.plot_graph,
            'toggle_pause': self._toggle_pause,
            'toggle_options': self._toggle_options,
            'save_chart': self._save_chart,
            'on_series_setting_change': self._on_series_setting_change,
            'on_group_change': self._on_group_change,
            'on_fps_change': self._on_fps_change,
            'on_color_setting_change': self._on_color_setting_change
        }

    def _create_widgets(self):
        """Create all widgets using the widgets manager."""
        # Create main control widgets
        self.widgets_manager.create_main_widgets()

        # Create Y column entries
        self.widgets_manager.create_y_column_widgets()

        # Create options widgets
        self.widgets_manager.create_options_widgets()

        # Create graph manager
        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(column=0, row=4, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)

        # Get widget references for backward compatibility
        widgets = self.widgets_manager.get_widget_references()
        self.x_column_entry = widgets['x_column_entry']
        self.y_entries = widgets['y_entries']
        self.plot_button = widgets['plot_button']
        self.pause_button = widgets['pause_button']
        self.options_button = widgets['options_button']
        self.save_button = widgets['save_button']
        self.options_frame = widgets['options_frame']
        self.data_window_entry = widgets['data_window_entry']
        self.group_combobox = widgets['group_combobox']
        self.series_widgets = widgets['series_widgets']
        self.min_y_entry = widgets['min_y_entry']
        self.max_y_entry = widgets['max_y_entry']
        self.fps_combobox = widgets['fps_combobox']
        self.fps_debug_label = widgets['fps_debug_label']
        self.y_color_combos = widgets['y_color_combos']
        self.series_config_frame = widgets['series_config_frame']

    def _toggle_options(self):
        """Toggle the visibility of options frame using widgets manager."""
        if self.options_visible:
            self.widgets_manager.hide_options()
            self.widgets_manager.set_widget_text('options_button', t("ui.graph_tab.show_options"))
            self.options_visible = False
        else:
            self.widgets_manager.show_options()
            self.options_frame.grid(column=0, row=2, columnspan=4, padx=10, pady=10, sticky="ew")
            self.widgets_manager.set_widget_text('options_button', t("ui.graph_tab.hide_options"))
            self.options_visible = True

    def _on_series_setting_change(self, series_index):

        self._save_preferences()
        self._on_setting_change()

    def _toggle_pause(self):

        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text=t("ui.graph_tab.resume"))
        else:
            self.pause_button.config(text=t("ui.graph_tab.pause"))

    def _save_chart(self):

        from tkinter import filedialog
        import matplotlib.pyplot as plt
        import io



        fig_copy = plt.figure(figsize=self.graph_manager.figure.get_size_inches(),
                             dpi=self.graph_manager.figure.dpi)


        ax_original = self.graph_manager.ax
        ax_copy = fig_copy.add_subplot(111)


        for line in ax_original.get_lines():
            ax_copy.plot(line.get_xdata(), line.get_ydata(),
                        color=line.get_color(), marker=line.get_marker(),
                        linestyle=line.get_linestyle(), linewidth=line.get_linewidth(),
                        markersize=line.get_markersize())


        ax_copy.set_xlim(ax_original.get_xlim())
        ax_copy.set_ylim(ax_original.get_ylim())
        ax_copy.set_xlabel(ax_original.get_xlabel())
        ax_copy.set_ylabel(ax_original.get_ylabel())
        ax_copy.set_title(ax_original.get_title())
        ax_copy.grid(ax_original.get_xgridlines() or ax_original.get_ygridlines())


        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title=t("ui.graph_tab.save_dialog_title")
        )

        if file_path:
            try:

                fig_copy.savefig(file_path, dpi=300, bbox_inches='tight')
                self.data_tab.add_message(t("ui.graph_tab.graph_saved").format(path=file_path))
            except Exception as e:
                self.data_tab.add_message(t("ui.data_tab.error_saving").format(error=e))
            finally:

                plt.close(fig_copy)

    def _on_setting_change(self, event=None):


        pass

    def plot_graph(self):
        """Plot graph using the plotter module."""
        try:
            # Validate widgets exist
            if not hasattr(self, 'x_column_entry') or not self.x_column_entry.winfo_exists():
                return
            if not hasattr(self, 'data_window_entry') or not self.data_window_entry.winfo_exists():
                return
            if not hasattr(self, 'group_combobox') or not self.group_combobox.winfo_exists():
                return

            x_col = int(self.x_column_entry.get()) - 1
            if x_col < 0:
                raise ValueError(t("ui.graph_tab.positive_numbers"))

            data_lines = self.data_tab.get_data()
            if not data_lines:
                self.data_tab.add_message(t("ui.graph_tab.no_data_available"))
                return

            # Apply data window
            data_window = int(self.data_window_entry.get()) if self.data_window_entry.get() else 0
            if data_window > 0:
                data_lines = data_lines[-data_window:]

            # Extract x data
            x_data, _ = DataParser.extract_columns(data_lines, x_col, 0)
            if not x_data:
                self.data_tab.add_message(t("ui.graph_tab.could_not_extract_data"))
                return

            # Get chart type and plot
            group = self.group_combobox.get()
            plot_settings = self._collect_plot_settings()

            self.plotter.plot_chart(
                self.graph_manager,
                x_data,
                data_lines,
                x_col,
                group,
                plot_settings,
                self.y_entries,
                self.data_tab
            )

        except tk.TclError as e:
            pass
        except ValueError as e:
            self.data_tab.add_message(t("ui.graph_tab.parameter_error").format(error=e))
        except Exception as e:
            self.data_tab.add_message(t("ui.graph_tab.graph_error").format(error=e))

    def _collect_plot_settings(self):
        """Collect current plot settings from widgets."""
        settings = {}

        try:
            # Collect min/max Y settings if they exist
            if hasattr(self, 'min_y_entry') and self.min_y_entry.get():
                settings['min_y'] = float(self.min_y_entry.get())
            if hasattr(self, 'max_y_entry') and self.max_y_entry.get():
                settings['max_y'] = float(self.max_y_entry.get())

            # Collect normalize_100 setting for stacked charts
            if hasattr(self, 'normalize_100_var'):
                settings['normalize_100'] = self.normalize_100_var.get()

            # Collect series settings - only if widgets exist
            if hasattr(self, 'series_widgets') and self.series_widgets:
                settings['series'] = []
                for i, widget_set in enumerate(self.series_widgets):
                    if widget_set and isinstance(widget_set, dict):
                        # Convert translated values to original values for performance
                        marker_widget = widget_set.get('marker')
                        type_widget = widget_set.get('type')
                        
                        marker_value = 'o'  # default
                        if marker_widget and hasattr(marker_widget, 'get'):
                            try:
                                marker_text = marker_widget.get()
                                marker_value = self._get_original_marker(marker_text)
                            except:
                                pass
                                
                        type_value = 'line'  # default
                        if type_widget and hasattr(type_widget, 'get'):
                            try:
                                type_text = type_widget.get()
                                type_value = self._get_original_graph_type(type_text)
                            except:
                                pass
                        
                        # Get color from UI widget like in _get_stacked_color
                        color_value = 'blue'  # default
                        if i < len(self.y_color_combos):
                            try:
                                translated_color = self.y_color_combos[i].get()
                                color_value = self._get_original_color(translated_color)
                            except:
                                pass
                        
                        series_setting = {
                            'type': type_value,
                            'color': color_value,
                            'marker': marker_value
                        }
                        settings['series'].append(series_setting)
        except Exception as e:
            # If there's any error, return minimal settings
            print(f"Error collecting plot settings: {e}")
            settings = {'series': []}

        return settings

    def _get_series_settings(self, series_index):


        color = self._get_stacked_color(series_index)

        if series_index < len(self.series_widgets):
            widgets = self.series_widgets[series_index]


            if 'type' in widgets:

                return {
                    'type': self._get_original_graph_type(widgets['type'].get()),
                    'color': color,
                    'marker': self._get_original_marker(widgets['marker'].get())
                }
            else:

                return {
                    'type': 'line',
                    'color': color,
                    'marker': 'o'
                }


        return {
            'type': 'line',
            'color': color,
            'marker': 'o'
        }

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
            translated_marker = self.settings_manager.get_translated_marker_from_original(settings["dot_type"])
            self.dot_type_combobox.set(translated_marker)

        if self.data_tab.get_data() and not self.is_paused:
            self.plot_graph()

    def _load_preferences(self):
        """Load preferences using the settings manager."""
        self.graph_settings = self.settings_manager.load_preferences()

        # Apply settings to widgets
        x_col = self.graph_settings.get('x_column', DEFAULT_X_COLUMN)
        self.x_column_entry.delete(0, "end")
        self.x_column_entry.insert(0, str(x_col))

        # Set other widget values from loaded preferences
        group = self.graph_settings.get('chart_type', 'Time Series')
        if hasattr(self, 'group_combobox'):
            self.group_combobox.set(group)

        # Load Y column settings
        for i in range(1, 6):
            series_settings = self.graph_settings.get(f'series_{i-1}', {})
            y_col = series_settings.get('column', '')
            entry = self.y_entries[i-1]
            entry.delete(0, "end")
            entry.insert(0, str(y_col))


        window_size = self.config_manager.load_tab_setting('graph.general', 'window_size', '50')
        self.data_window_entry.delete(0, "end")
        self.data_window_entry.insert(0, str(window_size))


        refresh_rate = self.graph_settings.get('refresh_rate', '30')
        self.fps_combobox.set(str(refresh_rate))
        self._set_refresh_rate(int(refresh_rate))


        if hasattr(self, 'fps_debug_label'):
            self.fps_debug_label.config(text=f"({self.refresh_rate_ms}ms)")

        min_y = self.config_manager.load_tab_setting('graph.general', 'min_y', '')
        max_y = self.config_manager.load_tab_setting('graph.general', 'max_y', '')
        if min_y:
            self.min_y_entry.delete(0, "end")
            self.min_y_entry.insert(0, str(min_y))
        if max_y:
            self.max_y_entry.delete(0, "end")
            self.max_y_entry.insert(0, str(max_y))


        default_colors = ['Blue', 'Red', 'Green', 'Orange', 'Magenta']
        for i in range(5):
            if i < len(self.y_color_combos):
                default_color = default_colors[i] if i < len(default_colors) else 'Blue'
                color = self.config_manager.load_tab_setting('graph.general', f'y{i+1}_color', default_color)

                color_translation_map = {
                    'Blue': t("ui.colors.blue"), 'Cyan': t("ui.colors.cyan"), 'Teal': t("ui.colors.teal"),
                    'Green': t("ui.colors.green"), 'Lime': t("ui.colors.lime"), 'Yellow': t("ui.colors.yellow"),
                    'Amber': t("ui.colors.amber"), 'Orange': t("ui.colors.orange"), 'Red': t("ui.colors.red"),
                    'Magenta': t("ui.colors.magenta"), 'Indigo': t("ui.colors.indigo"), 'Violet': t("ui.colors.violet"),
                    'Turquoise': t("ui.colors.turquoise"), 'Aquamarine': t("ui.colors.aquamarine"),
                    'Springgreen': t("ui.colors.springgreen"), 'Chartreuse': t("ui.colors.chartreuse"),
                    'Gold': t("ui.colors.gold"), 'Coral': t("ui.colors.coral"), 'Crimson': t("ui.colors.crimson"),
                    'Pink': t("ui.colors.pink")
                }
                if color in color_translation_map:
                    self.y_color_combos[i].set(color_translation_map[color])

        # Load group preferences
        group = self.graph_settings.get('chart_type', 'Time Series')
        if hasattr(self, 'group_combobox'):
            self.group_combobox.set(group)
        
        # Create dynamic series widgets for the current group
        self._create_series_widgets()
        
        # Load group-specific preferences
        self._load_group_preferences(group)

    def _save_preferences(self):
        """Save preferences using the settings manager."""
        try:
            # Collect current settings from widgets
            current_settings = {}
            
            # Main settings
            try:
                current_settings['x_column'] = self.x_column_entry.get()
            except tk.TclError:
                pass
                
            try:
                current_settings['chart_type'] = self.group_combobox.get()
            except tk.TclError:
                pass
                
            try:
                current_settings['refresh_rate'] = self.fps_combobox.get()
            except tk.TclError:
                pass
                
            # Y column settings
            for i in range(5):
                try:
                    entry = self.y_entries[i]
                    current_settings[f'series_{i}'] = {
                        'column': entry.get(),
                        'type': 'Line',
                        'color': 'blue',
                        'marker': 'o',
                        'enabled': bool(entry.get().strip())
                    }
                except (tk.TclError, IndexError):
                    pass
                    
            # Save using settings manager
            self.settings_manager.save_preferences(current_settings)
            
        except Exception as e:
            print(f"Error saving preferences: {e}")

    def _on_group_change(self, event=None):
        # Recreate series widgets based on chart type
        self._create_series_widgets()
        
        # Load preferences for the new group
        group = self.group_combobox.get()
        self._load_group_preferences(group)
        
        self._save_preferences()
        self._on_setting_change()

    def _create_series_widgets(self):
        """Create dynamic series widgets based on chart type."""
        # Clear existing widgets
        for widget in self.series_config_frame.winfo_children():
            widget.destroy()

        group = self.group_combobox.get()

        if group == "Time Series":
            self._create_time_series_widgets()
        elif group == "Stacked":
            self._create_stacked_widgets()

    def _create_time_series_widgets(self):
        """Create time series specific widgets."""
        self.series_config_frame.config(text=t("ui.graph_tab.time_series_settings"))

        # Headers
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.series_label")).grid(column=0, row=0, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.type_label")).grid(column=1, row=0, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.point_label")).grid(column=2, row=0, padx=5, pady=5)

        # Create series widgets
        self.series_widgets = []
        for i in range(1, 6):
            self._create_time_series_row(self.series_config_frame, i, f"Y{i}", i-1)

    def _create_time_series_row(self, parent, row, label, index):
        """Create a single time series configuration row."""
        ttk.Label(parent, text=label).grid(column=0, row=row, padx=5, pady=2)

        # Type combobox
        type_combo = ttk.Combobox(parent, state="readonly", values=self._get_translated_graph_types(), width=10)
        type_combo.grid(column=1, row=row, padx=5, pady=2)
        type_combo.set(t("ui.graph_types.line"))
        type_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self._on_series_setting_change(idx))

        # Marker combobox
        marker_combo = ttk.Combobox(parent, state="readonly", values=self._get_translated_markers(), width=10)
        marker_combo.grid(column=2, row=row, padx=5, pady=2)
        marker_combo.set(t("ui.markers.circle"))
        marker_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self._on_series_setting_change(idx))

        self.series_widgets.append({
            'type': type_combo,
            'marker': marker_combo
        })

    def _create_stacked_widgets(self):
        """Create stacked chart specific widgets."""
        self.series_config_frame.config(text="Stack Settings")

        # Normalize 100% checkbox
        self.normalize_100_var = tk.BooleanVar()
        self.normalize_100_checkbox = ttk.Checkbutton(
            self.series_config_frame,
            text="Normalizar para 100%",
            variable=self.normalize_100_var
        )
        self.normalize_100_checkbox.grid(column=0, row=0, columnspan=4, padx=5, pady=10)
        self.normalize_100_checkbox.bind("<Button-1>", lambda e: self.series_config_frame.after_idle(self._on_setting_change))

        # Empty series widgets for stacked mode
        self.series_widgets = []

    def _load_group_preferences(self, group):
        """Load preferences specific to the chart group."""
        if group == "Time Series":
            self._load_time_series_preferences()
        elif group == "Stacked":
            self._load_stacked_preferences()

    def _load_time_series_preferences(self):
        """Load time series specific preferences."""
        for i in range(5):
            if i < len(self.series_widgets) and 'type' in self.series_widgets[i]:
                widgets = self.series_widgets[i]
                series_id = f'y{i+1}'

                # Load graph type
                graph_type = self.config_manager.load_tab_setting('graph.group.ts', f'{series_id}_type', 'Line')
                type_translation_map = {
                    'Line': t("ui.graph_types.line"),
                    'Scatter': t("ui.graph_types.scatter")
                }
                if graph_type in type_translation_map:
                    widgets['type'].set(type_translation_map[graph_type])

                # Load marker
                marker = self.config_manager.load_tab_setting('graph.group.ts', f'{series_id}_marker', 'circle')
                marker_translation_map = {
                    'circle': t("ui.markers.circle"), 'square': t("ui.markers.square"), 'triangle': t("ui.markers.triangle"),
                    'diamond': t("ui.markers.diamond"), 'star': t("ui.markers.star"), 'plus': t("ui.markers.plus"),
                    'x': t("ui.markers.x"), 'vline': t("ui.markers.vline"), 'hline': t("ui.markers.hline"),
                    'hexagon': t("ui.markers.hexagon")
                }
                if marker in marker_translation_map:
                    widgets['marker'].set(marker_translation_map[marker])

    def _load_stacked_preferences(self):
        """Load stacked chart specific preferences."""
        if hasattr(self, 'normalize_100_var'):
            normalize_100 = self.config_manager.load_tab_setting('graph.group.stacked', 'normalize_100', False)
            self.normalize_100_var.set(normalize_100)

    def _get_stacked_color(self, series_index):

        if series_index < len(self.y_color_combos):
            translated_color = self.y_color_combos[series_index].get()
            return self._get_original_color(translated_color)


        default_colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#ff00ff"]
        return default_colors[series_index % len(default_colors)]

    def get_frame(self):

        return self.frame

    def _on_color_setting_change(self, color_index):

        self._save_preferences()
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
                        print(f"Chart refresh #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Fixed Rate")


                    self.plot_graph()
                else:

                    pass
            else:

                pass

        except Exception as e:

            if self.debug_refresh:
                print(f"Chart refresh error: {e}")
        finally:

            if hasattr(self, 'frame') and self.frame.winfo_exists():
                self.refresh_timer_id = self.frame.after(self.refresh_rate_ms, self._refresh_chart)

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

        try:
            fps = int(self.fps_combobox.get())
            self._set_refresh_rate(fps)


            self.fps_debug_label.config(text=f"({self.refresh_rate_ms}ms)")


            import time
            self.last_render_time = time.time()
            self.refresh_counter = 0

            self._save_preferences()
        except ValueError:

            pass

    def should_render_now(self, current_time):

        if self.is_paused:
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
                    print(f"Render frame #{self.refresh_counter}: {fps_actual:.1f} FPS ({self.refresh_rate_ms}ms) - Game Loop Style")


                self.plot_graph()


            self.last_render_time = time.time()

        except Exception as e:

            if self.debug_refresh:
                print(f"Render frame error: {e}")

            self.last_render_time = time.time()

    def _get_translated_graph_types(self):
        """Get list of translated graph type options."""
        return self.settings_manager.get_translated_graph_types()

    def _get_translated_colors(self):
        """Get list of translated color options."""
        return self.settings_manager.get_translated_colors()

    def _get_translated_markers(self):
        """Get list of translated marker options."""
        return self.settings_manager.get_translated_markers()

    def _get_original_marker(self, translated_marker):
        """Convert translated marker back to original marker symbol."""
        return self.settings_manager.get_original_marker(translated_marker)

    def _get_translated_marker_from_original(self, original_marker):
        """Convert original marker symbol to translated marker."""
        return self.settings_manager.get_translated_marker_from_original(original_marker)

    def _get_original_graph_type(self, translated_type):
        """Convert translated graph type back to original type."""
        return self.settings_manager.get_original_graph_type(translated_type)

    def _get_original_color(self, translated_color):
        """Convert translated color back to original color."""
        return self.settings_manager.get_original_color(translated_color)
