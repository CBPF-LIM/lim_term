#!/usr/bin/env python3
"""
Lim Terminal - Serial Communication & Data Visualization
Entry point for the application
"""
import sys
import os

# Add the current directory to Python path for development
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from limterm.gui import MainWindow


def main():
    """Main entry point for Lim Terminal application"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
