"""
Tab de visualização de gráficos
"""
import tkinter as tk
from tkinter import ttk
from ..core import GraphManager
from ..utils import DataParser
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN, GRAPH_TYPES, AVAILABLE_COLORS, MARKER_TYPES
from ..i18n import t, get_config_manager


class GraphTab:
    """Tab de gráficos"""

    def __init__(self, parent, data_tab, open_options_callback):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.graph_settings = {}
        self.options_visible = False
        self.is_paused = False
        self.config_manager = get_config_manager()

        self._create_widgets()
        self._load_preferences()

    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Primeira linha: Coluna X e botões
        top_row = ttk.Frame(self.frame)
        top_row.grid(column=0, row=0, sticky="w", padx=10, pady=10)

        self.x_label = ttk.Label(top_row, text=t("ui.graph_tab.column_x"))
        self.x_label.pack(side="left", padx=(0,5))
        self.x_column_entry = ttk.Entry(top_row, width=10)
        self.x_column_entry.pack(side="left", padx=(0,15))
        self.x_column_entry.insert(0, DEFAULT_X_COLUMN)
        self.x_column_entry.bind("<KeyRelease>", self._on_setting_change)
        self.x_column_entry.bind("<FocusOut>", self._on_preference_changed)

        self.plot_button = ttk.Button(top_row, text=t("ui.graph_tab.update_graph"), command=self.plot_graph)
        self.plot_button.pack(side="left", padx=(0,10))

        self.pause_button = ttk.Button(top_row, text=t("ui.graph_tab.pause"), command=self._toggle_pause)
        self.pause_button.pack(side="left", padx=(0,10))

        self.options_button = ttk.Button(top_row, text=t("ui.graph_tab.show_options"), command=self._toggle_options)
        self.options_button.pack(side="left", padx=(0,10))

        self.save_button = ttk.Button(top_row, text=t("ui.graph_tab.save_png"), command=self._save_chart)
        self.save_button.pack(side="left", padx=(0,10))

        # Segunda linha: Colunas Y (Y1-Y5 only)
        self.y_columns_frame = ttk.LabelFrame(self.frame, text=t("ui.graph_tab.y_columns"))
        self.y_columns_frame.grid(column=0, row=1, columnspan=4, padx=10, pady=5, sticky="ew")

        # Y1-Y5 columns only
        self.y_entries = []
        for i in range(1, 6):  # Y1 to Y5
            y_frame = ttk.Frame(self.y_columns_frame)
            y_frame.grid(column=i-1, row=0, padx=5, pady=5, sticky="w")

            y_label = ttk.Label(y_frame, text=t(f"ui.graph_tab.column_y{i}"))
            y_label.pack(side="top")
            y_entry = ttk.Entry(y_frame, width=8)
            y_entry.pack(side="top")
            y_entry.bind("<KeyRelease>", self._on_setting_change)
            y_entry.bind("<FocusOut>", self._on_preference_changed)
            self.y_entries.append(y_entry)

        # Frame para opções (inicialmente oculto)
        self.options_frame = ttk.LabelFrame(self.frame, text=t("ui.graph_tab.options_frame"))
        self._create_options_widgets()

        # Área do gráfico
        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(column=0, row=4, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Configura expansão
        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)

    def _create_options_widgets(self):
        """Cria os widgets de opções com configuração por série Y"""
        # Global settings row
        global_frame = ttk.LabelFrame(self.options_frame, text="Global Settings")
        global_frame.grid(column=0, row=0, columnspan=6, padx=5, pady=5, sticky="ew")

        # Visualization group selection
        self.group_label = ttk.Label(global_frame, text="Grupo de Visualização:")
        self.group_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.group_combobox = ttk.Combobox(global_frame, state="readonly", values=["Time Series", "Stacked"], width=15)
        self.group_combobox.grid(column=1, row=0, padx=5, pady=5, sticky="w")
        self.group_combobox.set("Time Series")
        self.group_combobox.bind("<<ComboboxSelected>>", self._on_group_change)

        # Window size
        self.window_label = ttk.Label(global_frame, text=t("ui.graph_tab.window_label"))
        self.window_label.grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.data_window_entry = ttk.Entry(global_frame, width=12)
        self.data_window_entry.grid(column=3, row=0, padx=5, pady=5, sticky="w")
        self.data_window_entry.insert(0, "50")
        self.data_window_entry.bind("<KeyRelease>", self._on_setting_change)
        self.data_window_entry.bind("<FocusOut>", self._on_preference_changed)

        # Min and Max Y (global for all series) - second row
        self.min_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.min_y_label"))
        self.min_y_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.min_y_entry = ttk.Entry(global_frame, width=12)
        self.min_y_entry.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.min_y_entry.bind("<KeyRelease>", self._on_setting_change)
        self.min_y_entry.bind("<FocusOut>", self._on_preference_changed)

        self.max_y_label = ttk.Label(global_frame, text=t("ui.graph_tab.max_y_label"))
        self.max_y_label.grid(column=2, row=1, padx=5, pady=5, sticky="w")
        self.max_y_entry = ttk.Entry(global_frame, width=12)
        self.max_y_entry.grid(column=3, row=1, padx=5, pady=5, sticky="w")
        self.max_y_entry.bind("<KeyRelease>", self._on_setting_change)
        self.max_y_entry.bind("<FocusOut>", self._on_preference_changed)

        # Series configuration frame (dynamic based on group)
        self.series_config_frame = ttk.LabelFrame(self.options_frame, text="Series Settings")
        self.series_config_frame.grid(column=0, row=1, columnspan=6, padx=5, pady=5, sticky="ew")

        self._create_series_widgets()

    def _create_series_row(self, parent, row, label, index):
        """Cria uma linha de configuração para uma série Y"""
        ttk.Label(parent, text=label).grid(column=0, row=row, padx=5, pady=2)

        # Graph type
        type_combo = ttk.Combobox(parent, state="readonly", values=self._get_translated_graph_types(), width=10)
        type_combo.grid(column=1, row=row, padx=5, pady=2)
        type_combo.set(t("ui.graph_types.line"))
        type_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self._on_series_setting_change(idx))

        # Color
        color_combo = ttk.Combobox(parent, state="readonly", values=self._get_translated_colors(), width=10)
        color_combo.grid(column=2, row=row, padx=5, pady=2)
        # Set different default colors for each series
        default_colors = [t("ui.colors.blue"), t("ui.colors.red"), t("ui.colors.green"),
                         t("ui.colors.orange"), t("ui.colors.magenta"), t("ui.colors.cyan")]
        color_combo.set(default_colors[index % len(default_colors)])
        color_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self._on_series_setting_change(idx))

        # Marker
        marker_combo = ttk.Combobox(parent, state="readonly", values=self._get_translated_markers(), width=10)
        marker_combo.grid(column=3, row=row, padx=5, pady=2)
        marker_combo.set(t("ui.markers.circle"))
        marker_combo.bind("<<ComboboxSelected>>", lambda e, idx=index: self._on_series_setting_change(idx))

        self.series_widgets.append({
            'type': type_combo,
            'color': color_combo,
            'marker': marker_combo
        })

    def _toggle_options(self):
        """Mostra/oculta opções"""
        if self.options_visible:
            self.options_frame.grid_remove()
            self.options_button.config(text=t("ui.graph_tab.show_options"))
            self.options_visible = False
        else:
            self.options_frame.grid(column=0, row=2, columnspan=4, padx=10, pady=10, sticky="ew")
            self.options_button.config(text=t("ui.graph_tab.hide_options"))
            self.options_visible = True

    def _on_series_setting_change(self, series_index):
        """Handle changes to series-specific settings"""
        self._save_preferences()
        self._on_setting_change()

    def _toggle_pause(self):
        """Pausa/resume a atualização do gráfico"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text=t("ui.graph_tab.resume"))
        else:
            self.pause_button.config(text=t("ui.graph_tab.pause"))

    def _save_chart(self):
        """Salva o gráfico atual como PNG"""
        from tkinter import filedialog
        import matplotlib.pyplot as plt
        import io

        # Captura o estado atual do gráfico ANTES de abrir o diálogo
        # Cria uma cópia da figura em memória
        fig_copy = plt.figure(figsize=self.graph_manager.figure.get_size_inches(),
                             dpi=self.graph_manager.figure.dpi)

        # Copia o conteúdo da figura atual para a nova figura
        ax_original = self.graph_manager.ax
        ax_copy = fig_copy.add_subplot(111)

        # Copia todos os elementos do plot
        for line in ax_original.get_lines():
            ax_copy.plot(line.get_xdata(), line.get_ydata(),
                        color=line.get_color(), marker=line.get_marker(),
                        linestyle=line.get_linestyle(), linewidth=line.get_linewidth(),
                        markersize=line.get_markersize())

        # Copia as configurações dos eixos
        ax_copy.set_xlim(ax_original.get_xlim())
        ax_copy.set_ylim(ax_original.get_ylim())
        ax_copy.set_xlabel(ax_original.get_xlabel())
        ax_copy.set_ylabel(ax_original.get_ylabel())
        ax_copy.set_title(ax_original.get_title())
        ax_copy.grid(ax_original.get_xgridlines() or ax_original.get_ygridlines())

        # AGORA abre o diálogo para salvar
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Salvar gráfico como PNG"
        )

        if file_path:
            try:
                # Salva a figura copiada (estado do momento 1)
                fig_copy.savefig(file_path, dpi=300, bbox_inches='tight')
                self.data_tab.add_message(t("ui.graph_tab.graph_saved").format(path=file_path))
            except Exception as e:
                self.data_tab.add_message(t("ui.data_tab.error_saving").format(error=e))
            finally:
                # Limpa a figura copiada da memória
                plt.close(fig_copy)

    def _on_setting_change(self, event=None):
        """Callback chamado quando qualquer configuração muda"""
        try:
            # Auto-update graph if not paused and has data
            if self.data_tab.get_data() and not self.is_paused:
                self.plot_graph()
        except (ValueError, KeyError):
            # Ignora erros durante digitação
            pass

    def plot_graph(self):
        """Gera o gráfico com múltiplas séries Y"""
        try:
            x_col = int(self.x_column_entry.get()) - 1

            if x_col < 0:
                raise ValueError(t("ui.graph_tab.positive_numbers"))

            data_lines = self.data_tab.get_data()
            if not data_lines:
                self.data_tab.add_message(t("ui.graph_tab.no_data_available"))
                return

            # Aplica janela de dados
            data_window = int(self.data_window_entry.get()) if self.data_window_entry.get() else 0
            if data_window > 0:
                data_lines = data_lines[-data_window:]

            # Extract X data
            x_data, _ = DataParser.extract_columns(data_lines, x_col, 0)  # Y doesn't matter here
            if not x_data:
                self.data_tab.add_message(t("ui.graph_tab.could_not_extract_data"))
                return

            # Get visualization group
            group = self.group_combobox.get()
            
            if group == "Stacked":
                self._plot_stacked_chart(x_data, data_lines, x_col)
            else:  # Time Series (default)
                self._plot_time_series_chart(x_data, data_lines, x_col)

        except ValueError as e:
            self.data_tab.add_message(t("ui.graph_tab.parameter_error").format(error=e))
        except Exception as e:
            self.data_tab.add_message(t("ui.graph_tab.graph_error").format(error=e))
    
    def _plot_time_series_chart(self, x_data, data_lines, x_col):
        """Plot Time Series chart (original behavior)"""
        # Collect all Y series data and settings
        y_series_data = []
        settings_list = []
        has_data = False

        # Process Y1-Y5 columns only
        for i, y_entry in enumerate(self.y_entries):
            y_col_str = y_entry.get().strip()
            if y_col_str:
                try:
                    y_col = int(y_col_str) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            y_series_data.append(y_data)
                            settings = self._get_series_settings(i)
                            settings['has_data'] = True
                            settings_list.append(settings)
                            has_data = True
                except ValueError:
                    pass

        if not has_data:
            self.data_tab.add_message(t("ui.graph_tab.no_data_available"))
            return

        # Generate translated labels
        title = t("ui.graph_tab.chart_title")
        xlabel = t("ui.graph_tab.chart_xlabel").format(column=x_col + 1)
        ylabel = t("ui.graph_tab.chart_ylabel").format(column="Multi")

        # Apply global Y limits to first settings
        if settings_list:
            min_y = self.min_y_entry.get().strip()
            max_y = self.max_y_entry.get().strip()
            settings_list[0]['min_y'] = min_y
            settings_list[0]['max_y'] = max_y

        self.graph_manager.plot_multi_series(x_data, y_series_data, settings_list, x_col, title, xlabel, ylabel)
    
    def _plot_stacked_chart(self, x_data, data_lines, x_col):
        """Plot Stacked chart"""
        # Collect all Y series data
        y_series_data = []
        colors = []
        has_data = False

        # Process Y1-Y5 columns only
        for i, y_entry in enumerate(self.y_entries):
            y_col_str = y_entry.get().strip()
            if y_col_str:
                try:
                    y_col = int(y_col_str) - 1
                    if y_col >= 0:
                        _, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
                        if y_data:
                            y_series_data.append(y_data)
                            # Get color from stacked settings
                            color = self._get_stacked_color(i)
                            colors.append(color)
                            has_data = True
                        else:
                            y_series_data.append([])  # Empty data but maintain order
                            colors.append("#cccccc")  # Gray for empty
                    else:
                        y_series_data.append([])
                        colors.append("#cccccc")
                except ValueError:
                    y_series_data.append([])
                    colors.append("#cccccc")
            else:
                y_series_data.append([])  # Empty data to maintain Y order
                colors.append("#cccccc")

        if not has_data:
            self.data_tab.add_message(t("ui.graph_tab.no_data_available"))
            return

        # Get 100% normalization setting
        normalize_100 = getattr(self, 'normalize_100_var', tk.BooleanVar()).get()

        # Generate labels
        title = "Stacked Chart"
        xlabel = t("ui.graph_tab.chart_xlabel").format(column=x_col + 1)
        ylabel = "Percentage (%)" if normalize_100 else "Value"

        self.graph_manager.plot_stacked_series(x_data, y_series_data, colors, normalize_100, title, xlabel, ylabel)

    def _get_series_settings(self, series_index):
        """Get settings for a specific Y series"""
        if series_index < len(self.series_widgets):
            widgets = self.series_widgets[series_index]
            
            # Check if this is Time Series (has 'type' widget) or Stacked (only 'color' widget)
            if 'type' in widgets:
                # Time Series configuration
                return {
                    'type': self._get_original_graph_type(widgets['type'].get()),
                    'color': self._get_original_color(widgets['color'].get()),
                    'marker': self._get_original_marker(widgets['marker'].get())
                }
            else:
                # Stacked configuration (only color)
                return {
                    'type': 'line',  # Default for stacked
                    'color': self._get_original_color(widgets['color'].get()),
                    'marker': 'o'  # Default marker
                }
        
        # Default settings
        return {
            'type': 'line',
            'color': '#1f77b4',
            'marker': 'o'
        }

    def update_graph_settings(self, settings):
        """Atualiza configurações do gráfico (compatibilidade)"""
        self.graph_settings.update(settings)
        # Atualiza os widgets com as novas configurações
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
            for label, value in MARKER_TYPES.items():
                if value == settings["dot_type"]:
                    self.dot_type_combobox.set(label)
                    break
        # Replot automaticamente se houver dados
        if self.data_tab.get_data() and not self.is_paused:
            self.plot_graph()

    def _get_translated_graph_types(self):
        """Retorna lista de tipos de gráfico traduzidos"""
        return [t("ui.graph_types.line"), t("ui.graph_types.scatter")]

    def _get_translated_colors(self):
        """Retorna lista de cores traduzidas"""
        color_keys = ["blue", "cyan", "teal", "green", "lime", "yellow", "amber", "orange",
                     "red", "magenta", "indigo", "violet", "turquoise", "aquamarine",
                     "springgreen", "chartreuse", "gold", "coral", "crimson", "pink"]
        return [t(f"ui.colors.{color}") for color in color_keys]

    def _get_translated_markers(self):
        """Retorna lista de marcadores traduzidos"""
        marker_keys = ["circle", "square", "triangle", "diamond", "star", "plus",
                      "x", "vline", "hline", "hexagon"]
        return [t(f"ui.markers.{marker}") for marker in marker_keys]

    def _get_original_marker(self, translated_marker):
        """Retorna o valor original do marcador a partir da tradução"""
        marker_mapping = {
            t("ui.markers.circle"): "o",
            t("ui.markers.square"): "s",
            t("ui.markers.triangle"): "^",
            t("ui.markers.diamond"): "D",
            t("ui.markers.star"): "*",
            t("ui.markers.plus"): "+",
            t("ui.markers.x"): "x",
            t("ui.markers.vline"): "|",
            t("ui.markers.hline"): "_",
            t("ui.markers.hexagon"): "h"
        }
        return marker_mapping.get(translated_marker, "o")

    def _get_original_graph_type(self, translated_type):
        """Retorna o valor original do tipo de gráfico a partir da tradução"""
        type_mapping = {
            t("ui.graph_types.line"): "line",
            t("ui.graph_types.scatter"): "scatter"
        }
        return type_mapping.get(translated_type, "line")

    def _get_original_color(self, translated_color):
        """Retorna o valor original da cor a partir da tradução"""
        color_mapping = {
            t("ui.colors.blue"): "#1f77b4",
            t("ui.colors.cyan"): "#17becf",
            t("ui.colors.teal"): "#008080",
            t("ui.colors.green"): "#2ca02c",
            t("ui.colors.lime"): "#32cd32",
            t("ui.colors.yellow"): "#ffff00",
            t("ui.colors.amber"): "#ffc000",
            t("ui.colors.orange"): "#ff7f0e",
            t("ui.colors.red"): "#d62728",
            t("ui.colors.magenta"): "#ff00ff",
            t("ui.colors.indigo"): "#4b0082",
            t("ui.colors.violet"): "#9467bd",
            t("ui.colors.turquoise"): "#40e0d0",
            t("ui.colors.aquamarine"): "#7fffd4",
            t("ui.colors.springgreen"): "#00ff7f",
            t("ui.colors.chartreuse"): "#7fff00",
            t("ui.colors.gold"): "#ffd700",
            t("ui.colors.coral"): "#ff7f50",
            t("ui.colors.crimson"): "#dc143c",
            t("ui.colors.pink"): "#ffc0cb"
        }
        return color_mapping.get(translated_color, "#1f77b4")

    def refresh_translations(self):
        """Atualiza as traduções na interface"""
        # Atualiza labels superiores
        self.x_label.config(text=t("ui.graph_tab.column_x"))

        # Atualiza Y columns frame
        self.y_columns_frame.config(text=t("ui.graph_tab.y_columns"))

        # Atualiza comboboxes das séries
        for series_widgets in self.series_widgets:
            series_widgets['type']['values'] = self._get_translated_graph_types()
            series_widgets['color']['values'] = self._get_translated_colors()
            series_widgets['marker']['values'] = self._get_translated_markers()

        # Atualiza botões
        self.plot_button.config(text=t("ui.graph_tab.update_graph"))
        self.save_button.config(text=t("ui.graph_tab.save_png"))
        self.options_frame.config(text=t("ui.graph_tab.options_frame"))

        # Atualiza botão de pausa
        if self.is_paused:
            self.pause_button.config(text=t("ui.graph_tab.resume"))
        else:
            self.pause_button.config(text=t("ui.graph_tab.pause"))

        # Atualiza botão de opções
        if self.options_visible:
            self.options_button.config(text=t("ui.graph_tab.hide_options"))
        else:
            self.options_button.config(text=t("ui.graph_tab.show_options"))

        # Atualiza labels das opções
        self.window_label.config(text=t("ui.graph_tab.window_label"))
        self.min_y_label.config(text=t("ui.graph_tab.min_y_label"))
        self.max_y_label.config(text=t("ui.graph_tab.max_y_label"))

    def _load_preferences(self):
        """Load saved preferences"""
        # Load column settings
        x_col = self.config_manager.load_tab_setting('graph', 'x_column', DEFAULT_X_COLUMN)
        self.x_column_entry.delete(0, "end")
        self.x_column_entry.insert(0, str(x_col))

        # Load Y1-Y5 columns
        for i in range(1, 6):
            y_col = self.config_manager.load_tab_setting('graph', f'y{i}_column', '')
            entry = self.y_entries[i-1]  # y_entries[0] = Y1, y_entries[1] = Y2, etc.
            entry.delete(0, "end")
            entry.insert(0, str(y_col))

        # Load series settings for Y1-Y5
        for i in range(5):  # 0-4 for Y1-Y5
            if i < len(self.series_widgets):
                widgets = self.series_widgets[i]
                series_id = f'y{i+1}'  # y1, y2, y3, y4, y5

                # Load graph type
                graph_type = self.config_manager.load_tab_setting('graph', f'{series_id}_type', 'Line')
                type_translation_map = {
                    'Line': t("ui.graph_types.line"),
                    'Scatter': t("ui.graph_types.scatter")
                }
                if graph_type in type_translation_map:
                    widgets['type'].set(type_translation_map[graph_type])

                # Load color
                default_colors = ['Blue', 'Red', 'Green', 'Orange', 'Magenta']
                default_color = default_colors[i] if i < len(default_colors) else 'Blue'
                color = self.config_manager.load_tab_setting('graph', f'{series_id}_color', default_color)

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
                    widgets['color'].set(color_translation_map[color])

                # Load marker
                marker = self.config_manager.load_tab_setting('graph', f'{series_id}_marker', 'circle')
                marker_translation_map = {
                    'circle': t("ui.markers.circle"), 'square': t("ui.markers.square"), 'triangle': t("ui.markers.triangle"),
                    'diamond': t("ui.markers.diamond"), 'star': t("ui.markers.star"), 'plus': t("ui.markers.plus"),
                    'x': t("ui.markers.x"), 'vline': t("ui.markers.vline"), 'hline': t("ui.markers.hline"),
                    'hexagon': t("ui.markers.hexagon")
                }
                if marker in marker_translation_map:
                    widgets['marker'].set(marker_translation_map[marker])

        # Load window size
        window_size = self.config_manager.load_tab_setting('graph', 'window_size', '50')
        self.data_window_entry.delete(0, "end")
        self.data_window_entry.insert(0, str(window_size))

        # Load Y range
        min_y = self.config_manager.load_tab_setting('graph', 'min_y', '')
        max_y = self.config_manager.load_tab_setting('graph', 'max_y', '')
        if min_y:
            self.min_y_entry.delete(0, "end")
            self.min_y_entry.insert(0, str(min_y))
        if max_y:
            self.max_y_entry.delete(0, "end")
            self.max_y_entry.insert(0, str(max_y))

    def _save_preferences(self):
        """Save current preferences"""
        # Save column settings
        self.config_manager.save_tab_setting('graph', 'x_column', self.x_column_entry.get())

        # Save Y1-Y5 columns
        for i in range(1, 6):
            entry = self.y_entries[i-1]  # y_entries[0] = Y1, y_entries[1] = Y2, etc.
            self.config_manager.save_tab_setting('graph', f'y{i}_column', entry.get())

        # Save series settings for Y1-Y5
        for i in range(5):  # 0-4 for Y1-Y5
            if i < len(self.series_widgets):
                widgets = self.series_widgets[i]
                series_id = f'y{i+1}'  # y1, y2, y3, y4, y5

                # Save graph type (convert from translated to English)
                current_type = widgets['type'].get()
                type_reverse_map = {
                    t("ui.graph_types.line"): 'Line',
                    t("ui.graph_types.scatter"): 'Scatter'
                }
                type_value = type_reverse_map.get(current_type, 'Line')
                self.config_manager.save_tab_setting('graph', f'{series_id}_type', type_value)

                # Save color (convert from translated to English)
                current_color = widgets['color'].get()
                color_reverse_map = {
                    t("ui.colors.blue"): 'Blue', t("ui.colors.cyan"): 'Cyan', t("ui.colors.teal"): 'Teal',
                    t("ui.colors.green"): 'Green', t("ui.colors.lime"): 'Lime', t("ui.colors.yellow"): 'Yellow',
                    t("ui.colors.amber"): 'Amber', t("ui.colors.orange"): 'Orange', t("ui.colors.red"): 'Red',
                    t("ui.colors.magenta"): 'Magenta', t("ui.colors.indigo"): 'Indigo', t("ui.colors.violet"): 'Violet',
                    t("ui.colors.turquoise"): 'Turquoise', t("ui.colors.aquamarine"): 'Aquamarine',
                    t("ui.colors.springgreen"): 'Springgreen', t("ui.colors.chartreuse"): 'Chartreuse',
                    t("ui.colors.gold"): 'Gold', t("ui.colors.coral"): 'Coral', t("ui.colors.crimson"): 'Crimson',
                    t("ui.colors.pink"): 'Pink'
                }
                color_value = color_reverse_map.get(current_color, 'Blue')
                self.config_manager.save_tab_setting('graph', f'{series_id}_color', color_value)

                # Save marker type (convert from translated to English)
                current_marker = widgets['marker'].get()
                marker_reverse_map = {
                    t("ui.markers.circle"): 'circle', t("ui.markers.square"): 'square', t("ui.markers.triangle"): 'triangle',
                    t("ui.markers.diamond"): 'diamond', t("ui.markers.star"): 'star', t("ui.markers.plus"): 'plus',
                    t("ui.markers.x"): 'x', t("ui.markers.vline"): 'vline', t("ui.markers.hline"): 'hline',
                    t("ui.markers.hexagon"): 'hexagon'
                }
                marker_value = marker_reverse_map.get(current_marker, 'circle')
                self.config_manager.save_tab_setting('graph', f'{series_id}_marker', marker_value)

        # Save window size
        self.config_manager.save_tab_setting('graph', 'window_size', self.data_window_entry.get())

        # Save Y range
        self.config_manager.save_tab_setting('graph', 'min_y', self.min_y_entry.get())
        self.config_manager.save_tab_setting('graph', 'max_y', self.max_y_entry.get())

    def _on_preference_changed(self, event=None):
        """Called when any preference changes"""
        self._save_preferences()

    def _on_group_change(self, event=None):
        """Handle visualization group change"""
        self._create_series_widgets()
        self._save_preferences()
        self._on_setting_change()

    def _create_series_widgets(self):
        """Create series widgets based on the selected visualization group"""
        # Clear existing widgets
        for widget in self.series_config_frame.winfo_children():
            widget.destroy()

        group = self.group_combobox.get()

        if group == "Time Series":
            self._create_time_series_widgets()
        elif group == "Stacked":
            self._create_stacked_widgets()

    def _create_time_series_widgets(self):
        """Create Time Series configuration widgets (original behavior)"""
        self.series_config_frame.config(text="Series Settings")

        # Headers
        ttk.Label(self.series_config_frame, text="Series").grid(column=0, row=0, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.type_label")).grid(column=1, row=0, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.color_label")).grid(column=2, row=0, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.point_label")).grid(column=3, row=0, padx=5, pady=5)

        # Y1-Y5 series configuration
        self.series_widgets = []
        for i in range(1, 6):
            self._create_series_row(self.series_config_frame, i, f"Y{i}", i-1)

    def _create_stacked_widgets(self):
        """Create Stacked configuration widgets"""
        self.series_config_frame.config(text="Stack Settings")

        # 100% normalization checkbox
        self.normalize_100_var = tk.BooleanVar()
        self.normalize_100_checkbox = ttk.Checkbutton(
            self.series_config_frame,
            text="Normalizar para 100%",
            variable=self.normalize_100_var
        )
        self.normalize_100_checkbox.grid(column=0, row=0, columnspan=4, padx=5, pady=10)
        self.normalize_100_checkbox.bind("<Button-1>", lambda e: self.series_config_frame.after_idle(self._on_setting_change))

        # Headers for color configuration
        ttk.Label(self.series_config_frame, text="Series").grid(column=0, row=1, padx=5, pady=5)
        ttk.Label(self.series_config_frame, text=t("ui.graph_tab.color_label")).grid(column=1, row=1, padx=5, pady=5)

        # Y1-Y5 color configuration only
        self.series_widgets = []
        default_colors = [t("ui.colors.blue"), t("ui.colors.red"), t("ui.colors.green"),
                         t("ui.colors.orange"), t("ui.colors.magenta")]

        for i in range(1, 6):
            ttk.Label(self.series_config_frame, text=f"Y{i}").grid(column=0, row=i+1, padx=5, pady=2)

            color_combo = ttk.Combobox(self.series_config_frame, state="readonly",
                                     values=self._get_translated_colors(), width=10)
            color_combo.grid(column=1, row=i+1, padx=5, pady=2)
            color_combo.set(default_colors[(i-1) % len(default_colors)])
            color_combo.bind("<<ComboboxSelected>>", lambda e, idx=i-1: self._on_series_setting_change(idx))

            self.series_widgets.append({
                'color': color_combo
            })

    def _get_stacked_color(self, series_index):
        """Get color for stacked chart from series widgets"""
        if series_index < len(self.series_widgets) and 'color' in self.series_widgets[series_index]:
            translated_color = self.series_widgets[series_index]['color'].get()
            return self._get_original_color(translated_color)
        
        # Default colors if no widget found
        default_colors = ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#ff00ff"]
        return default_colors[series_index % len(default_colors)]

    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
