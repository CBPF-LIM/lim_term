"""
Utilitários para comunicação serial
"""
import serial
import serial.tools.list_ports
import glob
import platform


class SerialPortManager:
    """Gerenciador de portas seriais"""
    
    @staticmethod
    def get_available_ports():
        """Retorna lista de portas seriais disponíveis"""
        if platform.system() == "Linux":
            # Inclui pseudo-terminais no Linux
            pts_ports = glob.glob("/dev/pts/*")
            ports = [port.device for port in serial.tools.list_ports.comports()] + pts_ports
        else:
            ports = [port.device for port in serial.tools.list_ports.comports()]
        return ports
    
    @staticmethod
    def create_connection(port, baudrate, timeout=1):
        """Cria conexão serial"""
        try:
            return serial.Serial(port, baudrate, timeout=timeout)
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar na porta {port}: {e}")


class DataParser:
    """Parser para dados recebidos via serial"""
    
    @staticmethod
    def parse_line(line):
        """Converte linha de dados em colunas"""
        return line.strip().split()
    
    @staticmethod
    def extract_columns(data_lines, x_col, y_col):
        """Extrai dados das colunas especificadas"""
        x_data = []
        y_data = []
        
        for line in data_lines:
            try:
                columns = DataParser.parse_line(line)
                if len(columns) > max(x_col, y_col):
                    x_data.append(float(columns[x_col]))
                    y_data.append(float(columns[y_col]))
            except (ValueError, IndexError):
                continue  # Ignora linhas inválidas
                
        return x_data, y_data
