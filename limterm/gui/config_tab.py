import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import SyntheticDataGenerator
from ..i18n import t, get_config_manager
from .preference_widgets import PrefCombobox
import platform


class ConfigTab:
    def __init__(self, parent, serial_manager):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        self.synthetic_generator = None
        self.config_manager = get_config_manager()
        self.equation_entries = {}

        self._create_widgets()
        self._update_ports()
        self._load_preferences()

    def _create_widgets(self):
        self.config_frame = ttk.LabelFrame(
            self.frame, text=t("ui.config_tab.configuration_frame")
        )
        self.config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="ew")

        self.mode_label = ttk.Label(
            self.config_frame, text=t("ui.config_tab.mode_label")
        )
        self.mode_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox = ttk.Combobox(
            self.config_frame,
            state="readonly",
            values=["Hardware", "Synthetic"],
        )
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox.set("Hardware")
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combobox.bind(
            "<<ComboboxSelected>>", self._on_preference_changed, add="+"
        )

        self.port_label = ttk.Label(
            self.config_frame, text=t("ui.config_tab.port_label")
        )
        self.port_label.grid(column=0, row=1, padx=10, pady=10, sticky="w")

        port_frame = ttk.Frame(self.config_frame)
        port_frame.grid(column=1, row=1, padx=10, pady=10, sticky="w")

        self.port_combobox = ttk.Combobox(port_frame, state="readonly")
        self.port_combobox.grid(column=0, row=0, sticky="w")
        self.port_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)

        self.refresh_button = ttk.Button(
            port_frame, text="🔄", width=3, command=self._update_ports
        )
        self.refresh_button.grid(column=1, row=0, padx=(5, 0))

        port_frame.columnconfigure(0, weight=1)

        self.baudrate_label = ttk.Label(
            self.config_frame, text=t("ui.config_tab.baudrate_label")
        )
        self.baudrate_label.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox = ttk.Combobox(
            self.config_frame, state="readonly", values=DEFAULT_BAUDRATES
        )
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        self.baudrate_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)

        self.config_frame.columnconfigure(1, weight=1)

        self.equation_frame = ttk.LabelFrame(
            self.frame, text=t("ui.config_tab.mode_synthetic_data_equations")
        )
        self.equation_frame.grid(column=0, row=2, padx=10, pady=10, sticky="ew")
        self.equation_frame.grid_remove()  # Hidden by default

        # FPS selection for synthetic mode (move up)
        self.fps_label = ttk.Label(self.equation_frame, text="FPS:")
        self.fps_label.grid(
            column=0, row=0, padx=5, pady=5, sticky="w"
        )
        self.fps_pref_combobox = PrefCombobox(
            self.equation_frame,
            pref_key="graph.general.refresh_rate",
            default_value="10",
            state="readonly",
            values=[str(i) for i in range(1, 31)],
            width=8,
        )
        self.fps_pref_combobox.grid(
            column=1, row=0, padx=5, pady=5, sticky="w"
        )

        self.equation_labels = ["a", "b", "c", "d", "e"]
        for i, label in enumerate(self.equation_labels):
            col_label = ttk.Label(self.equation_frame, text=f"{label}:")
            col_label.grid(column=0, row=i+1, padx=5, pady=5, sticky="w")

            equation_entry = ttk.Entry(self.equation_frame, width=40)
            equation_entry.grid(column=1, row=i+1, padx=5, pady=5, sticky="ew")
            equation_entry.bind("<KeyRelease>", self._on_equation_changed)
            self.equation_entries[label] = equation_entry

        self.equation_frame.columnconfigure(1, weight=1)

        self.info_frame = ttk.LabelFrame(
            self.frame, text=t("ui.config_tab.connection_info_frame")
        )
        self.info_frame.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

        self.info_label = ttk.Label(
            self.info_frame,
            text="",
            justify="left",
            font=("TkDefaultFont", 9),
            foreground="darkgreen",
        )
        self.info_label.grid(column=0, row=0, padx=15, pady=15, sticky="w")

        self.info_frame.grid_remove()

        self.connect_button = ttk.Button(
            self.frame, text=t("ui.config_tab.connect"), command=self._connect
        )
        self.connect_button.grid(column=0, row=2, padx=10, pady=10, sticky="w")

        self.frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        frame_bg = style.lookup("TLabelframe", "background")
        self.win_simul_info = tk.Text(
            self.config_frame,
            height=3,
            width=120,
            wrap="word",
            foreground="red",
            background=frame_bg,
            borderwidth=0,
            highlightthickness=0,
        )
        self.win_simul_info.insert(
            "1.0",
            "To simulate a virtual serial port on Windows, install the Null-modem emulator (com0com: https://com0com.sourceforge.net/).\nAfter configuration, select 'Hardware' mode and choose the created COM port.",
        )
        self.win_simul_info.config(state="disabled")
        self.win_simul_info.grid(
            column=0, row=10, columnspan=2, padx=10, pady=5, sticky="w"
        )
        self.win_simul_info.grid_remove()

    def _on_mode_changed(self, event=None):
        mode = self.mode_combobox.get()
        if mode == "Synthetic":
            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.port_combobox.set("")
            self.baudrate_combobox.set("")
            self.equation_frame.grid(
                column=0, row=6, columnspan=2, padx=10, pady=10, sticky="ew"
            )
            self.win_simul_info.grid_remove()
            self.connect_button.config(
                text=t("ui.config_tab.start_synthetic"), state="normal"
            )
        else:
            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            self.win_simul_info.grid_remove()
            self.equation_frame.grid_remove()
            self.connect_button.config(text=t("ui.config_tab.connect"), state="normal")
            self.connect_button.config(state="normal")

            if not self.baudrate_combobox.get():
                if hasattr(self.baudrate_combobox, "config"):
                    self.baudrate_combobox.set(DEFAULT_BAUDRATES[0])
            self._update_ports()

    def _update_ports(self):
        if self.mode_combobox.get() == "Hardware":
            ports = self.serial_manager.get_available_ports()
            self.port_combobox["values"] = ports
            if ports:
                if (
                    hasattr(self, "_preferred_port")
                    and self._preferred_port
                    and self._preferred_port in ports
                ):
                    self.port_combobox.set(self._preferred_port)
                else:
                    self.port_combobox.set(ports[0])

    def _connect(self):
        mode = self.mode_combobox.get()

        if self.serial_manager.is_connected or self.synthetic_generator:
            self.serial_manager.disconnect()
            if self.synthetic_generator:
                self.synthetic_generator.stop_data_generation()
                self.synthetic_generator = None
            self.connect_button.config(text=t("ui.config_tab.connect"))
            self._set_equation_widgets_state("normal")
            self._show_config_interface()
            return

        if mode == "Hardware":
            port = self.port_combobox.get()
            baudrate = self.baudrate_combobox.get()

            if not port:
                return

            if self.serial_manager.connect(port, baudrate):
                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                self._show_connection_info(mode, port, baudrate)

        elif mode == "Synthetic":
            try:
                equations = self._get_equations_from_ui()
                fps = int(self.fps_pref_combobox.get())
                self.synthetic_generator = SyntheticDataGenerator(
                    data_callback=self.serial_manager.data_callback,
                    equations=equations,
                    refresh_rate=fps,
                )

                self.synthetic_generator.start_data_generation()
                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                self._set_equation_widgets_state("disabled")
                self._show_connection_info(mode, "SYNTHETIC_MODE", "N/A")
            except Exception as e:
                print(t("ui.config_tab.mode_synthetic_start_error").format(error=e))

        else:
            print(t("ui.config_tab.mode_unknown_error").format(mode=mode))

    def _show_config_interface(self):
        self.config_frame.grid()
        self.info_frame.grid_remove()
        self.equation_frame.grid_remove
        self._on_mode_changed()

    def _show_connection_info(self, mode, port, baudrate):
        self.config_frame.grid_remove()
        self.info_frame.grid()

        if mode == "Hardware":
            info_text = t("ui.config_tab.connection_status").format(
                mode=t("ui.config_tab.mode_hardware"), port=port, baudrate=baudrate
            )
        elif mode == "Synthetic":
            info_text = t("ui.config_tab.synthetic_connection_status")
        else:
            info_text = t("ui.config_tab.virtual_connection_status").format(
                mode=mode, port=port, baudrate=baudrate
            )

        self.info_label.config(text=info_text)

    def _load_preferences(self):
        saved_mode = self.config_manager.load_tab_setting("config", "mode")
        if saved_mode:
            self.mode_combobox.set(saved_mode)

        saved_baudrate = self.config_manager.load_tab_setting(
            "config", "baudrate", DEFAULT_BAUDRATE
        )
        if saved_baudrate in DEFAULT_BAUDRATES:
            self.baudrate_combobox.set(saved_baudrate)

        saved_port = self.config_manager.load_tab_setting("config", "port")
        if saved_port:
            self._preferred_port = saved_port
        else:
            self._preferred_port = None

        # Load equations
        equations = self.config_manager.load_setting("equations", {})
        if equations:
            self._load_equations_to_ui(equations)

        self._on_mode_changed()

    def _save_preferences(self):
        current_mode = self.mode_combobox.get()

        self.config_manager.save_tab_setting("config", "mode", current_mode)
        self.config_manager.save_tab_setting("config", "port", self.port_combobox.get())
        self.config_manager.save_tab_setting(
            "config", "baudrate", self.baudrate_combobox.get()
        )

        # Save equations
        equations = self._get_equations_from_ui()
        self.config_manager.save_setting("equations", equations)

    def _on_preference_changed(self, event=None):
        self._save_preferences()

    def get_frame(self):
        return self.frame

    def _get_equations_from_ui(self):
        equations = {}
        for label, entry in self.equation_entries.items():
            equation = entry.get().strip()
            if equation:
                equations[label] = equation
        return equations

    def _load_equations_to_ui(self, equations):
        for label, entry in self.equation_entries.items():
            equation = equations.get(label, "")
            entry.delete(0, tk.END)
            entry.insert(0, equation)

    def _on_equation_changed(self, event=None):
        equations = self._get_equations_from_ui()
        self.config_manager.save_setting("equations", equations)

        if self.synthetic_generator and self.synthetic_generator.is_running:
            self.synthetic_generator.set_equations(equations)

    def _set_equation_widgets_state(self, state):
        for entry in self.equation_entries.values():
            entry.config(state=state)
        self.fps_pref_combobox.config(state=state)
