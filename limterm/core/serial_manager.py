import threading
from ..utils import SerialPortManager
from ..config import SERIAL_TIMEOUT
from ..i18n import t


class SerialManager:
    def __init__(self, data_callback=None, error_callback=None):
        self.serial_port = None
        self.data_callback = data_callback
        self.error_callback = error_callback
        self.is_connected = False
        self._stop_reading = False

    def connect(self, port, baudrate):
        try:
            self.serial_port = SerialPortManager.create_connection(
                port, baudrate, SERIAL_TIMEOUT
            )
            self.is_connected = True
            self._stop_reading = False

            threading.Thread(target=self._read_data, daemon=True).start()
            return True

        except Exception as e:
            if self.error_callback:
                self.error_callback(t("errors.connection_error", error=str(e)))
            return False

    def disconnect(self):
        self._stop_reading = True
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False

    def _read_data(self):
        while self.serial_port and self.serial_port.is_open and not self._stop_reading:
            try:
                line = self.serial_port.readline().decode("utf-8").strip()
                if line and self.data_callback:
                    self.data_callback(line)

            except Exception as e:
                if self.error_callback:
                    self.error_callback(t("errors.data_read_error", error=str(e)))
                break

    def get_available_ports(self):
        return SerialPortManager.get_available_ports()
