import os
import threading
import time
import math
import platform


class MockSerial:


    def __init__(self):
        self.master_fd = None
        self.slave_port = None
        self.is_running = False
        self.data_thread = None

    def create_virtual_port(self):

        try:
            if platform.system() == "Linux":
                import pty
                self.master_fd, slave_fd = pty.openpty()
                self.slave_port = os.ttyname(slave_fd)


                os.chmod(self.slave_port, 0o666)

                return self.slave_port
            else:


                self.slave_port = "COM_VIRTUAL"
                return self.slave_port

        except Exception as e:
            raise Exception(f"Erro ao criar porta virtual: {e}")

    def start_data_generation(self):

        if not self.master_fd or self.is_running:
            return

        self.is_running = True
        self.data_thread = threading.Thread(target=self._generate_data, daemon=True)
        self.data_thread.start()

    def stop_data_generation(self):

        self.is_running = False
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except:
                pass
        self.master_fd = None
        self.slave_port = None

    def _generate_data(self):

        index = 0
        while self.is_running and self.master_fd:
            try:

                col1 = int(index)
                col2 = col1 * 0.01 + 2
                col3 = math.sin(10 * col2) + 2
                col4 = math.sin(20 * col2) + 0.1 + 2
                col5 = math.sin(30 * col2) + 0.2 + 2
                col6 = math.sin(40 * col2) + 0.3 + 2
                col7 = math.sin(50 * col2) + 0.4 + 2

                data = f"{col1:d} {col2:.2f} {col3:.2f} {col4:.2f} {col5:.2f} {col6:.2f} {col7:.2f}"
                os.write(self.master_fd, (data + "\n").encode("utf-8"))

                index += 1
                time.sleep(0.5)

            except Exception as e:
                print(f"Erro na geração de dados: {e}")
                break

    def get_port(self):

        return self.slave_port
