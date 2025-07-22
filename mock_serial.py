import serial
import threading
import time
import platform
import os
import pty
import math

def mock_serial(port=None, baudrate=9600):
    try:
        # Detect OS and set default port
        if port is None:
            if platform.system() == "Windows":
                port = "COM1"
            elif platform.system() == "Linux":
                master, slave = pty.openpty()
                port = os.ttyname(slave)

        print(f"Mock serial port opened on {port} with baudrate {baudrate}")

        def generate_data(master_fd):
            index = 0
            while True:
                # Generate artificial data
                col1 = index
                col2 = col1
                col3 = math.sin(col2 / 10.0) * 100  # Simulated sensor data
                data = f"{col1} {col2} {col3}"
                os.write(master_fd, (data + "\n").encode("utf-8"))
                index += 1
                time.sleep(1)

        threading.Thread(target=generate_data, args=(master,), daemon=True).start()

        # Ensure pseudo-terminal permissions
        os.chmod(port, 0o666)

        # Keep the script running
        print(f"Connect to the mock serial port using: screen {port} {baudrate}")
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Error creating mock serial port: {e}")

if __name__ == "__main__":
    # Detect OS and set default port automatically
    if platform.system() == "Windows":
        mock_serial(port="COM1", baudrate=9600)
    elif platform.system() == "Linux":
        mock_serial(port=None, baudrate=9600)
