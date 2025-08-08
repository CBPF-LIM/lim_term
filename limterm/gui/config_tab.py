import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import SyntheticDataGenerator
from ..i18n import t, get_config_manager
from .preference_widgets import PrefCombobox
import platform
import math


class ConfigTab:
    def __init__(self, parent, serial_manager, signal_handler=None):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        self.signal_handler = signal_handler
        self.synthetic_generator = None
        self.config_manager = get_config_manager()
        self.equation_entries = {}

        self._create_widgets()
        self._update_ports()
        self._load_preferences()

    def _create_widgets(self):
        toggle_frame = ttk.Frame(self.frame)
        toggle_frame.grid(column=0, row=0, padx=10, pady=5, sticky="ew")
        toggle_frame.columnconfigure(0, weight=1)

        button_container = ttk.Frame(toggle_frame)
        button_container.grid(column=0, row=0, sticky="w")

        self.connect_button = ttk.Button(
            button_container, text=t("ui.config_tab.connect"), command=self._connect
        )
        self.connect_button.pack(side="left")

        self.settings_button = ttk.Button(
            toggle_frame,
            text=t("ui.config_tab.show_settings"),
            command=self._toggle_settings,
        )
        self.settings_button.grid(column=1, row=0, sticky="e")

        self.info_frame = ttk.LabelFrame(self.frame, text=t("ui.config_tab.status"))
        self.info_frame.grid(column=0, row=1, padx=10, pady=5, sticky="ew")

        self.status_label = ttk.Label(
            self.info_frame, text=t("ui.config_tab.not_connected"), foreground="red"
        )
        self.status_label.pack(padx=10, pady=5)

        self.settings_frame = ttk.Frame(self.frame)
        self.settings_frame.grid(column=0, row=2, padx=10, pady=5, sticky="ew")

        # Connection Settings parent frame
        connection_settings_frame = ttk.LabelFrame(
            self.settings_frame, text=t("ui.config_tab.connection_settings")
        )
        connection_settings_frame.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        # Main container for side-by-side layout (line 1: Mode | Synthetic)
        main_container = ttk.Frame(connection_settings_frame)
        main_container.grid(column=0, row=0, sticky="ew", padx=5, pady=5)

        # Mode frame (left side) - make stretchable
        self.mode_frame = ttk.LabelFrame(main_container, text=t("ui.config_tab.mode"))
        self.mode_frame.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="nsew")

        self.mode_label = ttk.Label(self.mode_frame, text=t("ui.config_tab.mode_label"))
        self.mode_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox = PrefCombobox(
            self.mode_frame,
            pref_key="config.mode",
            default_value="hardware",
            state="readonly",
            values=[t("common.hardware"), t("common.synthetic")],
            value_mapping={
                t("common.hardware"): "hardware",
                t("common.synthetic"): "synthetic",
            },
            on_change=self._on_mode_changed,
        )
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10, sticky="w")

        self.port_label = ttk.Label(self.mode_frame, text=t("ui.config_tab.port_label"))
        self.port_label.grid(column=0, row=1, padx=10, pady=10, sticky="w")

        port_frame = ttk.Frame(self.mode_frame)
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
            self.mode_frame, text=t("ui.config_tab.baudrate_label")
        )
        self.baudrate_label.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox = ttk.Combobox(
            self.mode_frame, state="readonly", values=DEFAULT_BAUDRATES
        )
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        self.baudrate_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)

        self.mode_frame.columnconfigure(1, weight=1)

        # Synthetic Settings frame (right side) - make stretchable
        self.synthetic_frame = ttk.LabelFrame(
            main_container, text=t("ui.config_tab.synthetic_settings")
        )
        self.synthetic_frame.grid(column=1, row=0, padx=(5, 0), pady=5, sticky="nsew")

        self.fps_label = ttk.Label(self.synthetic_frame, text="FPS:")
        self.fps_label.grid(column=0, row=0, padx=5, pady=5, sticky="w")

        fps_frame = ttk.Frame(self.synthetic_frame)
        fps_frame.grid(column=1, row=0, padx=5, pady=5, sticky="ew")

        self.fps_pref_combobox = PrefCombobox(
            fps_frame,
            pref_key="graph.general.refresh_rate",
            default_value="10",
            state="readonly",
            values=[str(i) for i in range(1, 31)],
            width=8,
        )
        self.fps_pref_combobox.pack(side="left")

        # Add math functions toggle button next to FPS
        self.math_funcs_button = ttk.Button(
            fps_frame,
            text=t("ui.config_tab.show_math_functions"),
            command=self._toggle_math_functions,
        )
        self.math_funcs_button.pack(side="right")

        self.equation_labels = ["a", "b", "c", "d", "e"]
        for i, label in enumerate(self.equation_labels):
            col_label = ttk.Label(self.synthetic_frame, text=f"{label}:")
            col_label.grid(column=0, row=i + 1, padx=5, pady=5, sticky="w")

            equation_entry = ttk.Entry(self.synthetic_frame, width=40)
            equation_entry.grid(column=1, row=i + 1, padx=5, pady=5, sticky="ew")
            equation_entry.bind("<KeyRelease>", self._on_equation_changed)
            self.equation_entries[label] = equation_entry

        self.synthetic_frame.columnconfigure(1, weight=1)
        fps_frame.columnconfigure(0, weight=1)

        # Math functions frame at the bottom (line 2: Functions) - simplified
        self.math_functions_frame = ttk.LabelFrame(
            connection_settings_frame, text=t("ui.config_tab.available_math_functions")
        )
        # Don't grid it initially - let _update_math_functions_visibility handle it

        self.math_funcs_text = tk.Text(
            self.math_functions_frame, height=4, width=80, wrap="word"
        )
        math_funcs = [
            name
            for name in dir(math)
            if not name.startswith("_") and callable(getattr(math, name))
        ]
        math_funcs_text = ", ".join(math_funcs)
        self.math_funcs_text.insert("1.0", math_funcs_text)
        self.math_funcs_text.config(state="disabled")
        self.math_funcs_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Initialize math functions visibility
        self.math_funcs_visible = self.config_manager.load_setting(
            "config.math_functions_visible", False
        )
        self._update_math_functions_visibility()

        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        connection_settings_frame.columnconfigure(0, weight=1)
        self.settings_frame.columnconfigure(0, weight=1)

        self.settings_visible = self.config_manager.load_setting(
            "config.ui.settings_visible", False
        )

        if not self.settings_visible:
            self.settings_frame.grid_remove()
            self.settings_button.config(text=t("ui.config_tab.show_settings"))
        else:
            self.settings_button.config(text=t("ui.config_tab.hide_settings"))

        self.frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        frame_bg = style.lookup("TLabelframe", "background")
        self.win_simul_info = tk.Text(
            self.mode_frame,
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
            t("dialogs.windows_virtual_port_info"),
        )
        self.win_simul_info.config(state="disabled")
        self.win_simul_info.grid(
            column=0, row=10, columnspan=2, padx=10, pady=5, sticky="w"
        )
        self.win_simul_info.grid_remove()

    def _on_mode_changed(self, event=None):
        mode = self.mode_combobox.get_value()
        if mode == "synthetic":
            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.port_combobox.set("")
            self.baudrate_combobox.set("")
            # Show synthetic frame when in synthetic mode (50/50 split)
            self.synthetic_frame.grid(
                column=1, row=0, padx=(5, 0), pady=5, sticky="nsew"
            )
            # Reset column weights to 50/50
            self.synthetic_frame.master.columnconfigure(0, weight=1)
            self.synthetic_frame.master.columnconfigure(1, weight=1)
            self.win_simul_info.grid_remove()
            self.connect_button.config(
                text=t("ui.config_tab.start_synthetic"), state="normal"
            )
        else:
            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            self.win_simul_info.grid_remove()
            # Hide synthetic frame when in hardware mode
            self.synthetic_frame.grid_remove()
            # Make mode frame take full width (100%)
            self.mode_frame.master.columnconfigure(0, weight=1)
            self.mode_frame.master.columnconfigure(1, weight=0)
            self.connect_button.config(text=t("ui.config_tab.connect"), state="normal")
            self.connect_button.config(state="normal")

            if not self.baudrate_combobox.get():
                if hasattr(self.baudrate_combobox, "config"):
                    self.baudrate_combobox.set(DEFAULT_BAUDRATES[0])
            self._update_ports()

    def _update_ports(self):
        if self.mode_combobox.get_value() == "hardware":
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
        mode = self.mode_combobox.get_value()

        if self.serial_manager.is_connected or self.synthetic_generator:
            # Disconnecting - set not busy
            if self.signal_handler:
                self.signal_handler.set_busy(False)

            self.serial_manager.disconnect()
            if self.synthetic_generator:
                self.synthetic_generator.stop_data_generation()
                self.synthetic_generator = None
            self.connect_button.config(text=t("ui.config_tab.connect"))
            self.status_label.config(
                text=t("ui.config_tab.not_connected"), foreground="red"
            )
            self._set_equation_widgets_state("normal")
            self._show_config_interface()
            return

        if mode == "hardware":
            port = self.port_combobox.get()
            baudrate = self.baudrate_combobox.get()

            if not port:
                return

            if self.serial_manager.connect(port, baudrate):
                # Connected - set busy
                if self.signal_handler:
                    self.signal_handler.set_busy(True)

                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                self.status_label.config(
                    text=t("ui.config_tab.connected"), foreground="green"
                )
                self._show_connection_info(mode, port, baudrate)

        elif mode == "synthetic":
            try:
                equations = self._get_equations_from_ui()
                fps = int(self.fps_pref_combobox.get())
                self.synthetic_generator = SyntheticDataGenerator(
                    data_callback=self.serial_manager.data_callback,
                    equations=equations,
                    refresh_rate=fps,
                )

                self.synthetic_generator.start_data_generation()

                # Synthetic mode started - set busy
                if self.signal_handler:
                    self.signal_handler.set_busy(True)

                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                self.status_label.config(
                    text=t("ui.config_tab.connected"), foreground="green"
                )
                self._set_equation_widgets_state("disabled")
                self._show_connection_info(mode, "SYNTHETIC_MODE", "N/A")
            except Exception as e:
                print(t("ui.config_tab.mode_synthetic_start_error").format(error=e))

        else:
            print(t("ui.config_tab.mode_unknown_error").format(mode=mode))

    def _show_config_interface(self):
        # Keep frames in their proper side-by-side positions
        self._on_mode_changed()

    def _show_connection_info(self, mode, port, baudrate):
        self.mode_frame.grid_remove()

    def _load_preferences(self):
        # Note: mode is automatically loaded by PrefCombobox, don't override it

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

        equations = self.config_manager.load_setting("equations", {})
        if equations:
            self._load_equations_to_ui(equations)

        self._on_mode_changed()

    def _save_preferences(self):
        current_mode = self.mode_combobox.get_value()

        self.config_manager.save_tab_setting("config", "mode", current_mode)
        self.config_manager.save_tab_setting("config", "port", self.port_combobox.get())
        self.config_manager.save_tab_setting(
            "config", "baudrate", self.baudrate_combobox.get()
        )

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

    def _toggle_math_functions(self):
        self.math_funcs_visible = not self.math_funcs_visible
        self.config_manager.save_setting(
            "config.math_functions_visible", self.math_funcs_visible
        )
        self._update_math_functions_visibility()

    def _toggle_settings(self):
        """Toggle the visibility of the settings frame."""
        if self.settings_visible:
            self.settings_frame.grid_remove()
            self.settings_button.config(text=t("ui.config_tab.show_settings"))
            self.settings_visible = False
        else:
            self.settings_frame.grid()
            self.settings_button.config(text=t("ui.config_tab.hide_settings"))
            self.settings_visible = True

        self.config_manager.save_setting(
            "config.ui.settings_visible", self.settings_visible
        )

    def _update_math_functions_visibility(self):
        if self.math_funcs_visible:
            self.math_functions_frame.grid(column=0, row=1, padx=5, pady=5, sticky="ew")
            self.math_funcs_button.config(text=t("ui.config_tab.hide_math_functions"))
        else:
            self.math_functions_frame.grid_remove()
            self.math_funcs_button.config(text=t("ui.config_tab.show_math_functions"))
