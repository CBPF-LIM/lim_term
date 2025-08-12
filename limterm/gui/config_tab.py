from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import SyntheticDataGenerator
from ..i18n import t, get_config_manager
import math
from ..utils.ui_builder import build_from_layout_name, build_from_spec


class ConfigTab:
    def __init__(self, parent, serial_manager, signal_handler=None):

        self.frame = build_from_layout_name(parent, "config_tab", self)
        self.serial_manager = serial_manager
        self.signal_handler = signal_handler
        self.synthetic_generator = None
        self.config_manager = get_config_manager()
        self.equation_entries = {}

        self._create_widgets()
        self._update_ports()
        self._load_preferences()

    def _create_widgets(self):

        eq_map = {
            "a": getattr(self, "eq_a", None),
            "b": getattr(self, "eq_b", None),
            "c": getattr(self, "eq_c", None),
            "d": getattr(self, "eq_d", None),
            "e": getattr(self, "eq_e", None),
        }
        self.equation_entries = {k: v for k, v in eq_map.items() if v is not None}

        if hasattr(self, "baudrate_combobox"):
            try:
                self.baudrate_combobox["values"] = DEFAULT_BAUDRATES
                self.baudrate_combobox.set(DEFAULT_BAUDRATE)
            except Exception:
                pass

        if hasattr(self, "math_funcs_text"):
            try:
                math_funcs = [
                    name
                    for name in dir(math)
                    if not name.startswith("_") and callable(getattr(math, name))
                ]
                self.math_funcs_text.delete("1.0", "end")
                self.math_funcs_text.insert("1.0", ", ".join(math_funcs))
                self.math_funcs_text.config(state="disabled")
            except Exception:
                pass

        try:
            if hasattr(self, "mode_frame"):
                spec = {
                    "widget": "Label",
                    "name": "win_simul_info",
                    "options": {
                        "text": "${dialogs.windows_virtual_port_info}",
                        "foreground": "red",
                        "justify": "left",
                        "wraplength": 800,
                    },
                    "layout": {
                        "method": "grid",
                        "column": 0,
                        "row": 10,
                        "columnspan": 2,
                        "padx": 10,
                        "pady": 5,
                        "sticky": "w",
                    },
                }
                build_from_spec(self.mode_frame, spec, self)

                self.win_simul_info.grid_remove()
        except Exception:
            pass

        self.settings_visible = self.config_manager.load_setting(
            "config.ui.settings_visible", False
        )
        if not self.settings_visible and hasattr(self, "settings_frame"):
            try:
                self.settings_frame.grid_remove()
                if hasattr(self, "settings_button"):
                    self.settings_button.config(text=t("ui.config_tab.show_settings"))
            except Exception:
                pass
        else:
            if hasattr(self, "settings_button"):
                self.settings_button.config(text=t("ui.config_tab.hide_settings"))

        self.math_funcs_visible = self.config_manager.load_setting(
            "config.math_functions_visible", False
        )
        self._update_math_functions_visibility()

        try:
            self.frame.columnconfigure(0, weight=1)
            if hasattr(self, "settings_frame"):
                self.settings_frame.columnconfigure(0, weight=1)
            if hasattr(self, "connection_settings_frame"):
                self.connection_settings_frame.columnconfigure(0, weight=1)
            if hasattr(self, "main_container"):
                self.main_container.columnconfigure(0, weight=1)
                self.main_container.columnconfigure(1, weight=1)
            if hasattr(self, "mode_frame"):
                self.mode_frame.columnconfigure(1, weight=1)
            if hasattr(self, "synthetic_frame"):
                self.synthetic_frame.columnconfigure(1, weight=1)
            if hasattr(self, "equations_container"):
                self.equations_container.columnconfigure(1, weight=1)
            if hasattr(self, "port_frame"):
                self.port_frame.columnconfigure(0, weight=1)
        except Exception:
            pass

    def _on_mode_changed(self, event=None):
        mode = self.mode_combobox.get_value()
        if mode == "synthetic":
            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.port_combobox.set("")
            self.baudrate_combobox.set("")

            self.synthetic_frame.grid(
                column=1, row=0, padx=(5, 0), pady=5, sticky="nsew"
            )

            self.synthetic_frame.master.columnconfigure(0, weight=1)
            self.synthetic_frame.master.columnconfigure(1, weight=1)
            if hasattr(self, "win_simul_info"):
                self.win_simul_info.grid_remove()
            self.connect_button.config(
                text=t("ui.config_tab.start_synthetic"), state="normal"
            )
        else:
            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            if hasattr(self, "win_simul_info"):
                self.win_simul_info.grid_remove()

            self.synthetic_frame.grid_remove()

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

            if self.signal_handler:
                self.signal_handler.set_busy(False)

            self.serial_manager.disconnect()
            if self.synthetic_generator:
                self.synthetic_generator.stop_data_generation()
                self.synthetic_generator = None
            self.connect_button.config(text=t("ui.config_tab.connect"))
            self.status_label.config(
                text=f"🔴 {t('ui.config_tab.not_connected')}", foreground="red"
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

                if self.signal_handler:
                    self.signal_handler.set_busy(True)

                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                status_text = t(
                    "ui.config_tab.connected_hardware_status",
                    port=port,
                    baudrate=baudrate,
                )
                self.status_label.config(text=status_text, foreground="black")
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

                if self.signal_handler:
                    self.signal_handler.set_busy(True)

                self.connect_button.config(text=t("ui.config_tab.disconnect"))

                status_text = t("ui.config_tab.connected_synthetic_status", fps=fps)
                self.status_label.config(text=status_text, foreground="black")
                self._set_equation_widgets_state("disabled")
                self._show_connection_info(mode, "SYNTHETIC_MODE", "N/A")
            except Exception as e:
                print(t("ui.config_tab.mode_synthetic_start_error").format(error=e))

        else:
            print(t("ui.config_tab.mode_unknown_error").format(mode=mode))

    def _set_connection_widgets_state(self, state):
        try:

            combo_state = "readonly" if state == "normal" else "disabled"

            if hasattr(self, "mode_combobox"):
                self.mode_combobox.config(state=combo_state)

            if hasattr(self, "port_combobox"):
                self.port_combobox.config(state=combo_state)

            if hasattr(self, "baudrate_combobox"):
                self.baudrate_combobox.config(state=combo_state)

            if hasattr(self, "refresh_button"):
                self.refresh_button.config(state=state)

        except Exception as e:
            print(f"Error setting widget state: {e}")

    def _show_config_interface(self):

        self.mode_frame.grid(column=0, row=0, padx=(0, 5), pady=5, sticky="nsew")
        self._set_connection_widgets_state("normal")
        self._on_mode_changed()

    def _show_connection_info(self, mode, port, baudrate):

        self._set_connection_widgets_state("disabled")

    def _load_preferences(self):

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
            entry.delete(0, "end")
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
