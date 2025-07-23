#!/usr/bin/env python3
"""
Ponto de entrada principal da aplicação LIM Serial
"""

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lim_serial.gui import MainWindow


def main():
    """Função principal"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário")
    except Exception as e:
        print(f"Erro na aplicação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
