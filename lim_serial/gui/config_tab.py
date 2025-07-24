import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import MockSerial
from ..i18n import t, get_config_manager
import platform


class ConfigTab:


    def __init__(self, parent, serial_manager):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        self.mock_serial = None
        self.config_manager = get_config_manager()

        self._create_widgets()
        self._update_ports()
        self._load_preferences()

    def _create_widgets(self):


        self.config_frame = ttk.LabelFrame(self.frame, text=t("ui.config_tab.configuration_frame"))
        self.config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="ew")


        self.mode_label = ttk.Label(self.config_frame, text=t("ui.config_tab.mode_label"))
        self.mode_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox = ttk.Combobox(self.config_frame, state="readonly",
                                         values=[t("ui.config_tab.mode_hardware"), t("ui.config_tab.mode_simulated")])
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox.set(t("ui.config_tab.mode_hardware"))
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed, add="+")


        self.port_label = ttk.Label(self.config_frame, text=t("ui.config_tab.port_label"))
        self.port_label.grid(column=0, row=1, padx=10, pady=10, sticky="w")


        port_frame = ttk.Frame(self.config_frame)
        port_frame.grid(column=1, row=1, padx=10, pady=10, sticky="w")

        self.port_combobox = ttk.Combobox(port_frame, state="readonly")
        self.port_combobox.grid(column=0, row=0, sticky="w")
        self.port_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)

        self.refresh_button = ttk.Button(port_frame, text="🔄", width=3,
                                       command=self._update_ports)
        self.refresh_button.grid(column=1, row=0, padx=(5, 0))


        port_frame.columnconfigure(0, weight=1)


        self.baudrate_label = ttk.Label(self.config_frame, text=t("ui.config_tab.baudrate_label"))
        self.baudrate_label.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox = ttk.Combobox(self.config_frame, state="readonly",
                                            values=DEFAULT_BAUDRATES)
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        self.baudrate_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)


        self.config_frame.columnconfigure(1, weight=1)


        self.info_frame = ttk.LabelFrame(self.frame, text=t("ui.config_tab.connection_info_frame"))
        self.info_frame.grid(column=0, row=1, padx=10, pady=10, sticky="ew")

        self.info_label = ttk.Label(self.info_frame, text="", justify="left",
                                   font=("TkDefaultFont", 9), foreground="darkgreen")
        self.info_label.grid(column=0, row=0, padx=15, pady=15, sticky="w")


        self.info_frame.grid_remove()


        self.connect_button = ttk.Button(self.frame, text=t("ui.config_tab.connect"), command=self._connect)
        self.connect_button.grid(column=0, row=2, padx=10, pady=10, sticky="w")


        self.frame.columnconfigure(0, weight=1)

        # Add the win_simul_info as a selectable, read-only Text widget (initially hidden)
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
            highlightthickness=0
        )
        self.win_simul_info.insert(
            "1.0",
            "To simulate a virtual serial port on Windows, install the Null-modem emulator (com0com: https://com0com.sourceforge.net/).\nAfter configuration, select 'Hardware' mode and choose the created COM port."
        )
        self.win_simul_info.config(state="disabled")
        self.win_simul_info.grid(column=0, row=10, columnspan=2, padx=10, pady=5, sticky="w")
        self.win_simul_info.grid_remove()

    def _on_mode_changed(self, event=None):

        mode = self.mode_combobox.get()
        if mode == t("ui.config_tab.mode_simulated"):

            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.port_combobox.set("")
            self.baudrate_combobox.set("")
            # Show Windows info if on Windows
            if platform.system() == "Windows":
                self.win_simul_info.grid()
                self.win_simul_info.config(state="normal")
                self.win_simul_info.tag_add("all", "1.0", "end")
                self.win_simul_info.config(state="disabled")
                self.connect_button.config(state="disabled")
            else:
                self.win_simul_info.grid_remove()
                self.connect_button.config(state="normal")
        else:

            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            self.win_simul_info.grid_remove()
            self.connect_button.config(state="normal")

            if not self.baudrate_combobox.get():
                if hasattr(self.baudrate_combobox, 'config'):
                    self.baudrate_combobox.set(DEFAULT_BAUDRATES[0])
            self._update_ports()

    def _update_ports(self):

        if self.mode_combobox.get() == t("ui.config_tab.mode_hardware"):
            ports = self.serial_manager.get_available_ports()
            self.port_combobox["values"] = ports
            if ports:

                if hasattr(self, '_preferred_port') and self._preferred_port and self._preferred_port in ports:
                    self.port_combobox.set(self._preferred_port)
                else:
                    self.port_combobox.set(ports[0])

    def _connect(self):

        mode = self.mode_combobox.get()

        if self.serial_manager.is_connected:

            self.serial_manager.disconnect()
            if self.mock_serial:
                self.mock_serial.stop_data_generation()
                self.mock_serial = None
            self.connect_button.config(text=t("ui.config_tab.connect"))
            self._show_config_interface()
            return


        if mode == t("ui.config_tab.mode_hardware"):
            port = self.port_combobox.get()
            baudrate = self.baudrate_combobox.get()

            if not port:
                return

            if self.serial_manager.connect(port, baudrate):
                self.connect_button.config(text=t("ui.config_tab.disconnect"))
                self._show_connection_info(mode, port, baudrate)

        elif mode == t("ui.config_tab.mode_simulated"):
            try:

                self.mock_serial = MockSerial()
                virtual_port = self.mock_serial.create_virtual_port()


                if self.serial_manager.connect(virtual_port, DEFAULT_BAUDRATE):
                    self.mock_serial.start_data_generation()
                    self.connect_button.config(text=t("ui.config_tab.disconnect"))
                    self._show_connection_info(mode, virtual_port, DEFAULT_BAUDRATE)


                    current_ports = list(self.port_combobox["values"])
                    if virtual_port not in current_ports:
                        current_ports.append(f"{virtual_port} (Virtual)")
                        self.port_combobox["values"] = current_ports
                        self.port_combobox.set(f"{virtual_port} (Virtual)")
                else:
                    self.mock_serial.stop_data_generation()
                    self.mock_serial = None

            except Exception as e:
                print(t("errors.virtual_port_error").format(error=e))

    def _show_config_interface(self):

        self.config_frame.grid()
        self.info_frame.grid_remove()
        self._on_mode_changed()

    def _show_connection_info(self, mode, port, baudrate):

        self.config_frame.grid_remove()
        self.info_frame.grid()


        if mode == t("ui.config_tab.mode_hardware"):
            info_text = t("ui.config_tab.connection_status").format(
                mode=mode, port=port, baudrate=baudrate)
        else:
            info_text = t("ui.config_tab.virtual_connection_status").format(
                mode=mode, port=port, baudrate=baudrate)

        self.info_label.config(text=info_text)

    def _load_preferences(self):


        saved_mode = self.config_manager.load_tab_setting('config', 'mode')
        if saved_mode:
            if saved_mode == "Hardware":
                self.mode_combobox.set(t("ui.config_tab.mode_hardware"))
            elif saved_mode == "Simulated":
                self.mode_combobox.set(t("ui.config_tab.mode_simulated"))


        saved_baudrate = self.config_manager.load_tab_setting('config', 'baudrate', DEFAULT_BAUDRATE)
        if saved_baudrate in DEFAULT_BAUDRATES:
            self.baudrate_combobox.set(saved_baudrate)


        saved_port = self.config_manager.load_tab_setting('config', 'port')
        if saved_port:

            self._preferred_port = saved_port
        else:
            self._preferred_port = None


        self._on_mode_changed()

    def _save_preferences(self):


        current_mode = self.mode_combobox.get()
        if current_mode == t("ui.config_tab.mode_hardware"):
            mode_value = "Hardware"
        elif current_mode == t("ui.config_tab.mode_simulated"):
            mode_value = "Simulated"
        else:
            mode_value = "Hardware"

        self.config_manager.save_tab_setting('config', 'mode', mode_value)
        self.config_manager.save_tab_setting('config', 'port', self.port_combobox.get())
        self.config_manager.save_tab_setting('config', 'baudrate', self.baudrate_combobox.get())

    def _on_preference_changed(self, event=None):

        self._save_preferences()

    def get_frame(self):

        return self.frame
