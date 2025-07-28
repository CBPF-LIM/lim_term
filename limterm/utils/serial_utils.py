import serial
import serial.tools.list_ports
import glob
import platform


class SerialPortManager:
    @staticmethod
    def get_available_ports():
        if platform.system() == "Linux":
            pts_ports = glob.glob("/dev/pts/*")
            ports = [
                port.device for port in serial.tools.list_ports.comports()
            ] + pts_ports
        else:
            ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports

    @staticmethod
    def create_connection(port, baudrate, timeout=1):
        try:
            return serial.Serial(port, baudrate, timeout=timeout)
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar na porta {port}: {e}")


class DataParser:
    @staticmethod
    def parse_line(line):
        return line.strip().split()

    @staticmethod
    def extract_columns(data_lines, x_col, y_col):
        x_data = []
        y_data = []

        for line in data_lines:
            try:
                columns = DataParser.parse_line(line)
                if len(columns) > max(x_col, y_col):
                    x_data.append(float(columns[x_col]))
                    y_data.append(float(columns[y_col]))
            except (ValueError, IndexError):
                continue

        return x_data, y_data
