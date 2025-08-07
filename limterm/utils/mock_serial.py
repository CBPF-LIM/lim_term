import threading
import time
import math
from asteval import Interpreter
import logging

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    def __init__(self, data_callback=None, equations=None, refresh_rate=15):
        self.data_callback = data_callback
        self.equations = equations or {}
        self.is_running = False
        self.data_thread = None
        self.refresh_rate = refresh_rate
        self.index = 1

    def set_equations(self, equations):
        self.equations = equations

    def set_data_callback(self, callback):
        self.data_callback = callback

    def start_data_generation(self):
        if self.is_running:
            return

        self.is_running = True
        self.data_thread = threading.Thread(target=self._generate_data, daemon=True)
        self.data_thread.start()

    def stop_data_generation(self):
        self.is_running = False
        if self.data_thread:
            self.data_thread.join(timeout=1.0)

    def _generate_data(self):
        while self.is_running:
            try:
                data_values = []
                n = int(self.index)

                data_values.append(str(n))

                if self.equations:
                    aeval = Interpreter()
                    aeval.symtable['n'] = n
                    for column_name in sorted(self.equations.keys()):
                        expr = self.equations[column_name]
                        if not expr.strip():
                            value = 0
                            aeval.symtable[column_name] = value
                            continue
                        try:
                            value = aeval(expr)
                            if value is None:
                                value = 0
                        except Exception as e:
                            logger.error(f"Error evaluating equation '{expr}': {e}")
                            value = 0
                        aeval.symtable[column_name] = value
                        data_values.append(str(value))

                data_line = " ".join(data_values)

                if self.data_callback:
                    self.data_callback(data_line)

                self.index += 1
                time.sleep(1 / self.refresh_rate)

            except Exception as e:
                print(t("mode_synthetic_generation_error").format(error=e))
                break


class MockSerial(SyntheticDataGenerator):
    def __init__(self):
        super().__init__()
        self.master_fd = None
        self.slave_port = None

    def create_virtual_port(self):
        self.slave_port = "SYNTHETIC_MODE"
        return self.slave_port

    def get_port(self):
        return self.slave_port
