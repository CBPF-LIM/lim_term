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
        # Seleção de modo (Hardware ou Simulado)
        ttk.Label(self.frame, text="Modo:").grid(column=0, row=0, padx=10, pady=10)
        self.mode_combobox = ttk.Combobox(self.frame, state="readonly", 
                                         values=["Hardware", "Simulado"])
        self.mode_combobox.grid(column=1, row=0, padx=10, pady=10)
        self.mode_combobox.set("Hardware")
        self.mode_combobox.bind("<<ComboboxSelected>>", self._on_mode_changed)
        
        # Seleção de porta
        ttk.Label(self.frame, text="Porta:").grid(column=0, row=1, padx=10, pady=10)
        
        # Frame para porta e botão refresh
        port_frame = ttk.Frame(self.frame)
        port_frame.grid(column=1, row=1, padx=10, pady=10, sticky="ew")
        
        self.port_combobox = ttk.Combobox(port_frame, state="readonly")
        self.port_combobox.grid(column=0, row=0, sticky="ew")
        
        self.refresh_button = ttk.Button(port_frame, text="🔄", width=3, 
                                       command=self._update_ports)
        self.refresh_button.grid(column=1, row=0, padx=(5, 0))
        
        # Configura peso da coluna para expandir o combobox
        port_frame.columnconfigure(0, weight=1)
        
        # Seleção de baudrate
        ttk.Label(self.frame, text="Baudrate:").grid(column=0, row=2, padx=10, pady=10)
        self.baudrate_combobox = ttk.Combobox(self.frame, state="readonly", 
                                            values=DEFAULT_BAUDRATES)
        self.baudrate_combobox.grid(column=1, row=2, padx=10, pady=10)
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        
        # Botão de conectar
        self.connect_button = ttk.Button(self.frame, text="Conectar", command=self._connect)
        self.connect_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)
        
        # Configura peso das colunas
        self.frame.columnconfigure(1, weight=1)
    
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
            self._on_mode_changed()  # Reabilita controles
            return
        
        # Conectar
        if mode == "Hardware":
            port = self.port_combobox.get()
            baudrate = self.baudrate_combobox.get()
            
            if not port:
                return
            
            if self.serial_manager.connect(port, baudrate):
                self.connect_button.config(text="Desconectar")
                
        elif mode == "Simulado":
            try:
                # Cria porta virtual
                self.mock_serial = MockSerial()
                virtual_port = self.mock_serial.create_virtual_port()
                
                # Conecta à porta virtual
                if self.serial_manager.connect(virtual_port, DEFAULT_BAUDRATE):
                    self.mock_serial.start_data_generation()
                    self.connect_button.config(text="Desconectar")
                    
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
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
