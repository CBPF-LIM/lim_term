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
        # Linha superior: Coluna X, Coluna Y, e botões, todos alinhados à esquerda
        top_row = ttk.Frame(self.frame)
        top_row.grid(column=0, row=0, sticky="w", padx=10, pady=10)

        self.x_label = ttk.Label(top_row, text=t("ui.graph_tab.column_x"))
        self.x_label.pack(side="left", padx=(0,5))
        self.x_column_entry = ttk.Entry(top_row, width=10)
        self.x_column_entry.pack(side="left", padx=(0,15))
        self.x_column_entry.insert(0, DEFAULT_X_COLUMN)
        self.x_column_entry.bind("<KeyRelease>", self._on_setting_change)
        self.x_column_entry.bind("<FocusOut>", self._on_preference_changed)

        self.y_label = ttk.Label(top_row, text=t("ui.graph_tab.column_y"))
        self.y_label.pack(side="left", padx=(0,5))
        self.y_column_entry = ttk.Entry(top_row, width=10)
        self.y_column_entry.pack(side="left", padx=(0,15))
        self.y_column_entry.insert(0, DEFAULT_Y_COLUMN)
        self.y_column_entry.bind("<KeyRelease>", self._on_setting_change)
        self.y_column_entry.bind("<FocusOut>", self._on_preference_changed)

        self.plot_button = ttk.Button(top_row, text=t("ui.graph_tab.update_graph"), command=self.plot_graph)
        self.plot_button.pack(side="left", padx=(0,10))

        self.pause_button = ttk.Button(top_row, text=t("ui.graph_tab.pause"), command=self._toggle_pause)
        self.pause_button.pack(side="left", padx=(0,10))

        self.options_button = ttk.Button(top_row, text=t("ui.graph_tab.show_options"), command=self._toggle_options)
        self.options_button.pack(side="left", padx=(0,10))

        self.save_button = ttk.Button(top_row, text=t("ui.graph_tab.save_png"), command=self._save_chart)
        self.save_button.pack(side="left", padx=(0,10))
        
        # Frame para opções (inicialmente oculto)
        self.options_frame = ttk.LabelFrame(self.frame, text=t("ui.graph_tab.options_frame"))
        self._create_options_widgets()
        
        # Área do gráfico
        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(column=0, row=3, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        # Configura expansão
        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, weight=1)
    
    def _create_options_widgets(self):
        """Cria os widgets de opções"""
        # Tipo de gráfico
        self.type_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.type_label"))
        self.type_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.graph_type_combobox = ttk.Combobox(self.options_frame, state="readonly", values=self._get_translated_graph_types(), width=12)
        self.graph_type_combobox.grid(column=1, row=0, padx=5, pady=5, sticky="w")
        self.graph_type_combobox.set(t("ui.graph_types.line"))
        self.graph_type_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        self.graph_type_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed, add="+")
        
        # Cor
        self.color_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.color_label"))
        self.color_label.grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.color_combobox = ttk.Combobox(self.options_frame, state="readonly", values=self._get_translated_colors(), width=12)
        self.color_combobox.grid(column=3, row=0, padx=5, pady=5, sticky="w")
        self.color_combobox.set(t("ui.colors.blue"))
        self.color_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        self.color_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed, add="+")
        
        # Janela de dados
        self.window_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.window_label"))
        self.window_label.grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.data_window_entry = ttk.Entry(self.options_frame, width=12)
        self.data_window_entry.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.data_window_entry.insert(0, "100")
        self.data_window_entry.bind("<KeyRelease>", self._on_setting_change)
        self.data_window_entry.bind("<FocusOut>", self._on_preference_changed)
        
        # Tipo de ponto
        self.point_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.point_label"))
        self.point_label.grid(column=2, row=1, padx=5, pady=5, sticky="w")
        self.dot_type_combobox = ttk.Combobox(self.options_frame, state="readonly", 
                                            values=self._get_translated_markers(), width=12)
        self.dot_type_combobox.grid(column=3, row=1, padx=5, pady=5, sticky="w")
        self.dot_type_combobox.set(t("ui.markers.circle"))
        self.dot_type_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        self.dot_type_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed, add="+")
        
        # Min e Max Y
        self.min_y_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.min_y_label"))
        self.min_y_label.grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.min_y_entry = ttk.Entry(self.options_frame, width=12)
        self.min_y_entry.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        self.min_y_entry.bind("<KeyRelease>", self._on_setting_change)
        self.min_y_entry.bind("<FocusOut>", self._on_preference_changed)
        
        self.max_y_label = ttk.Label(self.options_frame, text=t("ui.graph_tab.max_y_label"))
        self.max_y_label.grid(column=2, row=2, padx=5, pady=5, sticky="w")
        self.max_y_entry = ttk.Entry(self.options_frame, width=12)
        self.max_y_entry.grid(column=3, row=2, padx=5, pady=5, sticky="w")
        self.max_y_entry.bind("<KeyRelease>", self._on_setting_change)
        self.max_y_entry.bind("<FocusOut>", self._on_preference_changed)
    
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
        
        # Copia as barras se existirem
        for patch in ax_original.patches:
            if hasattr(patch, 'get_height'):  # É uma barra
                ax_copy.bar(patch.get_x() + patch.get_width()/2, patch.get_height(),
                           width=patch.get_width(), color=patch.get_facecolor(),
                           alpha=patch.get_alpha())
        
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
            # Coleta todas as configurações
            settings = {}
            
            if self.graph_type_combobox.get():
                settings["type"] = self.graph_type_combobox.get()
            if self.color_combobox.get():
                settings["color"] = self.color_combobox.get()
            if self.data_window_entry.get():
                settings["data_window"] = int(self.data_window_entry.get())
            if self.min_y_entry.get():
                settings["min_y"] = self.min_y_entry.get()
            if self.max_y_entry.get():
                settings["max_y"] = self.max_y_entry.get()
            if self.dot_type_combobox.get():
                settings["dot_type"] = self._get_original_marker(self.dot_type_combobox.get())
            
            # Atualiza configurações e reaplica gráfico
            self.graph_settings.update(settings)
            if self.data_tab.get_data() and not self.is_paused:
                self.plot_graph()
                
        except (ValueError, KeyError):
            # Ignora erros durante digitação
            pass
    
    def plot_graph(self):
        """Gera o gráfico"""
        try:
            x_col = int(self.x_column_entry.get()) - 1
            y_col = int(self.y_column_entry.get()) - 1
            
            if x_col < 0 or y_col < 0:
                raise ValueError(t("ui.graph_tab.positive_numbers"))
            
            data_lines = self.data_tab.get_data()
            if not data_lines:
                self.data_tab.add_message(t("ui.graph_tab.no_data_available"))
                return
            
            # Aplica janela de dados
            data_window = self.graph_settings.get("data_window", 0)
            if data_window > 0:
                data_lines = data_lines[-data_window:]
            
            x_data, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
            
            if not x_data or not y_data:
                self.data_tab.add_message(t("ui.graph_tab.could_not_extract_data"))
                return
            
            self.graph_manager.plot_from_settings(x_data, y_data, self.graph_settings, x_col, y_col)
            
        except ValueError as e:
            self.data_tab.add_message(t("ui.graph_tab.parameter_error").format(error=e))
        except Exception as e:
            self.data_tab.add_message(t("ui.graph_tab.graph_error").format(error=e))
    
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
        return [t("ui.graph_types.line"), t("ui.graph_types.bars"), t("ui.graph_types.scatter")]
    
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
    
    def refresh_translations(self):
        """Atualiza as traduções na interface"""
        # Atualiza labels superiores
        self.x_label.config(text=t("ui.graph_tab.column_x"))
        self.y_label.config(text=t("ui.graph_tab.column_y"))
        
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
        self.type_label.config(text=t("ui.graph_tab.type_label"))
        self.color_label.config(text=t("ui.graph_tab.color_label"))
        self.window_label.config(text=t("ui.graph_tab.window_label"))
        self.point_label.config(text=t("ui.graph_tab.point_label"))
        self.min_y_label.config(text=t("ui.graph_tab.min_y_label"))
        self.max_y_label.config(text=t("ui.graph_tab.max_y_label"))
        
        # Atualiza comboboxes
        self.graph_type_combobox["values"] = self._get_translated_graph_types()
        self.color_combobox["values"] = self._get_translated_colors()
        self.dot_type_combobox["values"] = self._get_translated_markers()
        
        # Redefine valores selecionados
        self.graph_type_combobox.set(t("ui.graph_types.line"))
        self.color_combobox.set(t("ui.colors.blue"))
        self.dot_type_combobox.set(t("ui.markers.circle"))
    
    def _load_preferences(self):
        """Load saved preferences"""
        # Load column settings
        x_col = self.config_manager.load_tab_setting('graph', 'x_column', DEFAULT_X_COLUMN)
        y_col = self.config_manager.load_tab_setting('graph', 'y_column', DEFAULT_Y_COLUMN)
        self.x_column_entry.delete(0, "end")
        self.x_column_entry.insert(0, str(x_col))
        self.y_column_entry.delete(0, "end")
        self.y_column_entry.insert(0, str(y_col))
        
        # Load graph type
        graph_type = self.config_manager.load_tab_setting('graph', 'type', 'Line')
        type_translation_map = {
            'Line': t("ui.graph_types.line"),
            'Bars': t("ui.graph_types.bars"),
            'Scatter': t("ui.graph_types.scatter")
        }
        if graph_type in type_translation_map:
            self.graph_type_combobox.set(type_translation_map[graph_type])
        
        # Load color
        color = self.config_manager.load_tab_setting('graph', 'color', 'Blue')
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
            self.color_combobox.set(color_translation_map[color])
        
        # Load window size
        window_size = self.config_manager.load_tab_setting('graph', 'window_size', '100')
        self.data_window_entry.delete(0, "end")
        self.data_window_entry.insert(0, str(window_size))
        
        # Load marker type
        marker = self.config_manager.load_tab_setting('graph', 'marker', 'circle')
        marker_translation_map = {
            'circle': t("ui.markers.circle"), 'square': t("ui.markers.square"), 'triangle': t("ui.markers.triangle"),
            'diamond': t("ui.markers.diamond"), 'star': t("ui.markers.star"), 'plus': t("ui.markers.plus"),
            'x': t("ui.markers.x"), 'vline': t("ui.markers.vline"), 'hline': t("ui.markers.hline"),
            'hexagon': t("ui.markers.hexagon")
        }
        if marker in marker_translation_map:
            self.dot_type_combobox.set(marker_translation_map[marker])
        
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
        self.config_manager.save_tab_setting('graph', 'y_column', self.y_column_entry.get())
        
        # Save graph type (convert from translated to English)
        current_type = self.graph_type_combobox.get()
        type_reverse_map = {
            t("ui.graph_types.line"): 'Line',
            t("ui.graph_types.bars"): 'Bars',
            t("ui.graph_types.scatter"): 'Scatter'
        }
        type_value = type_reverse_map.get(current_type, 'Line')
        self.config_manager.save_tab_setting('graph', 'type', type_value)
        
        # Save color (convert from translated to English)
        current_color = self.color_combobox.get()
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
        self.config_manager.save_tab_setting('graph', 'color', color_value)
        
        # Save window size
        self.config_manager.save_tab_setting('graph', 'window_size', self.data_window_entry.get())
        
        # Save marker type (convert from translated to English)
        current_marker = self.dot_type_combobox.get()
        marker_reverse_map = {
            t("ui.markers.circle"): 'circle', t("ui.markers.square"): 'square', t("ui.markers.triangle"): 'triangle',
            t("ui.markers.diamond"): 'diamond', t("ui.markers.star"): 'star', t("ui.markers.plus"): 'plus',
            t("ui.markers.x"): 'x', t("ui.markers.vline"): 'vline', t("ui.markers.hline"): 'hline',
            t("ui.markers.hexagon"): 'hexagon'
        }
        marker_value = marker_reverse_map.get(current_marker, 'circle')
        self.config_manager.save_tab_setting('graph', 'marker', marker_value)
        
        # Save Y range
        self.config_manager.save_tab_setting('graph', 'min_y', self.min_y_entry.get())
        self.config_manager.save_tab_setting('graph', 'max_y', self.max_y_entry.get())
    
    def _on_preference_changed(self, event=None):
        """Called when any preference changes"""
        self._save_preferences()
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
