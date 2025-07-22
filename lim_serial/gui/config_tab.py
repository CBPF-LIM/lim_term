"""
Tab de configuração da comunicação serial
"""
import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE
from ..utils import MockSerial


class ConfigTab:
    """Tab de configuração"""
    
    def __init__(self, parent, serial_manager):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        self.mock_serial = None
        
        self._create_widgets()
        self._update_ports()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Frame para configurações (será ocultado quando conectado)
        self.config_frame = ttk.LabelFrame(self.frame, text="Configuração")
        self.config_frame.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        
        # Seleção de modo (Hardware ou Simulado)
        ttk.Label(self.config_frame, text="Modo:").grid(column=0, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox = ttk.Combobox(self.config_frame, state="readonly", 
                                         values=["Hardware", "Simulado"])
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10, sticky="w")
        self.mode_combobox.set("Hardware")
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_changed)
        
        # Seleção de porta
        ttk.Label(self.config_frame, text="Porta:").grid(column=0, row=1, padx=10, pady=10, sticky="w")
        
        # Frame para porta e botão refresh
        port_frame = ttk.Frame(self.config_frame)
        port_frame.grid(column=1, row=1, padx=10, pady=10, sticky="w")
        
        self.port_combobox = ttk.Combobox(port_frame, state="readonly")
        self.port_combobox.grid(column=0, row=0, sticky="w")
        
        self.refresh_button = ttk.Button(port_frame, text="🔄", width=3, 
                                       command=self._update_ports)
        self.refresh_button.grid(column=1, row=0, padx=(5, 0), sticky="w")
        
        # Configura peso da coluna para expandir o combobox
        port_frame.columnconfigure(0, weight=1)
        
        # Seleção de baudrate
        ttk.Label(self.config_frame, text="Baudrate:").grid(column=0, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox = ttk.Combobox(self.config_frame, state="readonly", 
                                            values=DEFAULT_BAUDRATES)
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10, sticky="w")
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        
        # Configura peso das colunas do config_frame
        self.config_frame.columnconfigure(1, weight=1)
        
        # Frame para informações de conexão (será mostrado quando conectado)
        self.info_frame = ttk.LabelFrame(self.frame, text="Informações da Conexão")
        self.info_frame.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
        
        self.info_label = ttk.Label(self.info_frame, text="", justify="left", 
                                   font=("TkDefaultFont", 9), foreground="darkgreen")
        self.info_label.grid(column=0, row=0, padx=15, pady=15, sticky="w")
        
        # Inicialmente oculta o frame de informações
        self.info_frame.grid_remove()
        
        # Botão de conectar (sempre visível)
        self.connect_button = ttk.Button(self.frame, text="Conectar", command=self._connect)
        self.connect_button.grid(column=0, row=2, padx=10, pady=10)
        
        # Configura peso das colunas
        self.frame.columnconfigure(0, weight=1)
    
    def _on_mode_changed(self, event=None):
        """Callback para mudança de modo"""
        mode = self.mode_combobox.get()
        
        if mode == "Simulado":
            # Desabilita seleção de porta e baudrate para modo simulado
            self.port_combobox.config(state="disabled")
            self.baudrate_combobox.config(state="disabled")
            self.refresh_button.config(state="disabled")
        else:
            # Habilita seleção para modo hardware
            self.port_combobox.config(state="readonly")
            self.baudrate_combobox.config(state="readonly")
            self.refresh_button.config(state="normal")
            self._update_ports()
    
    def _update_ports(self):
        """Atualiza lista de portas disponíveis"""
        if self.mode_combobox.get() == "Hardware":
            ports = self.serial_manager.get_available_ports()
            self.port_combobox["values"] = ports
            if ports:
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
            self.connect_button.config(text="Conectar")
            self._show_config_interface()
            return
        
        # Conectar
        if mode == "Hardware":
            port = self.port_combobox.get()
            baudrate = self.baudrate_combobox.get()
            
            if not port:
                return
            
            if self.serial_manager.connect(port, baudrate):
                self.connect_button.config(text="Desconectar")
                self._show_connection_info(mode, port, baudrate)
                
        elif mode == "Simulado":
            try:
                # Cria porta virtual
                self.mock_serial = MockSerial()
                virtual_port = self.mock_serial.create_virtual_port()
                
                # Conecta à porta virtual
                if self.serial_manager.connect(virtual_port, DEFAULT_BAUDRATE):
                    self.mock_serial.start_data_generation()
                    self.connect_button.config(text="Desconectar")
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
                print(f"Erro ao criar porta simulada: {e}")
    
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
        info_text = f"🔗 Modo: {mode}\n"
        if mode == "Hardware":
            info_text += f"📡 Porta: {port}\n"
            info_text += f"⚡ Baudrate: {baudrate} bps"
        else:
            info_text += f"🖥️  Porta Virtual: {port}\n"
            info_text += f"⚡ Baudrate: {baudrate} bps (automático)\n"
            info_text += f"📊 Status: Gerando dados simulados"
        
        self.info_label.config(text=info_text)
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
