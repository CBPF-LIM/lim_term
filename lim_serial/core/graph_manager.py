"""
Gerenciador de gráficos usando matplotlib
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ..config import FIGURE_SIZE, FIGURE_DPI


class GraphManager:
    """Gerenciador de gráficos"""
    
    def __init__(self, parent_widget):
        self.figure = plt.Figure(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, parent_widget)
        
    def get_widget(self):
        """Retorna o widget do canvas"""
        return self.canvas.get_tk_widget()
    
    def clear(self):
        """Limpa o gráfico"""
        self.ax.clear()
    
    def plot_line(self, x_data, y_data, color="blue", marker="o"):
        """Plota gráfico de linha"""
        self.ax.plot(x_data, y_data, color=color, marker=marker)
    
    def plot_bar(self, x_data, y_data, color="blue"):
        """Plota gráfico de barras"""
        self.ax.bar(x_data, y_data, color=color)
    
    def plot_scatter(self, x_data, y_data, color="blue", marker="o"):
        """Plota gráfico de dispersão"""
        self.ax.scatter(x_data, y_data, color=color, marker=marker)
    
    def set_limits(self, min_x=None, max_x=None, min_y=None, max_y=None):
        """Define limites dos eixos"""
        if min_x is not None or max_x is not None:
            self.ax.set_xlim(min_x, max_x)
        if min_y is not None or max_y is not None:
            self.ax.set_ylim(min_y, max_y)
    
    def set_labels(self, title="Graph", xlabel="X", ylabel="Y"):
        """Define rótulos do gráfico"""
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
    
    def update(self):
        """Atualiza o canvas"""
        self.canvas.draw()
    
    def plot_from_settings(self, x_data, y_data, settings, x_col=0, y_col=1, title=None, xlabel=None, ylabel=None):
        """Plota gráfico baseado nas configurações"""
        self.clear()
        
        graph_type = settings.get("type", "Linha")
        color = settings.get("color", "blue").lower()
        marker = settings.get("dot_type", "o")
        
        # Converte nomes de cores se necessário
        if color in ["blue", "cyan", "teal", "green", "lime", "yellow", "amber", 
                    "orange", "red", "magenta", "indigo", "violet", "turquoise", 
                    "aquamarine", "springgreen", "chartreuse", "gold", "coral", 
                    "crimson", "pink"]:
            color = color.lower()
        
        if graph_type == "Linha":
            self.plot_line(x_data, y_data, color=color, marker=marker)
        elif graph_type == "Barras":
            self.plot_bar(x_data, y_data, color=color)
        elif graph_type == "Dispersão":
            self.plot_scatter(x_data, y_data, color=color, marker=marker)
        
        # Define limites se especificados
        min_x = float(settings.get("min_x", "0")) if settings.get("min_x") else None
        max_x = float(settings.get("max_x", "0")) if settings.get("max_x") else None
        min_y = float(settings.get("min_y", "0")) if settings.get("min_y") else None
        max_y = float(settings.get("max_y", "0")) if settings.get("max_y") else None
        
        self.set_limits(min_x, max_x, min_y, max_y)
        self.set_labels(
            title=title or "Graph",
            xlabel=xlabel or f"Column {x_col + 1}",
            ylabel=ylabel or f"Column {y_col + 1}"
        )
        self.update()
