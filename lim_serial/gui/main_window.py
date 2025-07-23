"""
Interface gráfica principal
"""
import tkinter as tk
from tkinter import ttk
import time
from ..config import DEFAULT_GEOMETRY
from ..core import SerialManager
from ..i18n import t, initialize as init_i18n, get_available_languages, set_language
from .config_tab import ConfigTab
from .data_tab import DataTab
from .graph_tab import GraphTab


class MainWindow:
    """Janela principal da aplicação"""

    def __init__(self):

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


        self.language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Language", menu=self.language_menu)


        self.language_vars = {}

        language_order = ["en", "pt-br", "fr", "es", "de"]
        langs_by_code = {lang['code']: lang for lang in get_available_languages()}
        for code in language_order:
            if code in langs_by_code:
                lang = langs_by_code[code]
                var = tk.BooleanVar()
                self.language_vars[lang['code']] = var
                self.language_menu.add_checkbutton(
                    label=lang['display_name'],
                    variable=var,
                    command=lambda code=lang['code']: self._change_language(code)
                )


        from ..i18n import get_current_language
        current_lang = get_current_language()
        if current_lang in self.language_vars:
            self.language_vars[current_lang].set(True)

    def _change_language(self, language_code):
        """Change the interface language and show restart message"""

        for code, var in self.language_vars.items():
            var.set(False)
        self.language_vars[language_code].set(True)


        set_language(language_code)


        from tkinter import messagebox
        messagebox.showinfo(
            "Language Changed",
            t("ui.main_window.restart_required")
        )

    def _create_tabs(self):
        """Cria as abas da interface"""

        self.tab_control = ttk.Notebook(self.root)


        self.config_tab = ConfigTab(self.tab_control, self.serial_manager)
        self.data_tab = DataTab(self.tab_control)
        self.graph_tab = GraphTab(self.tab_control, self.data_tab, None)


        self.tab_control.add(self.config_tab.get_frame(), text=t("ui.tabs.configuration"))
        self.tab_control.add(self.data_tab.get_frame(), text=t("ui.tabs.data"))
        self.tab_control.add(self.graph_tab.get_frame(), text=t("ui.tabs.graph"))


        self.tab_control.pack(expand=1, fill="both")

    def _on_data_received(self, line):
        """Callback chamado quando dados são recebidos"""
        self.data_tab.add_data(line)


    def _on_error(self, error_message):
        """Callback chamado quando ocorre um erro"""
        self.data_tab.add_message(error_message)

    def run(self):
        """Executa a aplicação com game-loop style architecture"""
        import time

        try:

            self._running = True
            self._last_render_time = time.time()


            self._game_loop()


            self.root.mainloop()

        finally:
            self._running = False

            self.serial_manager.disconnect()

    def _game_loop(self):
        """Game-engine style main loop: doEvents() + timed render()"""
        if not self._running:
            return

        try:

            self.root.update()


            current_time = time.time()
            if hasattr(self.graph_tab, 'should_render_now'):
                if self.graph_tab.should_render_now(current_time):
                    self.graph_tab.render_frame()

        except tk.TclError:

            self._running = False
            return
        except Exception as e:
            print(f"Game loop error: {e}")


        if self._running and self.root.winfo_exists():
            self.root.after(16, self._game_loop)
