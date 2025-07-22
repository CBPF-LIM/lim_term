import tkinter as tk
from tkinter import ttk, filedialog
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import glob
import platform

class GraphOptionsMenu:
    def __init__(self, parent, serial_gui):
        self.window = tk.Toplevel(parent)
        self.window.title("Opções de Gráfico")
        self.serial_gui = serial_gui

        # Tipo de gráfico
        ttk.Label(self.window, text="Tipo de Gráfico:").grid(column=0, row=0, padx=10, pady=10)
        self.graph_type_combobox = ttk.Combobox(self.window, state="readonly", values=["Linha", "Barras", "Dispersão"])
        self.graph_type_combobox.grid(column=1, row=0, padx=10, pady=10)
        self.graph_type_combobox.set(self.serial_gui.graph_settings.get("type", "Linha"))  # Load saved value

        # Cor
        ttk.Label(self.window, text="Cor:").grid(column=0, row=1, padx=10, pady=10)
        self.color_combobox = ttk.Combobox(self.window, state="readonly", values=[
            "Blue", "Cyan", "Teal", "Green", "Lime", "Yellow", "Amber", "Orange", "Red", "Magenta",
            "Indigo", "Violet", "Turquoise", "Aquamarine", "SpringGreen", "Chartreuse", "Gold", "Coral", "Crimson", "Pink"
        ])
        self.color_combobox.grid(column=1, row=1, padx=10, pady=10)
        self.color_combobox.set(self.serial_gui.graph_settings.get("color", "Blue"))  # Load saved value

        # Min e Max dos eixos
        ttk.Label(self.window, text="Min X:").grid(column=0, row=2, padx=10, pady=10)
        self.min_x_entry = ttk.Entry(self.window)
        self.min_x_entry.grid(column=1, row=2, padx=10, pady=10)
        self.min_x_entry.insert(0, self.serial_gui.graph_settings.get("min_x", ""))  # Load saved value

        ttk.Label(self.window, text="Max X:").grid(column=0, row=3, padx=10, pady=10)
        self.max_x_entry = ttk.Entry(self.window)
        self.max_x_entry.grid(column=1, row=3, padx=10, pady=10)
        self.max_x_entry.insert(0, self.serial_gui.graph_settings.get("max_x", ""))  # Load saved value

        ttk.Label(self.window, text="Min Y:").grid(column=0, row=4, padx=10, pady=10)
        self.min_y_entry = ttk.Entry(self.window)
        self.min_y_entry.grid(column=1, row=4, padx=10, pady=10)
        self.min_y_entry.insert(0, self.serial_gui.graph_settings.get("min_y", ""))  # Load saved value

        ttk.Label(self.window, text="Max Y:").grid(column=0, row=5, padx=10, pady=10)
        self.max_y_entry = ttk.Entry(self.window)
        self.max_y_entry.grid(column=1, row=5, padx=10, pady=10)
        self.max_y_entry.insert(0, self.serial_gui.graph_settings.get("max_y", ""))  # Load saved value

        # Formato dos pontos (apenas para dispersão)
        ttk.Label(self.window, text="Formato dos Pontos:").grid(column=0, row=6, padx=10, pady=10)
        self.marker_entry = ttk.Entry(self.window)
        self.marker_entry.grid(column=1, row=6, padx=10, pady=10)
        self.marker_entry.insert(0, self.serial_gui.graph_settings.get("marker", ""))  # Load saved value

        # Tipo de ponto
        ttk.Label(self.window, text="Tipo de Ponto:").grid(column=0, row=7, padx=10, pady=10)
        self.dot_type_combobox = ttk.Combobox(self.window, state="readonly", values=[
            "Círculo (o)", "Quadrado (s)", "Triângulo (^)" , "Diamante (D)", "Estrela (*)", "Mais (+)", "X (x)", "Barra Vertical (|)", "Barra Horizontal (_)", "Hexágono (h)"
        ])
        self.dot_type_combobox.grid(column=1, row=7, padx=10, pady=10)
        self.dot_type_combobox.set({
            "o": "Círculo (o)",
            "s": "Quadrado (s)",
            "^": "Triângulo (^)",
            "D": "Diamante (D)",
            "*": "Estrela (*)",
            "+": "Mais (+)",
            "x": "X (x)",
            "|": "Barra Vertical (|)",
            "_": "Barra Horizontal (_)",
            "h": "Hexágono (h)"
        }.get(self.serial_gui.graph_settings.get("dot_type", "o"), "Círculo (o)"))  # Load saved value

        # Botão para aplicar configurações
        self.apply_button = ttk.Button(self.window, text="Aplicar", command=self.apply_settings)
        self.apply_button.grid(column=0, row=8, columnspan=2, padx=10, pady=10)

    def apply_settings(self):
        try:
            self.serial_gui.graph_settings = {
                key: value for key, value in {
                    "type": self.graph_type_combobox.get(),
                    "color": self.color_combobox.get(),  # Atualizado para usar o menu suspenso
                    "min_x": self.min_x_entry.get(),
                    "max_x": self.max_x_entry.get(),
                    "min_y": self.min_y_entry.get(),
                    "max_y": self.max_y_entry.get(),
                    "marker": self.marker_entry.get(),
                    "dot_type": {
                        "Círculo (o)": "o",
                        "Quadrado (s)": "s",
                        "Triângulo (^)": "^",
                        "Diamante (D)": "D",
                        "Estrela (*)": "*",
                        "Mais (+)": "+",
                        "X (x)": "x",
                        "Barra Vertical (|)": "|",
                        "Barra Horizontal (_)": "_",
                        "Hexágono (h)": "h"
                    }.get(self.dot_type_combobox.get(), "o")  # Map descriptive label to internal value
                }.items() if value
            }
            print("Configurações aplicadas:", self.serial_gui.graph_settings)
            self.window.destroy()
        except Exception as e:
            print(f"Erro ao aplicar configurações: {e}")

class SerialGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Port GUI")

        self.serial_port = None
        self.data = []
        self.graph_settings = {}

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
        self.port_combobox = ttk.Combobox(self.config_tab, state="readonly")
        self.port_combobox.grid(column=1, row=0, padx=10, pady=10)
        self.update_ports()

        # Baudrate selection
        ttk.Label(self.config_tab, text="Baudrate:").grid(column=0, row=1, padx=10, pady=10)
        self.baudrate_combobox = ttk.Combobox(self.config_tab, state="readonly", values=["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combobox.grid(column=1, row=1, padx=10, pady=10)
        self.baudrate_combobox.set("9600")

        # Connect button
        self.connect_button = ttk.Button(self.config_tab, text="Conectar", command=self.connect_serial)
        self.connect_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    def update_ports(self):
        if platform.system() == "Linux":
            # Include pseudo-terminals in Linux
            pts_ports = glob.glob("/dev/pts/*")
            ports = [port.device for port in serial.tools.list_ports.comports()] + pts_ports
        else:
            ports = [port.device for port in serial.tools.list_ports.comports()]

        self.port_combobox["values"] = ports
        if ports:
            self.port_combobox.set(ports[0])

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
        self.x_column_entry.insert(0, "2")  # Valor padrão para coluna X

        ttk.Label(self.graph_tab, text="Coluna Y:").grid(column=0, row=1, padx=10, pady=10)
        self.y_column_entry = ttk.Entry(self.graph_tab)
        self.y_column_entry.grid(column=1, row=1, padx=10, pady=10)
        self.y_column_entry.insert(0, "3")  # Valor padrão para coluna Y

        self.plot_button = ttk.Button(self.graph_tab, text="Gerar Gráfico", command=self.plot_graph)
        self.plot_button.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_tab)
        self.canvas.get_tk_widget().grid(column=0, row=3, columnspan=2, padx=10, pady=10)

        # Botão para abrir o menu de opções de gráfico
        self.options_button = ttk.Button(self.graph_tab, text="Opções de Gráfico", command=self.open_graph_options)
        self.options_button.grid(column=0, row=4, columnspan=2, padx=10, pady=10)

    def open_graph_options(self):
        GraphOptionsMenu(self.root, self)

    def connect_serial(self):
        port = self.port_combobox.get()
        baudrate = self.baudrate_combobox.get()

        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            threading.Thread(target=self.read_serial_data, daemon=True).start()
        except Exception as e:
            error_message = f"Erro ao conectar: {e}\n"
            self.data_text.insert("end", error_message)
            print(error_message)

    def read_serial_data(self):
        while self.serial_port and self.serial_port.is_open:
            try:
                line = self.serial_port.readline().decode("utf-8").strip()
                if line:
                    self.data.append(line)
                    self.data_text.insert("end", line + "\n")
                    self.plot_graph()  # Atualiza o gráfico automaticamente ao receber novos dados
            except serial.SerialException as e:
                error_message = f"Erro ao ler dados: {e}\n"
                self.data_text.insert("end", error_message)
                print(error_message)
                break
            except Exception as e:
                error_message = f"Erro inesperado: {e}\n"
                self.data_text.insert("end", error_message)
                print(error_message)
                break

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

            graph_type = self.graph_settings.get("type", "Linha")
            color = self.graph_settings.get("color", "blue")
            min_x = float(self.graph_settings.get("min_x", "0")) if self.graph_settings.get("min_x") else None
            max_x = float(self.graph_settings.get("max_x", "0")) if self.graph_settings.get("max_x") else None
            min_y = float(self.graph_settings.get("min_y", "0")) if self.graph_settings.get("min_y") else None
            max_y = float(self.graph_settings.get("max_y", "0")) if self.graph_settings.get("max_y") else None
            marker = self.graph_settings.get("marker", "o")
            dot_type = self.graph_settings.get("dot_type", "o")

            if graph_type == "Linha":
                self.ax.plot(x_data, y_data, color=color, marker=dot_type)  # Added marker for line graph
            elif graph_type == "Barras":
                self.ax.bar(x_data, y_data, color=color)
            elif graph_type == "Dispersão":
                self.ax.scatter(x_data, y_data, color=color, marker=dot_type)

            self.ax.set_xlim(min_x, max_x)
            self.ax.set_ylim(min_y, max_y)
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
