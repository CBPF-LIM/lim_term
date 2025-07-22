"""
Interface gráfica principal
"""
import tkinter as tk
from tkinter import ttk
from ..config import WINDOW_TITLE, DEFAULT_GEOMETRY
from ..core import SerialManager
from .config_tab import ConfigTab
from .data_tab import DataTab
from .graph_tab import GraphTab


class MainWindow:
    """Janela principal da aplicação"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(DEFAULT_GEOMETRY)
        
        self._setup_serial_manager()
        self._create_tabs()
    
    def _setup_serial_manager(self):
        """Configura o gerenciador serial"""
        self.serial_manager = SerialManager(
            data_callback=self._on_data_received,
            error_callback=self._on_error
        )
    
    def _create_tabs(self):
        """Cria as abas da interface"""
        # Controle de abas
        self.tab_control = ttk.Notebook(self.root)
        
        # Cria as abas
        self.config_tab = ConfigTab(self.tab_control, self.serial_manager)
        self.data_tab = DataTab(self.tab_control)
        self.graph_tab = GraphTab(self.tab_control, self.data_tab, None)
        
        # Adiciona as abas ao controle
        self.tab_control.add(self.config_tab.get_frame(), text="Configuração")
        self.tab_control.add(self.data_tab.get_frame(), text="Dados")
        self.tab_control.add(self.graph_tab.get_frame(), text="Gráfico")
        
        # Empacota o controle de abas
        self.tab_control.pack(expand=1, fill="both")
    
    def _on_data_received(self, line):
        """Callback chamado quando dados são recebidos"""
        self.data_tab.add_data(line)
        # Atualiza gráfico automaticamente se configurado
        self.graph_tab.plot_graph()
    
    def _on_error(self, error_message):
        """Callback chamado quando ocorre um erro"""
        self.data_tab.add_message(error_message)
    
    def run(self):
        """Executa a aplicação"""
        try:
            self.root.mainloop()
        finally:
            # Garante que a conexão serial seja fechada
            self.serial_manager.disconnect()
