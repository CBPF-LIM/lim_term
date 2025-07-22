# Serial Port GUI

## Overview
This project provides a graphical user interface (GUI) for interacting with serial ports. It allows users to configure serial port settings, receive data, and visualize the data in various graph formats.

## Features
- **Serial Port Configuration**: Select port and baud rate.
- **Data Display**: View incoming serial data in real-time.
- **Graph Visualization**:
  - Line Graph
  - Bar Graph
  - Scatter Plot
  - Customizable options for colors, axis limits, and marker styles.
- **Automatic Graph Updates**: Graphs are updated automatically as new data is received.
- **Data Saving**: Save received data to a text file.

## Requirements
- Python 3.6+
- Required libraries:
  - `tkinter`
  - `serial`
  - `matplotlib`

## Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:CBPF-LIM/lim_term.git
   ```
2. Navigate to the project directory:
   ```bash
   cd lim_term
   ```
3. Install the required Python libraries:
   ```bash
   pip install pyserial matplotlib
   ```

## Usage
1. Run the GUI application:
   ```bash
   python tkinter_serial_gui.py
   ```
2. Select the serial port and baud rate in the "Configuração" tab.
3. View incoming data in the "Dados" tab.
4. Configure and generate graphs in the "Gráfico" tab.
5. Save data using the "Salvar" button in the "Dados" tab.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.

## Contact
For questions or support, please contact [CBPF-LIM](https://github.com/CBPF-LIM).
