"""
Tab de visualização de gráficos
"""
import tkinter as tk
from tkinter import ttk
from ..core import GraphManager
from ..utils import DataParser
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN, GRAPH_TYPES, AVAILABLE_COLORS, MARKER_TYPES


class GraphTab:
    """Tab de gráficos"""
    
    def __init__(self, parent, data_tab, open_options_callback):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.graph_settings = {}
        self.options_visible = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Configuração de colunas
        ttk.Label(self.frame, text="Coluna X:").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.x_column_entry = ttk.Entry(self.frame, width=10)
        self.x_column_entry.grid(column=1, row=0, padx=10, pady=10, sticky="w")
        self.x_column_entry.insert(0, DEFAULT_X_COLUMN)
        self.x_column_entry.bind("<KeyRelease>", self._on_setting_change)
        
        ttk.Label(self.frame, text="Coluna Y:").grid(column=2, row=0, padx=10, pady=10, sticky="w")
        self.y_column_entry = ttk.Entry(self.frame, width=10)
        self.y_column_entry.grid(column=3, row=0, padx=10, pady=10, sticky="w")
        self.y_column_entry.insert(0, DEFAULT_Y_COLUMN)
        self.y_column_entry.bind("<KeyRelease>", self._on_setting_change)
        
        # Botão de atualizar gráfico
        self.plot_button = ttk.Button(self.frame, text="Atualizar Gráfico", command=self.plot_graph)
        self.plot_button.grid(column=0, row=1, columnspan=2, padx=10, pady=10)
        
        # Botão de opções (toggle)
        self.options_button = ttk.Button(self.frame, text="Mostrar Opções", command=self._toggle_options)
        self.options_button.grid(column=2, row=1, columnspan=2, padx=10, pady=10)
        
        # Frame para opções (inicialmente oculto)
        self.options_frame = ttk.LabelFrame(self.frame, text="Opções do Gráfico")
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
        ttk.Label(self.options_frame, text="Tipo:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.graph_type_combobox = ttk.Combobox(self.options_frame, state="readonly", values=GRAPH_TYPES, width=12)
        self.graph_type_combobox.grid(column=1, row=0, padx=5, pady=5, sticky="w")
        self.graph_type_combobox.set("Linha")
        self.graph_type_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        
        # Cor
        ttk.Label(self.options_frame, text="Cor:").grid(column=2, row=0, padx=5, pady=5, sticky="w")
        self.color_combobox = ttk.Combobox(self.options_frame, state="readonly", values=AVAILABLE_COLORS, width=12)
        self.color_combobox.grid(column=3, row=0, padx=5, pady=5, sticky="w")
        self.color_combobox.set("Blue")
        self.color_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        
        # Janela de dados
        ttk.Label(self.options_frame, text="Janela:").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.data_window_entry = ttk.Entry(self.options_frame, width=12)
        self.data_window_entry.grid(column=1, row=1, padx=5, pady=5, sticky="w")
        self.data_window_entry.insert(0, "0")
        self.data_window_entry.bind("<KeyRelease>", self._on_setting_change)
        
        # Tipo de ponto
        ttk.Label(self.options_frame, text="Ponto:").grid(column=2, row=1, padx=5, pady=5, sticky="w")
        self.dot_type_combobox = ttk.Combobox(self.options_frame, state="readonly", 
                                            values=list(MARKER_TYPES.keys()), width=12)
        self.dot_type_combobox.grid(column=3, row=1, padx=5, pady=5, sticky="w")
        self.dot_type_combobox.set("Círculo (o)")
        self.dot_type_combobox.bind("<<ComboboxSelected>>", self._on_setting_change)
        
        # Min e Max Y
        ttk.Label(self.options_frame, text="Min Y:").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.min_y_entry = ttk.Entry(self.options_frame, width=12)
        self.min_y_entry.grid(column=1, row=2, padx=5, pady=5, sticky="w")
        self.min_y_entry.bind("<KeyRelease>", self._on_setting_change)
        
        ttk.Label(self.options_frame, text="Max Y:").grid(column=2, row=2, padx=5, pady=5, sticky="w")
        self.max_y_entry = ttk.Entry(self.options_frame, width=12)
        self.max_y_entry.grid(column=3, row=2, padx=5, pady=5, sticky="w")
        self.max_y_entry.bind("<KeyRelease>", self._on_setting_change)
    
    def _toggle_options(self):
        """Mostra/oculta opções"""
        if self.options_visible:
            self.options_frame.grid_remove()
            self.options_button.config(text="Mostrar Opções")
            self.options_visible = False
        else:
            self.options_frame.grid(column=0, row=2, columnspan=4, padx=10, pady=10, sticky="ew")
            self.options_button.config(text="Ocultar Opções")
            self.options_visible = True
    
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
                settings["dot_type"] = MARKER_TYPES.get(self.dot_type_combobox.get(), "o")
            
            # Atualiza configurações e reaplica gráfico
            self.graph_settings.update(settings)
            if self.data_tab.get_data():
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
                raise ValueError("Números de coluna devem ser positivos")
            
            data_lines = self.data_tab.get_data()
            if not data_lines:
                self.data_tab.add_message("Nenhum dado disponível para plotar")
                return
            
            # Aplica janela de dados
            data_window = self.graph_settings.get("data_window", 0)
            if data_window > 0:
                data_lines = data_lines[-data_window:]
            
            x_data, y_data = DataParser.extract_columns(data_lines, x_col, y_col)
            
            if not x_data or not y_data:
                self.data_tab.add_message("Não foi possível extrair dados das colunas especificadas")
                return
            
            self.graph_manager.plot_from_settings(x_data, y_data, self.graph_settings, x_col, y_col)
            
        except ValueError as e:
            self.data_tab.add_message(f"Erro nos parâmetros: {e}")
        except Exception as e:
            self.data_tab.add_message(f"Erro ao gerar gráfico: {e}")
    
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
        if self.data_tab.get_data():
            self.plot_graph()
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
