"""
Janela de opções de gráfico
"""
import tkinter as tk
from tkinter import ttk
from ..config import GRAPH_TYPES, AVAILABLE_COLORS, MARKER_TYPES

# Visualization groups
VISUALIZATION_GROUPS = ["Time Series", "Stacked"]

class GraphOptionsWindow:
    """Janela de configuração de opções de gráfico"""
    
    def __init__(self, parent, serial_gui):
        self.window = tk.Toplevel(parent)
        self.window.title("Opções de Gráfico")
        self.serial_gui = serial_gui
        
        self._create_widgets()
        self._load_current_settings()
    
    def _create_widgets(self):
        """Cria os widgets da janela"""
        # Grupo de visualização
        ttk.Label(self.window, text="Grupo de Visualização:").grid(column=0, row=0, padx=10, pady=10)
        self.group_combobox = ttk.Combobox(self.window, state="readonly", values=VISUALIZATION_GROUPS)
        self.group_combobox.grid(column=1, row=0, padx=10, pady=10)
        self.group_combobox.bind("<<ComboboxSelected>>", self._on_group_change)
        
        # Frame para configurações específicas do grupo
        self.group_frame = ttk.LabelFrame(self.window, text="Configurações do Grupo")
        self.group_frame.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Botão para aplicar configurações
        self.apply_button = ttk.Button(self.window, text="Aplicar", command=self._apply_settings)
        self.apply_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        
        # Set default group
        self.group_combobox.set("Time Series")
        self._create_group_widgets()
    
    def _load_current_settings(self):
        """Carrega as configurações atuais"""
        settings = self.serial_gui.graph_settings
        
        # Set visualization group
        group = settings.get("visualization_group", "Time Series")
        self.group_combobox.set(group)
        self._create_group_widgets()
        
        if group == "Time Series":
            self._load_time_series_settings(settings)
        elif group == "Stacked":
            self._load_stacked_settings(settings)
    
    def _load_time_series_settings(self, settings):
        """Carrega configurações para Time Series"""
        if hasattr(self, 'graph_type_combobox'):
            self.graph_type_combobox.set(settings.get("type", "Linha"))
            self.color_combobox.set(settings.get("color", "Blue"))
            self.data_window_entry.delete(0, "end")
            self.data_window_entry.insert(0, str(settings.get("data_window", "0")))
            self.min_y_entry.delete(0, "end")
            self.min_y_entry.insert(0, settings.get("min_y", ""))
            self.max_y_entry.delete(0, "end")
            self.max_y_entry.insert(0, settings.get("max_y", ""))
            
            # Carrega tipo de ponto
            current_dot_type = settings.get("dot_type", "o")
            for label, value in MARKER_TYPES.items():
                if value == current_dot_type:
                    self.dot_type_combobox.set(label)
                    break
            else:
                self.dot_type_combobox.set("Círculo (o)")
    
    def _load_stacked_settings(self, settings):
        """Carrega configurações para Stacked"""
        if hasattr(self, 'normalize_100_var'):
            self.normalize_100_var.set(settings.get("normalize_100", False))
            
            # Load Y series colors
            y_colors = settings.get("y_colors", ["Blue", "Red", "Green", "Orange", "Magenta"])
            for i, combo in enumerate(self.y_color_combos):
                if i < len(y_colors):
                    combo.set(y_colors[i])
    
    def _apply_settings(self):
        """Aplica as configurações selecionadas"""
        try:
            settings = {}
            group = self.group_combobox.get()
            settings["visualization_group"] = group
            
            if group == "Time Series":
                self._apply_time_series_settings(settings)
            elif group == "Stacked":
                self._apply_stacked_settings(settings)
            
            self.serial_gui.update_graph_settings(settings)
            print("Configurações aplicadas:", settings)
            self.window.destroy()
            
        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")
    
    def _apply_time_series_settings(self, settings):
        """Aplica configurações para Time Series"""
        if hasattr(self, 'graph_type_combobox'):
            # Coleta valores apenas se não estiverem vazios
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
    
    def _apply_stacked_settings(self, settings):
        """Aplica configurações para Stacked"""
        if hasattr(self, 'normalize_100_var'):
            settings["normalize_100"] = self.normalize_100_var.get()
            
            # Collect Y series colors
            y_colors = []
            for combo in self.y_color_combos:
                y_colors.append(combo.get())
            settings["y_colors"] = y_colors
    
    def _on_group_change(self, event=None):
        """Handle visualization group change"""
        self._create_group_widgets()
    
    def _create_group_widgets(self):
        """Cria widgets específicos para o grupo selecionado"""
        # Clear existing widgets
        for widget in self.group_frame.winfo_children():
            widget.destroy()
        
        group = self.group_combobox.get()
        
        if group == "Time Series":
            self._create_time_series_widgets()
        elif group == "Stacked":
            self._create_stacked_widgets()
    
    def _create_time_series_widgets(self):
        """Cria widgets para Time Series (configurações originais)"""
        # Tipo de gráfico
        ttk.Label(self.group_frame, text="Tipo de Gráfico:").grid(column=0, row=0, padx=5, pady=5)
        self.graph_type_combobox = ttk.Combobox(self.group_frame, state="readonly", values=GRAPH_TYPES)
        self.graph_type_combobox.grid(column=1, row=0, padx=5, pady=5)
        
        # Cor
        ttk.Label(self.group_frame, text="Cor:").grid(column=0, row=1, padx=5, pady=5)
        self.color_combobox = ttk.Combobox(self.group_frame, state="readonly", values=AVAILABLE_COLORS)
        self.color_combobox.grid(column=1, row=1, padx=5, pady=5)
        
        # Janela de dados
        ttk.Label(self.group_frame, text="Janela de Dados (N últimos pontos):").grid(column=0, row=2, padx=5, pady=5)
        self.data_window_entry = ttk.Entry(self.group_frame)
        self.data_window_entry.grid(column=1, row=2, padx=5, pady=5)
        self.data_window_entry.insert(0, "0")  # Valor padrão
        
        # Min e Max dos eixos Y
        ttk.Label(self.group_frame, text="Min Y:").grid(column=0, row=3, padx=5, pady=5)
        self.min_y_entry = ttk.Entry(self.group_frame)
        self.min_y_entry.grid(column=1, row=3, padx=5, pady=5)
        
        ttk.Label(self.group_frame, text="Max Y:").grid(column=0, row=4, padx=5, pady=5)
        self.max_y_entry = ttk.Entry(self.group_frame)
        self.max_y_entry.grid(column=1, row=4, padx=5, pady=5)
        
        # Tipo de ponto
        ttk.Label(self.group_frame, text="Tipo de Ponto:").grid(column=0, row=5, padx=5, pady=5)
        self.dot_type_combobox = ttk.Combobox(self.group_frame, state="readonly", 
                                            values=list(MARKER_TYPES.keys()))
        self.dot_type_combobox.grid(column=1, row=5, padx=5, pady=5)
    
    def _create_stacked_widgets(self):
        """Cria widgets para Stacked visualization"""
        # Stack Settings label
        ttk.Label(self.group_frame, text="Stack Settings", font=("Arial", 10, "bold")).grid(column=0, row=0, columnspan=2, pady=10)
        
        # 100% normalization checkbox
        self.normalize_100_var = tk.BooleanVar()
        self.normalize_100_checkbox = ttk.Checkbutton(
            self.group_frame, 
            text="Normalizar para 100%", 
            variable=self.normalize_100_var
        )
        self.normalize_100_checkbox.grid(column=0, row=1, columnspan=2, padx=5, pady=5)
        
        # Y Series Color Configuration
        ttk.Label(self.group_frame, text="Configuração de Cores das Séries Y:", font=("Arial", 9, "bold")).grid(column=0, row=2, columnspan=2, pady=(10, 5))
        
        # Create color selectors for Y1-Y5
        self.y_color_combos = []
        default_colors = ["Blue", "Red", "Green", "Orange", "Magenta"]
        
        for i in range(5):
            ttk.Label(self.group_frame, text=f"Y{i+1}:").grid(column=0, row=3+i, padx=5, pady=2, sticky="e")
            color_combo = ttk.Combobox(self.group_frame, state="readonly", values=AVAILABLE_COLORS, width=15)
            color_combo.grid(column=1, row=3+i, padx=5, pady=2)
            color_combo.set(default_colors[i])
            self.y_color_combos.append(color_combo)
