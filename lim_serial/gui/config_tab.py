"""
Tab de configuração da comunicação serial
"""
import tkinter as tk
from tkinter import ttk
from ..config import DEFAULT_BAUDRATES, DEFAULT_BAUDRATE


class ConfigTab:
    """Tab de configuração"""
    
    def __init__(self, parent, serial_manager):
        self.frame = ttk.Frame(parent)
        self.serial_manager = serial_manager
        
        self._create_widgets()
        self._update_ports()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Seleção de porta
        ttk.Label(self.frame, text="Porta:").grid(column=0, row=0, padx=10, pady=10)
        self.port_combobox = ttk.Combobox(self.frame, state="readonly")
        self.port_combobox.grid(column=1, row=0, padx=10, pady=10)
        
        # Seleção de baudrate
        ttk.Label(self.frame, text="Baudrate:").grid(column=0, row=1, padx=10, pady=10)
        self.baudrate_combobox = ttk.Combobox(self.frame, state="readonly", values=DEFAULT_BAUDRATES)
        self.baudrate_combobox.grid(column=1, row=1, padx=10, pady=10)
        self.baudrate_combobox.set(DEFAULT_BAUDRATE)
        
        # Botão de conectar
        self.connect_button = ttk.Button(self.frame, text="Conectar", command=self._connect)
        self.connect_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)
    
    def _update_ports(self):
        """Atualiza lista de portas disponíveis"""
        ports = self.serial_manager.get_available_ports()
        self.port_combobox["values"] = ports
        if ports:
            self.port_combobox.set(ports[0])
    
    def _connect(self):
        """Conecta à porta serial"""
        port = self.port_combobox.get()
        baudrate = self.baudrate_combobox.get()
        
        if not port:
            return
        
        if self.serial_manager.is_connected:
            self.serial_manager.disconnect()
            self.connect_button.config(text="Conectar")
        else:
            if self.serial_manager.connect(port, baudrate):
                self.connect_button.config(text="Desconectar")
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
