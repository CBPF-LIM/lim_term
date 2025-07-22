"""
Tab de visualização de gráficos
"""
import tkinter as tk
from tkinter import ttk
from ..core import GraphManager
from ..utils import DataParser
from ..config import DEFAULT_X_COLUMN, DEFAULT_Y_COLUMN


class GraphTab:
    """Tab de gráficos"""
    
    def __init__(self, parent, data_tab, open_options_callback):
        self.frame = ttk.Frame(parent)
        self.data_tab = data_tab
        self.open_options_callback = open_options_callback
        self.graph_settings = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Configuração de colunas
        ttk.Label(self.frame, text="Coluna X:").grid(column=0, row=0, padx=10, pady=10)
        self.x_column_entry = ttk.Entry(self.frame)
        self.x_column_entry.grid(column=1, row=0, padx=10, pady=10)
        self.x_column_entry.insert(0, DEFAULT_X_COLUMN)
        
        ttk.Label(self.frame, text="Coluna Y:").grid(column=0, row=1, padx=10, pady=10)
        self.y_column_entry = ttk.Entry(self.frame)
        self.y_column_entry.grid(column=1, row=1, padx=10, pady=10)
        self.y_column_entry.insert(0, DEFAULT_Y_COLUMN)
        
        # Botão de gerar gráfico
        self.plot_button = ttk.Button(self.frame, text="Gerar Gráfico", command=self.plot_graph)
        self.plot_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
        
        # Área do gráfico
        self.graph_manager = GraphManager(self.frame)
        self.graph_manager.get_widget().grid(column=0, row=3, columnspan=2, padx=10, pady=10)
        
        # Botão de opções
        self.options_button = ttk.Button(self.frame, text="Opções de Gráfico", 
                                       command=self.open_options_callback)
        self.options_button.grid(column=0, row=4, columnspan=2, padx=10, pady=10)
    
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
        """Atualiza configurações do gráfico"""
        self.graph_settings.update(settings)
        # Replot automaticamente se houver dados
        if self.data_tab.get_data():
            self.plot_graph()
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
