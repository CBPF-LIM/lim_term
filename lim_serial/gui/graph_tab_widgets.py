"""
Graph tab widget management module.
Handles UI creation and widget-related functionality for the graph tab.
"""

import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN, MARKER_MAPPING
from ..i18n import t


class GraphTabWidgets:
    """Manages widget creation and UI layout for the graph tab."""

    def __init__(self, parent_frame, callbacks):
        self.frame = parent_frame
        self.callbacks = callbacks
        self.widgets = {}

    def create_main_widgets(self):
        """Create the main control widgets."""
        # Top row controls
        top_row = ttk.Frame(self.frame)
        top_row.grid(column=0, row=0, sticky="w", padx=10, pady=10)

        self.widgets['x_label'] = ttk.Label(top_row, text=t("ui.graph_tab.column_x"))
        self.widgets['x_label'].pack(side="left", padx=(0,5))

        self.widgets['x_column_entry'] = ttk.Entry(top_row, width=10)
        self.widgets['x_column_entry'].pack(side="left", padx=(0,15))
        self.widgets['x_column_entry'].insert(0, DEFAULT_X_COLUMN)
        self.widgets['x_column_entry'].bind("<KeyRelease>", self.callbacks.get('on_setting_change'))
        self.widgets['x_column_entry'].bind("<FocusOut>", self.callbacks.get('on_preference_changed'))

        self.widgets['plot_button'] = ttk.Button(top_row, text=t("ui.graph_tab.update_graph"),
                                               command=self.callbacks.get('plot_graph'))
        self.widgets['plot_button'].pack(side="left", padx=(0,10))

        self.widgets['pause_button'] = ttk.Button(top_row, text=t("ui.graph_tab.pause"),
                                                command=self.callbacks.get('toggle_pause'))
        self.widgets['pause_button'].pack(side="left", padx=(0,10))

        self.widgets['options_button'] = ttk.Button(top_row, text=t("ui.graph_tab.show_options"),
                                                  command=self.callbacks.get('toggle_options'))
        self.widgets['options_button'].pack(side="left", padx=(0,10))

        self.widgets['save_button'] = ttk.Button(top_row, text=t("ui.graph_tab.save_png"),
                                               command=self.callbacks.get('save_chart'))
        self.widgets['save_button'].pack(side="left", padx=(0,10))

        return self.widgets

    def create_y_column_widgets(self):
        """Create the Y column entry widgets."""
        self.widgets['y_columns_frame'] = ttk.LabelFrame(self.frame, text=t("ui.graph_tab.y_columns"))
        self.widgets['y_columns_frame'].grid(column=0, row=1, columnspan=4, padx=10, pady=5, sticky="ew")

        self.widgets['y_entries'] = []
        for i in range(1, 6):
            y_frame = ttk.Frame(self.widgets['y_columns_frame'])
            y_frame.grid(column=i-1, row=0, padx=5, pady=5, sticky="w")

            y_label = ttk.Label(y_frame, text=t(f"ui.graph_tab.column_y{i}"))
            y_label.pack(side="top")
            y_entry = ttk.Entry(y_frame, width=8)
            y_entry.pack(side="top")
            y_entry.bind("<KeyRelease>", self.callbacks.get('on_setting_change'))
            y_entry.bind("<FocusOut>", self.callbacks.get('on_preference_changed'))
            self.widgets['y_entries'].append(y_entry)

    def create_options_widgets(self):
        """Create the options widgets."""
        self.widgets['options_frame'] = ttk.LabelFrame(self.frame, text=t("ui.graph_tab.options_frame"))

        # Global frame
        global_frame = ttk.LabelFrame(self.widgets['options_frame'], text=t("ui.graph_tab.global_settings"))
        global_frame.grid(column=0, row=0, columnspan=6, padx=5, pady=5, sticky="ew")

        # Group label and combobox
        group_label = ttk.Label(global_frame, text=t("ui.graph_tab.visualization_group_label"))
        group_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        self.widgets['group_combobox'] = ttk.Combobox(global_frame, state="readonly", width=15,
                                                    values=["Time Series", "Stacked"])
        self.widgets['group_combobox'].grid(column=1, row=0, padx=5, pady=5, sticky="w")
        self.widgets['group_combobox'].set("Time Series")
        self.widgets['group_combobox'].bind("<<ComboboxSelected>>", self.callbacks.get('on_group_change'))

        # Data window label and entry
        data_window_label = ttk.Label(global_frame, text=t("ui.graph_tab.window_label"))
        data_window_label.grid(column=2, row=0, padx=5, pady=5, sticky="w")

        self.widgets['data_window_entry'] = ttk.Entry(global_frame, width=10)
        self.widgets['data_window_entry'].grid(column=3, row=0, padx=5, pady=5, sticky="w")
        self.widgets['data_window_entry'].insert(0, "50")
        self.widgets['data_window_entry'].bind("<KeyRelease>", self.callbacks.get('on_setting_change'))
        self.widgets['data_window_entry'].bind("<FocusOut>", self.callbacks.get('on_preference_changed'))

        # FPS controls
        fps_label = ttk.Label(global_frame, text=t("ui.graph_tab.refresh_rate_label"))
        fps_label.grid(column=4, row=0, padx=5, pady=5, sticky="w")

        fps_frame = ttk.Frame(global_frame)
        fps_frame.grid(column=5, row=0, padx=5, pady=5, sticky="w")

        self.widgets['fps_combobox'] = ttk.Combobox(fps_frame, state="readonly",
                                                  values=["1", "5", "10", "15", "20", "30"], width=5)
        self.widgets['fps_combobox'].pack(side="left")
        self.widgets['fps_combobox'].set("30")
        self.widgets['fps_combobox'].bind("<<ComboboxSelected>>", self.callbacks.get('on_fps_change'))

        self.widgets['fps_debug_label'] = ttk.Label(fps_frame, text="(33ms)", font=("TkDefaultFont", 8))
        self.widgets['fps_debug_label'].pack(side="left", padx=(5,0))

        # Min/Max Y controls
        min_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.min_y_label"))
        min_y_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.widgets['min_y_entry'] = ttk.Entry(global_frame, width=12)
        self.widgets['min_y_entry'].grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.widgets['min_y_entry'].bind("<KeyRelease>", self.callbacks.get('on_setting_change'))
        self.widgets['min_y_entry'].bind("<FocusOut>", self.callbacks.get('on_preference_changed'))

        max_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.max_y_label"))
        max_y_label.grid(column=2, row=1, padx=5, pady=5, sticky="w")
        self.widgets['max_y_entry'] = ttk.Entry(global_frame, width=12)
        self.widgets['max_y_entry'].grid(column=3, row=1, padx=5, pady=5, sticky="w")
        self.widgets['max_y_entry'].bind("<KeyRelease>", self.callbacks.get('on_setting_change'))
        self.widgets['max_y_entry'].bind("<FocusOut>", self.callbacks.get('on_preference_changed'))

        # Color configuration
        colors_label = ttk.Label(global_frame, text=t("ui.graph_tab.color_label"))
        colors_label.grid(column=0, row=2, padx=5, pady=5, sticky="w")

        self.widgets['y_color_combos'] = []
        default_colors = [t("ui.colors.blue"), t("ui.colors.red"), t("ui.colors.green"),
                         t("ui.colors.orange"), t("ui.colors.magenta")]

        colors_frame = ttk.Frame(global_frame)
        colors_frame.grid(column=1, row=2, columnspan=3, padx=5, pady=5, sticky="w")

        from .graph_tab_settings import GraphTabSettings
        settings_helper = GraphTabSettings()
        
        # Use only existing color translations
        available_colors = settings_helper.get_translated_colors()

        for i in range(5):
            y_frame = ttk.Frame(colors_frame)
            y_frame.grid(column=i, row=0, padx=2, pady=2)

            ttk.Label(y_frame, text=f"Y{i+1}").pack()
            color_combo = ttk.Combobox(y_frame, state="readonly", values=available_colors, width=8)
            color_combo.pack()
            color_combo.set(default_colors[i])
            color_combo.bind("<<ComboboxSelected>>", lambda e, idx=i: self.callbacks.get('on_color_setting_change')(idx))
            self.widgets['y_color_combos'].append(color_combo)

        # Series configuration
        self.widgets['series_config_frame'] = ttk.LabelFrame(self.widgets['options_frame'], text=t("ui.graph_tab.series_settings"))
        self.widgets['series_config_frame'].grid(column=0, row=1, columnspan=6, padx=5, pady=5, sticky="ew")

        # Series widgets
        self.widgets['series_widgets'] = []
        for i in range(5):
            series_widget = self.create_series_widgets(self.widgets['series_config_frame'], i+1, f"Serie {i+1}", i)
            self.widgets['series_widgets'].append(series_widget)

    def create_series_widgets(self, parent, row, label, index):
        """Create widgets for a single series configuration."""
        series_frame = ttk.Frame(parent)
        series_frame.grid(column=0, row=row, sticky="ew", padx=5, pady=2, columnspan=5)

        # Column label and entry
        ttk.Label(series_frame, text=label, width=12).grid(column=0, row=0, sticky="w", padx=(0,5))

        column_entry = ttk.Entry(series_frame, width=8)
        column_entry.grid(column=1, row=0, padx=(0,10))
        column_entry.bind("<KeyRelease>", lambda e, idx=index: self.callbacks.get('on_series_setting_change')(idx))

        # Type combobox
        type_combo = ttk.Combobox(series_frame, state="readonly", width=10)
        type_combo.grid(column=2, row=0, padx=(0,10))
        type_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self.callbacks.get('on_series_setting_change')(idx))

        # Color combobox
        color_combo = ttk.Combobox(series_frame, state="readonly", width=10)
        color_combo.grid(column=3, row=0, padx=(0,10))
        color_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self.callbacks.get('on_series_setting_change')(idx))

        # Marker combobox
        marker_combo = ttk.Combobox(series_frame, state="readonly", width=8)
        marker_combo.grid(column=4, row=0, padx=(0,10))
        marker_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self.callbacks.get('on_series_setting_change')(idx))

        return {
            'frame': series_frame,
            'column_entry': column_entry,
            'type': type_combo,
            'color': color_combo,
            'marker': marker_combo
        }

    def hide_options(self):
        """Hide the options frame."""
        if 'options_frame' in self.widgets:
            self.widgets['options_frame'].grid_remove()

    def show_options(self):
        """Show the options frame."""
        if 'options_frame' in self.widgets:
            self.widgets['options_frame'].grid()

    def get_widget(self, name):
        """Get a widget by name."""
        return self.widgets.get(name)

    def set_widget_text(self, name, text):
        """Set text for a widget."""
        widget = self.widgets.get(name)
        if widget and hasattr(widget, 'config'):
            widget.config(text=text)

    def get_widget_references(self):
        """Get references to all widgets for backward compatibility."""
        return {
            'x_column_entry': self.widgets.get('x_column_entry'),
            'y_entries': self.widgets.get('y_entries', []),
            'plot_button': self.widgets.get('plot_button'),
            'pause_button': self.widgets.get('pause_button'),
            'options_button': self.widgets.get('options_button'),
            'save_button': self.widgets.get('save_button'),
            'options_frame': self.widgets.get('options_frame'),
            'data_window_entry': self.widgets.get('data_window_entry'),
            'group_combobox': self.widgets.get('group_combobox'),
            'series_widgets': self.widgets.get('series_widgets', []),
            'min_y_entry': self.widgets.get('min_y_entry'),
            'max_y_entry': self.widgets.get('max_y_entry'),
            'fps_combobox': self.widgets.get('fps_combobox'),
            'fps_debug_label': self.widgets.get('fps_debug_label'),
            'y_color_combos': self.widgets.get('y_color_combos', []),
            'series_config_frame': self.widgets.get('series_config_frame')
        }
