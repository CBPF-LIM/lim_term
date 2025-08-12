import signal
import sys
from .ui_builder import build_from_layout_name


class SignalHandler:

    def __init__(self, app_instance=None):
        self.app_instance = app_instance
        self.shutdown_requested = False
        self.is_busy = False
        self._exit_result = False
        self._exit_dialog = None

    def setup_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        if self.shutdown_requested:

            sys.exit(1)

        self.shutdown_requested = True

        if self.app_instance and hasattr(self.app_instance, "root"):
            try:
                self.app_instance.root.after_idle(self._show_exit_confirmation)
            except Exception:
                sys.exit(0)
        else:
            sys.exit(0)

    def _on_exit_ok(self):
        self._exit_result = True
        try:
            if self._exit_dialog and hasattr(self._exit_dialog, "destroy"):
                self._exit_dialog.destroy()
        except Exception:
            pass

    def _on_exit_cancel(self):
        self._exit_result = False
        try:
            if self._exit_dialog and hasattr(self._exit_dialog, "destroy"):
                self._exit_dialog.destroy()
        except Exception:
            pass

    def _show_exit_confirmation_dialog(self) -> bool:
        if not (self.app_instance and hasattr(self.app_instance, "root")):
            return True
        parent = self.app_instance.root
        self._exit_result = False

        try:
            build_from_layout_name(parent, "exit_confirmation_dialog", self)

            if hasattr(self._exit_dialog, "transient"):
                try:
                    self._exit_dialog.transient(parent)
                except Exception:
                    pass
            if hasattr(self._exit_dialog, "grab_set"):
                try:
                    self._exit_dialog.grab_set()
                except Exception:
                    pass
            if hasattr(self._exit_dialog, "focus_set"):
                try:
                    self._exit_dialog.focus_set()
                except Exception:
                    pass
            try:
                parent.wait_window(self._exit_dialog)
            except Exception:
                pass
        except Exception:

            return True
        return bool(self._exit_result)

    def _show_exit_confirmation(self):
        try:

            if not self.is_busy:
                if self.app_instance and hasattr(self.app_instance, "root"):
                    self.app_instance.root.quit()
                sys.exit(0)
                return

            confirm = self._show_exit_confirmation_dialog()

            if confirm:

                if self.app_instance and hasattr(self.app_instance, "root"):
                    self.app_instance.root.quit()
                sys.exit(0)
            else:

                self.shutdown_requested = False

        except Exception as e:
            print(f"Error showing exit confirmation: {e}")
            sys.exit(0)

    def set_busy(self, busy=True):
        self.is_busy = busy

    def request_exit(self):
        if not self.shutdown_requested:
            self.shutdown_requested = True
            self._show_exit_confirmation()
