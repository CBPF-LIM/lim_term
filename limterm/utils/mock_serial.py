import threading
import time
import math


class SyntheticDataGenerator:
    def __init__(self, data_callback=None, equations=None):
        self.data_callback = data_callback
        self.equations = equations or {}
        self.is_running = False
        self.data_thread = None
        self.index = 0

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
                n = self.index

                if self.equations:
                    evaluated_vars = {"n": n, "math": math}

                    for column_name in sorted(self.equations.keys()):
                        equation = self.equations[column_name]
                        try:
                            value = eval(equation, {"__builtins__": {}}, evaluated_vars)
                            evaluated_vars[column_name] = (value)
                            data_values.append(f"{value:.2f}")
                        except Exception as e:
                            print(f"Error evaluating equation '{equation}': {e}")
                            data_values.append("0.00")

                data_line = " ".join(data_values)

                if self.data_callback:
                    self.data_callback(data_line)

                self.index += 1
                time.sleep(1 / 30)

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
