#!/usr/bin/env python3
"""
Lim Terminal - Serial Communication & Data Visualization
Entry point for the application
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from limterm.gui import MainWindow
from limterm.i18n import t, initialize as init_i18n


def main():
    """Main entry point for Lim Terminal application"""
    init_i18n()

    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{t('errors.application_interrupted')}")
    except Exception as e:
        print(t("errors.application_error", error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
