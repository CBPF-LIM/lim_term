import tkinter as tk
from tkinter import ttk, filedialog
import serial
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class SerialGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Port GUI")

        self.serial_port = None
        self.data = []

        # Tabs
        self.tab_control = ttk.Notebook(root)

        self.config_tab = ttk.Frame(self.tab_control)
        self.data_tab = ttk.Frame(self.tab_control)
        self.graph_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.config_tab, text="Configuração")
        self.tab_control.add(self.data_tab, text="Dados")
        self.tab_control.add(self.graph_tab, text="Gráfico")

        self.tab_control.pack(expand=1, fill="both")

        self.setup_config_tab()
        self.setup_data_tab()
        self.setup_graph_tab()

    def setup_config_tab(self):
        # Port selection
        ttk.Label(self.config_tab, text="Porta:").grid(column=0, row=0, padx=10, pady=10)
        self.port_entry = ttk.Entry(self.config_tab)
        self.port_entry.grid(column=1, row=0, padx=10, pady=10)

        # Baudrate selection
        ttk.Label(self.config_tab, text="Baudrate:").grid(column=0, row=1, padx=10, pady=10)
        self.baudrate_entry = ttk.Entry(self.config_tab)
        self.baudrate_entry.grid(column=1, row=1, padx=10, pady=10)

        # Connect button
        self.connect_button = ttk.Button(self.config_tab, text="Conectar", command=self.connect_serial)
        self.connect_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    def setup_data_tab(self):
        # Text area for data
        self.data_text = tk.Text(self.data_tab, wrap="word")
        self.data_text.pack(expand=1, fill="both", padx=10, pady=10)

        # Save button
        self.save_button = ttk.Button(self.data_tab, text="Salvar", command=self.save_data)
        self.save_button.pack(pady=10)

    def setup_graph_tab(self):
        # Graph configuration
        ttk.Label(self.graph_tab, text="Coluna X:").grid(column=0, row=0, padx=10, pady=10)
        self.x_column_entry = ttk.Entry(self.graph_tab)
        self.x_column_entry.grid(column=1, row=0, padx=10, pady=10)

        ttk.Label(self.graph_tab, text="Coluna Y:").grid(column=0, row=1, padx=10, pady=10)
        self.y_column_entry = ttk.Entry(self.graph_tab)
        self.y_column_entry.grid(column=1, row=1, padx=10, pady=10)

        self.plot_button = ttk.Button(self.graph_tab, text="Gerar Gráfico", command=self.plot_graph)
        self.plot_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_tab)
        self.canvas.get_tk_widget().grid(column=0, row=3, columnspan=2, padx=10, pady=10)

    def connect_serial(self):
        port = self.port_entry.get()
        baudrate = self.baudrate_entry.get()

        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            threading.Thread(target=self.read_serial_data, daemon=True).start()
        except Exception as e:
            self.data_text.insert("end", f"Erro ao conectar: {e}\n")

    def read_serial_data(self):
        while self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode("utf-8").strip()
                if line:
                    self.data.append(line)
                    self.data_text.insert("end", line + "\n")
            except Exception as e:
                self.data_text.insert("end", f"Erro ao ler dados: {e}\n")

    def save_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("\n".join(self.data))

    def plot_graph(self):
        try:
            x_col = int(self.x_column_entry.get()) - 1
            y_col = int(self.y_column_entry.get()) - 1

            x_data = []
            y_data = []

            for line in self.data:
                columns = line.split()
                x_data.append(float(columns[x_col]))
                y_data.append(float(columns[y_col]))

            self.ax.clear()
            self.ax.plot(x_data, y_data)
            self.ax.set_title("Gráfico")
            self.ax.set_xlabel(f"Coluna {x_col + 1}")
            self.ax.set_ylabel(f"Coluna {y_col + 1}")
            self.canvas.draw()
        except Exception as e:
            self.data_text.insert("end", f"Erro ao gerar gráfico: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialGUI(root)
    root.mainloop()
