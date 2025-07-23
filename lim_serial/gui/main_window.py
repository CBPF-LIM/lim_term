"""
Interface gráfica principal
"""
import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_GEOMETRY
from ..core import SerialManager
from ..i18n import t, initialize as init_i18n, get_available_languages, set_language
from .config_tab import ConfigTab
from .data_tab import DataTab
from .graph_tab import GraphTab


class MainWindow:
    """Janela principal da aplicação"""
    
    def __init__(self):
        # Initialize i18n system
        init_i18n()
        
        self.root = tk.Tk()
        self.root.title(t("ui.main_window.title"))
        self.root.geometry(DEFAULT_GEOMETRY)
        
        self._setup_serial_manager()
        self._create_menu()
        self._create_tabs()
    
    def _setup_serial_manager(self):
        """Configura o gerenciador serial"""
        self.serial_manager = SerialManager(
            data_callback=self._on_data_received,
            error_callback=self._on_error
        )
    
    def _create_menu(self):
        """Cria o menu da aplicação"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Language menu
        self.language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=self.language_menu)
        
        # Store language variables for checkmarks
        self.language_vars = {}
        
        for lang in get_available_languages():
            var = tk.BooleanVar()
            self.language_vars[lang['code']] = var
            self.language_menu.add_checkbutton(
                label=lang['display_name'],
                variable=var,
                command=lambda code=lang['code']: self._change_language(code)
            )
        
        # Set initial language selection (pt-br as default)
        from ..i18n import get_current_language
        current_lang = get_current_language()
        if current_lang in self.language_vars:
            self.language_vars[current_lang].set(True)
    
    def _change_language(self, language_code):
        """Change the interface language"""
        # Update checkmarks - uncheck all, then check the selected one
        for code, var in self.language_vars.items():
            var.set(False)
        self.language_vars[language_code].set(True)
        
        set_language(language_code)
        # Update window title
        self.root.title(t("ui.main_window.title"))
        # Update tab labels
        self.tab_control.tab(0, text=t("ui.tabs.configuration"))
        self.tab_control.tab(1, text=t("ui.tabs.data"))
        self.tab_control.tab(2, text=t("ui.tabs.graph"))
        # Refresh all tabs
        self.config_tab.refresh_translations()
        self.data_tab.refresh_translations()
        self.graph_tab.refresh_translations()
    
    def _create_tabs(self):
        """Cria as abas da interface"""
        # Controle de abas
        self.tab_control = ttk.Notebook(self.root)
        
        # Cria as abas
        self.config_tab = ConfigTab(self.tab_control, self.serial_manager)
        self.data_tab = DataTab(self.tab_control)
        self.graph_tab = GraphTab(self.tab_control, self.data_tab, None)
        
        # Adiciona as abas ao controle
        self.tab_control.add(self.config_tab.get_frame(), text=t("ui.tabs.configuration"))
        self.tab_control.add(self.data_tab.get_frame(), text=t("ui.tabs.data"))
        self.tab_control.add(self.graph_tab.get_frame(), text=t("ui.tabs.graph"))
        
        # Empacota o controle de abas
        self.tab_control.pack(expand=1, fill="both")
    
    def _on_data_received(self, line):
        """Callback chamado quando dados são recebidos"""
        self.data_tab.add_data(line)
        # Atualiza gráfico automaticamente se configurado e não pausado
        if not self.graph_tab.is_paused:
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
