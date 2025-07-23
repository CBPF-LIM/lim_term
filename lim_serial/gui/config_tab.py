"""
Tab de configuração da comunicação serial
"""
import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import MockSerial
from ..i18n import t, get_config_manager


class ConfigTab:
    """Tab de configuração"""
    
    def __init__(self, parent, serial_manager):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        self.mock_serial = None
        self.config_manager = get_config_manager()
        
        self._create_widgets()
        self._update_ports()
        self._load_preferences()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Frame para configurações (será ocultado quando conectado)
        self.config_frame = ttk.LabelFrame(self.frame, text=t("ui.config_tab.configuration_frame"))
        self.config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        
        # Seleção de modo (Hardware ou Simulado)
        self.mode_label = ttk.Label(self.config_frame, text=t("ui.config_tab.mode_label"))
        self.mode_label.grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox = ttk.Combobox(self.config_frame, state="readonly", 
                                         values=[t("ui.config_tab.mode_hardware"), t("ui.config_tab.mode_simulated")])
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox.set(t("ui.config_tab.mode_hardware"))
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed, add="+")
        
        # Seleção de porta
        self.port_label = ttk.Label(self.config_frame, text=t("ui.config_tab.port_label"))
        self.port_label.grid(column=0, row=1, padx=10, pady=10, sticky="w")
        
        # Frame para porta e botão refresh
        port_frame = ttk.Frame(self.config_frame)
        port_frame.grid(column=1, row=1, padx=10, pady=10, sticky="w")
        
        self.port_combobox = ttk.Combobox(port_frame, state="readonly")
        self.port_combobox.grid(column=0, row=0, sticky="w")
        self.port_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)
        
        self.refresh_button = ttk.Button(port_frame, text="🔄", width=3, 
                                       command=self._update_ports)
        self.refresh_button.grid(column=1, row=0, padx=(5, 0), sticky="w")
        
        # Configura peso da coluna para expandir o combobox
        port_frame.columnconfigure(0, weight=1)
        
        # Seleção de baudrate
        self.baudrate_label = ttk.Label(self.config_frame, text=t("ui.config_tab.baudrate_label"))
        self.baudrate_label.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox = ttk.Combobox(self.config_frame, state="readonly", 
                                            values=DEFAULT_BAUDRATES)
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        self.baudrate_combobox.bind("<<ComboboxSelected>>", self._on_preference_changed)
        
        # Configura peso das colunas do config_frame
        self.config_frame.columnconfigure(1, weight=1)
        
        # Frame para informações de conexão (será mostrado quando conectado)
        self.info_frame = ttk.LabelFrame(self.frame, text=t("ui.config_tab.connection_info_frame"))
        self.info_frame.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
        
        self.info_label = ttk.Label(self.info_frame, text="", justify="left", 
                                   font=("TkDefaultFont", 9), foreground="darkgreen")
        self.info_label.grid(column=0, row=0, padx=15, pady=15, sticky="w")
        
        # Inicialmente oculta o frame de informações
        self.info_frame.grid_remove()
        
        # Botão de conectar (sempre visível)
        self.connect_button = ttk.Button(self.frame, text=t("ui.config_tab.connect"), command=self._connect)
        self.connect_button.grid(column=0, row=2, padx=10, pady=10, sticky="w")
        
        # Configura peso das colunas
        self.frame.columnconfigure(0, weight=1)
    
    def _on_mode_changed(self, event=None):
        """Callback para mudança de modo"""
        mode = self.mode_combobox.get()
        if mode == t("ui.config_tab.mode_simulated"):
            # Desabilita seleção de porta e baudrate para modo simulado
            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
            self.port_combobox.set("")
            self.baudrate_combobox.set("")
        else:
            # Habilita seleção para modo hardware
            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            # Se baudrate estiver vazio, seleciona o primeiro
            if not self.baudrate_combobox.get():
                if hasattr(self.baudrate_combobox, 'config'):
                    self.baudrate_combobox.set(DEFAULT_BAUDRATES[0])
            self._update_ports()
    
    def _update_ports(self):
        """Atualiza lista de portas disponíveis"""
        if self.mode_combobox.get() == t("ui.config_tab.mode_hardware"):
            ports = self.serial_manager.get_available_ports()
            self.port_combobox["values"] = ports
            if ports:
                # Try to apply preferred port if it exists in the list
                if hasattr(self, '_preferred_port') and self._preferred_port and self._preferred_port in ports:
                    self.port_combobox.set(self._preferred_port)
                else:
                    self.port_combobox.set(ports[0])
    
    def _connect(self):
        """Conecta à porta serial"""
        mode = self.mode_combobox.get()
        
        if self.serial_manager.is_connected:
            # Desconectar
            self.serial_manager.disconnect()
            if self.mock_serial:
                self.mock_serial.stop_data_generation()
                self.mock_serial = None
            self.connect_button.config(text=t("ui.config_tab.connect"))
            self._show_config_interface()
            return
        
        # Conectar
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
                # Cria porta virtual
                self.mock_serial = MockSerial()
                virtual_port = self.mock_serial.create_virtual_port()
                
                # Conecta à porta virtual
                if self.serial_manager.connect(virtual_port, DEFAULT_BAUDRATE):
                    self.mock_serial.start_data_generation()
                    self.connect_button.config(text=t("ui.config_tab.disconnect"))
                    self._show_connection_info(mode, virtual_port, DEFAULT_BAUDRATE)
                    
                    # Atualiza a lista de portas para mostrar a porta virtual
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
        """Mostra a interface de configuração e oculta as informações"""
        self.config_frame.grid()
        self.info_frame.grid_remove()
        self._on_mode_changed()  # Reabilita controles conforme o modo
    
    def _show_connection_info(self, mode, port, baudrate):
        """Mostra informações da conexão e oculta a interface de configuração"""
        self.config_frame.grid_remove()
        self.info_frame.grid()
        
        # Constrói texto informativo
        if mode == t("ui.config_tab.mode_hardware"):
            info_text = t("ui.config_tab.connection_status").format(
                mode=mode, port=port, baudrate=baudrate)
        else:
            info_text = t("ui.config_tab.virtual_connection_status").format(
                mode=mode, port=port, baudrate=baudrate)
        
        self.info_label.config(text=info_text)
    
    def refresh_translations(self):
        """Atualiza as traduções na interface"""
        # Atualiza textos dos frames
        self.config_frame.config(text=t("ui.config_tab.configuration_frame"))
        self.info_frame.config(text=t("ui.config_tab.connection_info_frame"))
        
        # Atualiza labels estáticos
        self.mode_label.config(text=t("ui.config_tab.mode_label"))
        self.port_label.config(text=t("ui.config_tab.port_label"))
        self.baudrate_label.config(text=t("ui.config_tab.baudrate_label"))
        
        # Atualiza botão de conectar
        if self.serial_manager.is_connected:
            self.connect_button.config(text=t("ui.config_tab.disconnect"))
        else:
            self.connect_button.config(text=t("ui.config_tab.connect"))
        
        # Atualiza valores do combobox de modo
        current_mode = self.mode_combobox.get()
        mode_values = [t("ui.config_tab.mode_hardware"), t("ui.config_tab.mode_simulated")]
        self.mode_combobox["values"] = mode_values
        
        # Redefine valor atual traduzido
        if "Hardware" in current_mode or current_mode == t("ui.config_tab.mode_hardware"):
            self.mode_combobox.set(t("ui.config_tab.mode_hardware"))
        else:
            self.mode_combobox.set(t("ui.config_tab.mode_simulated"))
        
        # Atualiza info se conectado
        if self.serial_manager.is_connected:
            mode = self.mode_combobox.get()
            port = self.port_combobox.get() if hasattr(self, 'port_combobox') else ""
            baudrate = self.baudrate_combobox.get() if hasattr(self, 'baudrate_combobox') else ""
            self._show_connection_info(mode, port, baudrate)
    
    def _load_preferences(self):
        """Load saved preferences"""
        # Load mode preference
        saved_mode = self.config_manager.load_tab_setting('config', 'mode')
        if saved_mode:
            if saved_mode == "Hardware":
                self.mode_combobox.set(t("ui.config_tab.mode_hardware"))
            elif saved_mode == "Simulated":
                self.mode_combobox.set(t("ui.config_tab.mode_simulated"))
        
        # Load baudrate preference
        saved_baudrate = self.config_manager.load_tab_setting('config', 'baudrate', DEFAULT_BAUDRATE)
        if saved_baudrate in DEFAULT_BAUDRATES:
            self.baudrate_combobox.set(saved_baudrate)
        
        # Load port preference (with safe loading)
        saved_port = self.config_manager.load_tab_setting('config', 'port')
        if saved_port:
            # Will be applied in _update_ports after ports are loaded
            self._preferred_port = saved_port
        else:
            self._preferred_port = None
        
        # Apply mode changes
        self._on_mode_changed()
    
    def _save_preferences(self):
        """Save current preferences"""
        # Save mode (convert from translated to English)
        current_mode = self.mode_combobox.get()
        if current_mode == t("ui.config_tab.mode_hardware"):
            mode_value = "Hardware"
        elif current_mode == t("ui.config_tab.mode_simulated"):
            mode_value = "Simulated"
        else:
            mode_value = "Hardware"  # default
        
        self.config_manager.save_tab_setting('config', 'mode', mode_value)
        self.config_manager.save_tab_setting('config', 'port', self.port_combobox.get())
        self.config_manager.save_tab_setting('config', 'baudrate', self.baudrate_combobox.get())
    
    def _on_preference_changed(self, event=None):
        """Called when any preference changes"""
        self._save_preferences()
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
