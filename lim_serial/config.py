"""
Configurações principais da aplicação
"""

# Configurações da interface
WINDOW_TITLE = "LIM Serial - GUI"
DEFAULT_GEOMETRY = "800x600"

# Configurações de comunicação serial
DEFAULT_BAUDRATES = ["9600", "19200", "38400", "57600", "115200"]
DEFAULT_BAUDRATE = "9600"
SERIAL_TIMEOUT = 1

# Configurações de gráfico
FIGURE_SIZE = (5, 4)
FIGURE_DPI = 100

# Cores disponíveis para gráficos
AVAILABLE_COLORS = [
    "Blue", "Cyan", "Teal", "Green", "Lime", "Yellow", "Amber", "Orange", 
    "Red", "Magenta", "Indigo", "Violet", "Turquoise", "Aquamarine", 
    "SpringGreen", "Chartreuse", "Gold", "Coral", "Crimson", "Pink"
]

# Tipos de marcadores disponíveis
MARKER_TYPES = {
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
}

# Tipos de gráfico
GRAPH_TYPES = ["Linha", "Barras", "Dispersão"]

# Configurações padrão de colunas
DEFAULT_X_COLUMN = "2"
DEFAULT_Y_COLUMN = "3"
