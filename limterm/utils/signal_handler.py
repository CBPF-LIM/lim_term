"""
Simple signal handler for graceful shutdown confirmation
"""

import signal
import sys
from tkinter import messagebox


class SignalHandler:
    """Handle system signals with simple exit confirmation"""

    def __init__(self, app_instance=None):
        self.app_instance = app_instance
        self.shutdown_requested = False
        self.is_busy = False

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        """Handle received signal"""
        if self.shutdown_requested:

            sys.exit(1)

        self.shutdown_requested = True

        if self.app_instance and hasattr(self.app_instance, "root"):
            try:
                self.app_instance.root.after_idle(self._show_exit_confirmation)
            except:
                sys.exit(0)
        else:
            sys.exit(0)

    def _show_exit_confirmation(self):
        """Show exit confirmation dialog only if app is busy"""
        try:

            if not self.is_busy:
                if self.app_instance and hasattr(self.app_instance, "root"):
                    self.app_instance.root.quit()
                sys.exit(0)
                return

            result = messagebox.askokcancel(
                "Exit Confirmation", "Are you sure you want to exit?", icon="warning"
            )

            if result:

                if self.app_instance and hasattr(self.app_instance, "root"):
                    self.app_instance.root.quit()
                sys.exit(0)
            else:

                self.shutdown_requested = False

        except Exception as e:
            print(f"Error showing exit confirmation: {e}")
            sys.exit(0)

    def set_busy(self, busy=True):
        """Set the busy state to control exit confirmation"""
        self.is_busy = busy

    def request_exit(self):
        """Programmatically request exit"""
        if not self.shutdown_requested:
            self.shutdown_requested = True
            self._show_exit_confirmation()
