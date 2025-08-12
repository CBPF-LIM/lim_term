import time
from ..config import DEFAULT_GEOMETRY
from ..core import SerialManager
from ..i18n import t, get_available_languages, set_language
from ..utils.signal_handler import SignalHandler
from ..utils.ui_builder import build_from_layout_name, show_info_dialog, extend_menu
from .config_tab import ConfigTab
from .data_tab import DataTab
from .graph_tab import GraphTab
from .osc_tab import OscTab


class MainWindow:
    def __init__(self):

        self.root = build_from_layout_name(None, "root_window", self)

        try:
            self.root.geometry(DEFAULT_GEOMETRY)
        except Exception:
            pass

        self.signal_handler = SignalHandler(self)
        self.signal_handler.setup_signal_handlers()

        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        except Exception:
            pass

        self._setup_serial_manager()
        self._build_layout()
        self._create_tabs()
        self._create_menu()
        self._setup_keyboard_shortcuts()

    def _setup_serial_manager(self):
        self.serial_manager = SerialManager(
            data_callback=self._on_data_received, error_callback=self._on_error
        )

    def _build_layout(self):
        try:
            build_from_layout_name(self.root, "main_window", self)
        except Exception:
            pass

    def _create_menu(self):

        try:
            build_from_layout_name(self.root, "main_menu", self)
        except Exception:
            pass

        try:
            language_order = ["en", "pt-br", "fr", "es", "de"]
            langs_by_code = {lang["code"]: lang for lang in get_available_languages()}

            lang_items = []
            for code in language_order:
                if code in langs_by_code:
                    lang = langs_by_code[code]

                    lang_items.append(
                        {
                            "type": "checkbutton",
                            "label": lang["display_name"],
                            "var_key": code,
                            "command": (
                                lambda c=code: (lambda: self._change_language(c))
                            )(),
                        }
                    )

            if hasattr(self, "language_menu"):
                extend_menu(
                    self.language_menu,
                    lang_items,
                    self,
                    variables_attr_name="language_vars",
                )
        except Exception:
            pass

    def _goto_config_tab(self):
        self._switch_to_tab(0)

    def _goto_data_tab(self):
        self._switch_to_tab(1)

    def _goto_graph_tab(self):
        self._switch_to_tab(2)

    def _goto_osc_tab(self):
        self._switch_to_tab(3)

    def _change_language(self, language_code):

        if hasattr(self, "language_vars") and isinstance(self.language_vars, dict):
            try:
                for code, var in self.language_vars.items():
                    var.set(False)
                if language_code in self.language_vars:
                    self.language_vars[language_code].set(True)
            except Exception:
                pass

        set_language(language_code)

        try:
            show_info_dialog(
                self.root,
                t("dialogs.language_changed"),
                t("ui.main_window.restart_required"),
            )
        except Exception:
            pass

    def _create_tabs(self):

        self.config_tab = ConfigTab(
            self.tab_control, self.serial_manager, self.signal_handler
        )
        self.data_tab = DataTab(self.tab_control)
        self.graph_tab = GraphTab(self.tab_control, self.data_tab, None)
        self.osc_tab = OscTab(self.tab_control, self.data_tab)

        self.tab_control.add(
            self.config_tab.get_frame(), text=t("ui.tabs.configuration")
        )
        self.tab_control.add(self.data_tab.get_frame(), text=t("ui.tabs.data"))
        self.tab_control.add(self.graph_tab.get_frame(), text=t("ui.tabs.graph"))
        self.tab_control.add(self.osc_tab.get_frame(), text=t("ui.tabs.oscilloscope"))

        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        try:
            self.tab_control.pack_configure(expand=1, fill="both")
        except Exception:
            pass

        self._update_active_tab()

    def _on_tab_changed(self, event):
        self._update_active_tab()

    def _update_active_tab(self):
        try:
            active_tab_index = self.tab_control.index("current")

            if hasattr(self.graph_tab, "set_tab_active"):
                self.graph_tab.set_tab_active(False)
            if hasattr(self.osc_tab, "set_tab_active"):
                self.osc_tab.set_tab_active(False)

            if active_tab_index == 2:
                if hasattr(self.graph_tab, "set_tab_active"):
                    self.graph_tab.set_tab_active(True)
            elif active_tab_index == 3:
                if hasattr(self.osc_tab, "set_tab_active"):
                    self.osc_tab.set_tab_active(True)

        except Exception:
            pass

    def _on_data_received(self, line):
        self.data_tab.add_data(line)

    def _on_error(self, error_message):
        self.data_tab.add_message(error_message)

    def run(self):
        try:
            self._running = True
            self._last_render_time = time.time()

            self._game_loop()

            try:
                self.root.mainloop()
            except Exception:
                pass

        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            self._running = False

            if hasattr(self, "data_tab"):
                self.data_tab.cleanup()

            if hasattr(self, "osc_tab"):
                self.osc_tab.cleanup()

            if hasattr(self, "serial_manager"):
                self.serial_manager.disconnect()

    def _game_loop(self):
        if not self._running:
            return

        try:
            try:
                self.root.update()
            except Exception:
                pass

            current_time = time.time()

            try:
                active_tab_index = self.tab_control.index("current")

                if active_tab_index == 2 and hasattr(
                    self.graph_tab, "should_render_now"
                ):
                    if self.graph_tab.should_render_now(current_time):
                        self.graph_tab.render_frame()

            except Exception:
                pass

        except Exception:
            self._running = False
            return
        except Exception as e:
            print(t("errors.main_loop_error", error=str(e)))

        try:
            if self._running and self.root.winfo_exists():
                self.root.after(16, self._game_loop)
        except Exception:
            self._running = False

    def _on_window_close(self):
        self.signal_handler.request_exit()

    def _setup_keyboard_shortcuts(self):

        try:
            self.root.bind("<Control-1>", lambda e: self._switch_to_tab(0))
            self.root.bind("<Control-2>", lambda e: self._switch_to_tab(1))
            self.root.bind("<Control-3>", lambda e: self._switch_to_tab(2))
            self.root.bind("<Control-4>", lambda e: self._switch_to_tab(3))

            self.root.bind("<Control-Key-1>", lambda e: self._switch_to_tab(0))
            self.root.bind("<Control-Key-2>", lambda e: self._switch_to_tab(1))
            self.root.bind("<Control-Key-3>", lambda e: self._switch_to_tab(2))
            self.root.bind("<Control-Key-4>", lambda e: self._switch_to_tab(3))

            self.root.focus_set()
            self.root.focus_force()
        except Exception:
            pass

    def _switch_to_tab(self, tab_index):
        try:
            if hasattr(self, "tab_control") and tab_index < self.tab_control.index(
                "end"
            ):
                self.tab_control.select(tab_index)
        except Exception:
            pass
