"""
Tab de visualização dos dados
"""
import tkinter as tk
from tkinter import ttk
from ..utils import FileManager


class DataTab:
    def _on_user_scroll(self, event=None):
        """Atualiza autoscroll flag conforme posição do scroll"""
        self.autoscroll = self._is_scrolled_to_end()
    """Tab de dados"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.data = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tab"""
        # Frame para área de texto e scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(expand=1, fill="both", padx=10, pady=10)
        
        # Área de texto para dados
        self.data_text = tk.Text(text_frame, wrap="word")
        self.data_text.pack(side="left", expand=1, fill="both")
        
        # Scrollbar vertical
        self.scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.data_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.data_text.config(yscrollcommand=self.scrollbar.set)
        
        # Botão de salvar
        self.save_button = ttk.Button(self.frame, text="Salvar", command=self._save_data)
        self.save_button.pack(pady=10)
        
        # Autoscroll flag
        self.autoscroll = True
        self.data_text.bind("<Button-1>", self._on_user_scroll)
        self.data_text.bind("<MouseWheel>", self._on_user_scroll)
        self.data_text.bind("<Key>", self._on_user_scroll)
        self.data_text.bind("<ButtonRelease-1>", self._on_user_scroll)
        self.data_text.bind("<Configure>", self._on_user_scroll)
    
    def add_data(self, line):
        """Adiciona linha de dados"""
        self.data.append({"type": "data", "value": line})
        # Verifica se o usuário está no final antes de inserir
        at_end = self._is_scrolled_to_end()
        self.data_text.insert("end", line + "\n")
        if at_end:
            self.data_text.see("end")
    
    def add_message(self, message):
        """Adiciona mensagem (erro, status, etc.)"""
        self.data.append({"type": "msg", "value": message})
        at_end = self._is_scrolled_to_end()
        self.data_text.insert("end", message + "\n")
        if at_end:
            self.data_text.see("end")
    def _is_scrolled_to_end(self):
        """Retorna True se o usuário está no final do texto"""
        # Obtém a posição do último caractere visível
        last_visible = self.data_text.index("@0,%d" % self.data_text.winfo_height())
        end_index = self.data_text.index("end-1c")
        # Se o último visível está próximo do fim, considera que está no final
        return last_visible >= end_index
    
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
