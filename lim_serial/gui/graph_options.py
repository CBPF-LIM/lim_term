"""
Janela de opções de gráfico
"""
import tkinter as tk
from tkinter import ttk
from ..config import GRAPH_TYPES, AVAILABLE_COLORS, MARKER_TYPES
from ..i18n import t


class GraphOptionsWindow:
    """Janela de configuração de opções de gráfico"""

    def __init__(self, parent, serial_gui):
        self.window = tk.Toplevel(parent)
        self.window.title(t("ui.graph_tab.graph_options_title"))
        self.serial_gui = serial_gui

        self._create_widgets()
        self._load_current_settings()

    def _create_widgets(self):
        """Cria os widgets da janela"""

        ttk.Label(self.window, text=t("ui.graph_tab.type_label")).grid(column=0, row=0, padx=10, pady=10)
        self.graph_type_combobox = ttk.Combobox(self.window, state="readonly", values=GRAPH_TYPES)
        self.graph_type_combobox.grid(column=1, row=0, padx=10, pady=10)


        ttk.Label(self.window, text=t("ui.graph_tab.color_label")).grid(column=0, row=1, padx=10, pady=10)
        self.color_combobox = ttk.Combobox(self.window, state="readonly", values=AVAILABLE_COLORS)
        self.color_combobox.grid(column=1, row=1, padx=10, pady=10)


        ttk.Label(self.window, text=t("ui.graph_tab.window_label")).grid(column=0, row=2, padx=10, pady=10)
        self.data_window_entry = ttk.Entry(self.window)
        self.data_window_entry.grid(column=1, row=2, padx=10, pady=10)
        self.data_window_entry.insert(0, "0")


        ttk.Label(self.window, text=t("ui.graph_tab.min_y_label")).grid(column=0, row=3, padx=10, pady=10)
        self.min_y_entry = ttk.Entry(self.window)
        self.min_y_entry.grid(column=1, row=3, padx=10, pady=10)

        ttk.Label(self.window, text=t("ui.graph_tab.max_y_label")).grid(column=0, row=4, padx=10, pady=10)
        self.max_y_entry = ttk.Entry(self.window)
        self.max_y_entry.grid(column=1, row=4, padx=10, pady=10)


        ttk.Label(self.window, text=t("ui.graph_tab.point_label")).grid(column=0, row=5, padx=10, pady=10)
        self.dot_type_combobox = ttk.Combobox(self.window, state="readonly",
                                            values=list(MARKER_TYPES.keys()))
        self.dot_type_combobox.grid(column=1, row=5, padx=10, pady=10)


        self.apply_button = ttk.Button(self.window, text=t("ui.graph_tab.apply_button"), command=self._apply_settings)
        self.apply_button.grid(column=0, row=6, columnspan=2, padx=10, pady=10)

    def _load_current_settings(self):
        """Carrega as configurações atuais"""
        settings = self.serial_gui.graph_settings

        self.graph_type_combobox.set(settings.get("type", "Linha"))
        self.color_combobox.set(settings.get("color", "Blue"))
        self.data_window_entry.delete(0, "end")
        self.data_window_entry.insert(0, str(settings.get("data_window", "0")))
        self.min_y_entry.delete(0, "end")
        self.min_y_entry.insert(0, settings.get("min_y", ""))
        self.max_y_entry.delete(0, "end")
        self.max_y_entry.insert(0, settings.get("max_y", ""))


        current_dot_type = settings.get("dot_type", "o")
        for label, value in MARKER_TYPES.items():
            if value == current_dot_type:
                self.dot_type_combobox.set(label)
                break
        else:
            self.dot_type_combobox.set("Círculo (o)")

    def _apply_settings(self):
        """Aplica as configurações selecionadas"""
        try:
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

            self.serial_gui.update_graph_settings(settings)
            print("Configurações aplicadas:", settings)
            self.window.destroy()

        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")
