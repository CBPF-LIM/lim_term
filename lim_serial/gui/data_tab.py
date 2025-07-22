"""
Tab de visualização dos dados
"""
import tkinter as tk
from tkinter import ttk
from ..utils import FileManager


class DataTab:
    """Tab de dados"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.data = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Área de texto para dados
        self.data_text = tk.Text(self.frame, wrap="word")
        self.data_text.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Botão de salvar
        self.save_button = ttk.Button(self.frame, text="Salvar", command=self._save_data)
        self.save_button.pack(pady=10)
    
    def add_data(self, line):
        """Adiciona linha de dados"""
        self.data.append({"type": "data", "value": line})
        self.data_text.insert("end", line + "\n")
        # Auto-scroll para o final
        self.data_text.see("end")
    
    def add_message(self, message):
        """Adiciona mensagem (erro, status, etc.)"""
        self.data.append({"type": "msg", "value": message})
        self.data_text.insert("end", message + "\n")
        self.data_text.see("end")
    
    def _save_data(self):
        """Salva os dados em arquivo"""
        # Salva apenas linhas de dados válidos
        valid_lines = [item["value"] for item in self.data if item["type"] == "data"]
        if valid_lines:
            file_path = FileManager.save_data_to_file(valid_lines)
            if file_path:
                self.add_message(f"Dados salvos em: {file_path}")
    
    def get_frame(self):
        """Retorna o frame da tab"""
        return self.frame
    
    def get_data(self):
        """Retorna apenas os dados válidos coletados"""
        return [item["value"] for item in self.data if item["type"] == "data"]
