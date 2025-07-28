# Technical configuration values only

# Window configuration
DEFAULT_GEOMETRY = "800x600"

# Serial configuration
DEFAULT_BAUDRATES = [
    "300",
    "1200",
    "2400",
    "4800",
    "9600",
    "19200",
    "38400",
    "57600",
    "74880",
    "115200",
    "230400",
    "250000",
    "500000",
    "1000000",
    "2000000",
]
DEFAULT_BAUDRATE = "9600"
SERIAL_TIMEOUT = 1

# Graph configuration
FIGURE_SIZE = (5, 4)
FIGURE_DPI = 100
DEFAULT_X_COLUMN = "2"
DEFAULT_Y_COLUMN = "3"

# Chart refresh rate configuration
DEFAULT_REFRESH_RATE = 10

# Color names for internal use (translation keys)
COLOR_KEYS = [
    "blue",
    "cyan",
    "teal",
    "green",
    "lime",
    "yellow",
    "amber",
    "orange",
    "red",
    "magenta",
    "indigo",
    "violet",
    "turquoise",
    "aquamarine",
    "springgreen",
    "chartreuse",
    "gold",
    "coral",
    "crimson",
    "pink",
]

# Marker type mappings for internal use
MARKER_MAPPING = {
    "circle": "o",
    "square": "s",
    "triangle": "^",
    "diamond": "D",
    "star": "*",
    "plus": "+",
    "x": "x",
    "vline": "|",
    "hline": "_",
    "hexagon": "h",
}
