import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ..utils import FileManager, format_elapsed_since
from ..i18n import t, get_config_manager
from .preference_widgets import PrefCheckbutton, PrefCombobox, PrefEntry
import logging
import os
import datetime
import time
from collections import deque
from ..config import CAPTURE_DIR

logger = logging.getLogger(__name__)


class DataTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.config_manager = get_config_manager()

        self.data_buffer = deque(maxlen=10000)
        self.capture_file = None
        self.capture_filename = None
        self.preview_offset = 0
        self.preview_paused = False
        self.timestamp_start = None

        self._create_widgets()

    def _create_widgets(self):

        toolbar_frame = ttk.Frame(self.frame)
        toolbar_frame.pack(fill="x", padx=10, pady=(5, 0))

        button_container = ttk.Frame(toolbar_frame)
        button_container.pack(side="left", fill="x", expand=True)

        self.save_button = ttk.Button(
            button_container, text=t("ui.data_tab.save"), command=self._save_data
        )
        self.save_button.pack(side="left", padx=(0, 10))

        self.load_button = ttk.Button(
            button_container, text=t("ui.data_tab.load"), command=self._load_data
        )
        self.load_button.pack(side="left", padx=(0, 10))

        self.clear_button = ttk.Button(
            button_container, text=t("ui.data_tab.clear"), command=self._clear_data
        )
        self.clear_button.pack(side="left", padx=(0, 10))

        self.pause_button = ttk.Button(
            button_container,
            text=t("ui.data_tab.pause_preview"),
            command=self._toggle_preview_pause,
        )
        self.pause_button.pack(side="left", padx=(0, 10))

        self.reset_timestamp_button = ttk.Button(
            button_container,
            text=t("ui.data_tab.reset_timestamp"),
            command=self._reset_timestamp,
        )
        self.reset_timestamp_button.pack(side="left", padx=(0, 10))

        self.toggle_settings_button = ttk.Button(
            toolbar_frame,
            text=t("ui.data_tab.show_settings"),
            command=self._toggle_settings,
        )
        self.toggle_settings_button.pack(side="right")

        self.data_settings_frame = ttk.LabelFrame(
            self.frame, text=t("ui.data_tab.data_settings")
        )

        settings_container = ttk.Frame(self.data_settings_frame)
        settings_container.pack(fill="x", padx=5, pady=5)

        capture_frame = ttk.LabelFrame(
            settings_container, text=t("ui.data_tab.capture")
        )
        capture_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.capture_enabled = PrefCheckbutton(
            capture_frame,
            pref_key="data_capture.enabled",
            default_value=False,
            text=t("ui.data_tab.capture_enabled"),
            on_change=self._on_capture_enabled_change,
        )
        self.capture_enabled.grid(
            column=0, row=0, columnspan=2, padx=5, pady=2, sticky="w"
        )

        ttk.Label(capture_frame, text=t("ui.data_tab.filename_mode_label")).grid(
            column=0, row=1, padx=5, pady=2, sticky="w"
        )
        self.filename_mode = PrefCombobox(
            capture_frame,
            pref_key="data_capture.filename_mode",
            default_value="auto",
            state="readonly",
            values=[
                t("ui.data_tab.filename_modes.auto"),
                t("ui.data_tab.filename_modes.fixed"),
            ],
            value_mapping={
                t("ui.data_tab.filename_modes.auto"): "auto",
                t("ui.data_tab.filename_modes.fixed"): "fixed",
            },
            width=12,
            on_change=self._on_filename_mode_change,
        )
        self.filename_mode.grid(column=1, row=1, padx=5, pady=2, sticky="w")

        ttk.Label(capture_frame, text=t("ui.data_tab.fixed_filename_label")).grid(
            column=0, row=2, padx=5, pady=2, sticky="w"
        )
        self.fixed_filename = PrefEntry(
            capture_frame,
            pref_key="data_capture.fixed_filename",
            default_value="data.txt",
            width=15,
            on_change=self._on_capture_setting_change,
        )
        self.fixed_filename.grid(column=1, row=2, padx=5, pady=2, sticky="w")

        ttk.Label(capture_frame, text=t("ui.data_tab.file_mode_label")).grid(
            column=0, row=3, padx=5, pady=2, sticky="w"
        )
        self.file_mode = PrefCombobox(
            capture_frame,
            pref_key="data_capture.file_mode",
            default_value="append",
            state="readonly",
            values=[
                t("ui.data_tab.file_modes.append"),
                t("ui.data_tab.file_modes.overwrite"),
            ],
            value_mapping={
                t("ui.data_tab.file_modes.append"): "append",
                t("ui.data_tab.file_modes.overwrite"): "overwrite",
            },
            width=12,
            on_change=self._on_capture_setting_change,
        )
        self.file_mode.grid(column=1, row=3, padx=5, pady=2, sticky="w")

        preview_frame = ttk.LabelFrame(
            settings_container, text=t("ui.data_tab.preview")
        )
        preview_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.preview_enabled = PrefCheckbutton(
            preview_frame,
            pref_key="data_preview.enabled",
            default_value=False,
            text=t("ui.data_tab.enable_preview"),
            on_change=self._on_preview_enabled_change,
        )
        self.preview_enabled.grid(
            column=0, row=0, columnspan=2, padx=5, pady=2, sticky="w"
        )

        ttk.Label(preview_frame, text=t("ui.data_tab.preview_limit_label")).grid(
            column=0, row=1, padx=5, pady=2, sticky="w"
        )
        self.preview_limit = PrefCombobox(
            preview_frame,
            pref_key="data_preview.limit",
            default_value="50",
            state="readonly",
            values=["10", "25", "50", "100", "200", "500"],
            width=12,
            on_change=self._on_preview_limit_change,
        )
        self.preview_limit.grid(column=1, row=1, padx=5, pady=2, sticky="w")

        self.timestamp_enabled = PrefCheckbutton(
            preview_frame,
            pref_key="data_preview.timestamp_enabled",
            default_value=False,
            text=t("ui.data_tab.enable_timestamp"),
            on_change=self._on_timestamp_enabled_change,
        )
        self.timestamp_enabled.grid(
            column=0, row=2, columnspan=2, padx=5, pady=2, sticky="w"
        )

        self.text_frame = ttk.Frame(self.frame)
        self.text_frame.pack(expand=1, fill="both", padx=10, pady=5)

        self.text_widget = tk.Text(self.text_frame, wrap="word", height=15)
        self.scrollbar = tk.Scrollbar(
            self.text_frame, orient="vertical", command=self.text_widget.yview
        )
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        self._update_widget_states()
        self._setup_initial_capture_state()
        self._update_preview_visibility()

    def _update_widget_states(self):
        filename_mode = self.filename_mode.get_value()
        if filename_mode == "fixed":
            self.fixed_filename.config(state="normal")
            self.file_mode.config(state="readonly")
        else:
            self.fixed_filename.config(state="disabled")
            self.file_mode.config(state="disabled")

        preview_enabled = self.preview_enabled.get_value()
        if preview_enabled:
            self.preview_limit.config(state="readonly")
            self.timestamp_enabled.config(state="normal")
            self.pause_button.config(state="normal")
            self.reset_timestamp_button.config(state="normal")
        else:
            self.preview_limit.config(state="disabled")
            self.timestamp_enabled.config(state="disabled")
            self.pause_button.config(state="disabled")
            self.reset_timestamp_button.config(state="disabled")

        if self.preview_paused:
            self.pause_button.config(text=t("ui.data_tab.resume_preview"))
        else:
            self.pause_button.config(text=t("ui.data_tab.pause_preview"))

    def _update_preview_visibility(self):
        if self.preview_enabled.get_value():
            self.text_widget.pack(side="left", expand=1, fill="both")
            self.scrollbar.pack(side="right", fill="y")
        else:
            self.text_widget.pack_forget()
            self.scrollbar.pack_forget()

    def _setup_initial_capture_state(self):
        if self.capture_enabled.get_value():
            self._setup_capture_file()

    def _toggle_settings(self):
        if self.data_settings_frame.winfo_viewable():
            self.data_settings_frame.pack_forget()
            self.toggle_settings_button.config(text=t("ui.data_tab.show_settings"))
        else:
            self.data_settings_frame.pack(
                fill="x", padx=10, pady=5, before=self.text_frame
            )
            self.toggle_settings_button.config(text=t("ui.data_tab.hide_settings"))

    def _on_capture_enabled_change(self):
        if self.capture_enabled.get_value():
            self._setup_capture_file()
        else:
            self._close_capture_file()
        self._update_widget_states()

    def _on_filename_mode_change(self):
        self._update_widget_states()
        if self.capture_enabled.get_value():
            self._close_capture_file()
            self._setup_capture_file()

    def _on_capture_setting_change(self):
        if self.capture_enabled.get_value():
            self._close_capture_file()
            self._setup_capture_file()

    def _on_preview_enabled_change(self):
        self._update_widget_states()
        self._update_preview_visibility()
        if self.preview_enabled.get_value():
            self._refresh_preview()

    def _on_preview_limit_change(self):
        if self.preview_enabled.get_value():
            self._refresh_preview()

    def _setup_capture_file(self):
        try:
            capture_dir = CAPTURE_DIR
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)

            filename_mode = self.filename_mode.get_value()

            if filename_mode == "auto":
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.capture_filename = os.path.join(
                    capture_dir, f"data_capture_{timestamp}.txt"
                )
            else:
                filename = self.fixed_filename.get_value()
                self.capture_filename = os.path.join(capture_dir, filename)

            file_mode = self.file_mode.get_value()
            mode = "a" if file_mode == "append" else "w"

            self.capture_file = open(self.capture_filename, mode, encoding="utf-8")

            self._add_message(
                t("ui.data_tab.capture_enabled_msg").format(
                    filename=os.path.basename(self.capture_filename)
                )
            )
            logger.info(f"Data capture enabled: {self.capture_filename} (mode: {mode})")

        except Exception as e:
            self.capture_enabled.set_value(False)
            self.capture_file = None
            self.capture_filename = None
            error_msg = t("ui.data_tab.capture_error").format(error=str(e))
            self._add_message(error_msg)
            logger.error(f"Error setting up capture file: {e}")

    def _close_capture_file(self):
        if self.capture_file:
            try:
                self.capture_file.close()
                self._add_message(t("ui.data_tab.capture_disabled_msg"))
                logger.info(f"Data capture disabled: {self.capture_filename}")
            except Exception as e:
                logger.error(f"Error closing capture file: {e}")
            finally:
                self.capture_file = None
                self.capture_filename = None

    def _refresh_preview(self):
        if not self.preview_enabled.get_value():
            return

        try:
            limit = int(self.preview_limit.get_value())
            self.text_widget.delete("1.0", "end")

            buffer_list = list(self.data_buffer)
            start_idx = max(0, len(buffer_list) - limit + self.preview_offset)
            end_idx = min(len(buffer_list), start_idx + limit)

            for line in buffer_list[start_idx:end_idx]:
                if self.timestamp_enabled.get_value() and self.timestamp_start is not None:
                    timestamp = format_elapsed_since(self.timestamp_start)
                    self.text_widget.insert("end", timestamp + line + "\n")
                else:
                    self.text_widget.insert("end", line + "\n")

            self.text_widget.see("end")
        except tk.TclError:
            pass

    def _add_message(self, message):
        if self.preview_enabled.get_value() and hasattr(self, "text_widget"):
            try:
                self.text_widget.insert("end", f"[MSG] {message}\n")
                self.text_widget.see("end")
            except tk.TclError:
                pass

    def _load_data(self):
        if self.data_buffer:
            result = messagebox.askquestion(
                t("ui.data_tab.overwrite_dialog_title"),
                t("ui.data_tab.overwrite_dialog_message"),
                icon="warning",
            )
            if result != "yes":
                return

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[
                (t("dialogs.text_files"), "*.txt"),
                (t("dialogs.all_files"), "*.*"),
            ],
            title=t("ui.graph_tab.load_dialog_title"),
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
                self._clear_data()
                for line in lines:
                    self.data_buffer.append(line)

                self._update_preview()
                self._add_message(t("ui.data_tab.data_loaded").format(path=file_path))
            except Exception as e:
                self._add_message(t("ui.data_tab.error_loading").format(error=e))

    def _on_timestamp_enabled_change(self, *args):

        if self.timestamp_enabled.get_value():
            self._reset_timestamp()

        if self.preview_enabled.get_value():
            self._refresh_preview()

    def _toggle_preview_pause(self):
        self.preview_paused = not self.preview_paused
        self._update_widget_states()
        if not self.preview_paused and self.preview_enabled.get_value():
            self._update_preview()

    def _reset_timestamp(self):
        self.timestamp_start = time.time()

    def _clear_data(self):
        if hasattr(self, "text_widget"):
            self.text_widget.delete(1.0, "end")

    def _save_data(self):
        buffer_lines = list(self.data_buffer)
        if buffer_lines:
            capture_dir = CAPTURE_DIR
            if not os.path.exists(capture_dir):
                os.makedirs(capture_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"manual_save_{timestamp}.txt"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[(t("dialogs.text_files"), "*.txt")],
                initialdir=capture_dir,
                initialfile=default_filename,
            )

            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        for line in buffer_lines:
                            if self.timestamp_enabled.get_value() and self.timestamp_start is not None:
                                f.write(format_elapsed_since(self.timestamp_start) + line + "\n")
                            else:
                                f.write(line + "\n")
                    self._add_message(
                        t("ui.data_tab.data_saved").format(path=file_path)
                    )
                except Exception as e:
                    self._add_message(t("ui.data_tab.error_saving").format(error=e))

    def add_data(self, line):
        self.data_buffer.append(line)

        if self.timestamp_enabled.get_value() and self.timestamp_start is None:
            self.timestamp_start = time.time()

        if self.capture_enabled.get_value() and self.capture_file:
            try:

                if (
                    self.timestamp_enabled.get_value()
                    and self.timestamp_start is not None
                ):
                    elapsed = time.time() - self.timestamp_start
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    seconds = elapsed % 60
                    timestamp = f"{hours:02d}:{minutes:02d}:{seconds:06.3f} "
                    self.capture_file.write(timestamp + line + "\n")
                else:
                    self.capture_file.write(line + "\n")
                self.capture_file.flush()
            except Exception as e:
                logger.error(f"Error writing to capture file: {e}")
                self._add_message(t("ui.data_tab.capture_error").format(error=str(e)))

        preview_enabled = self.preview_enabled.get_value()
        has_widget = hasattr(self, "text_widget")

        if preview_enabled and not self.preview_paused and has_widget:
            try:
                self._update_preview()
            except Exception as e:
                logger.error(f"Error in auto preview update: {e}")

    def _update_preview(self):
        if not hasattr(self, "text_widget") or not self.preview_enabled.get_value():
            return

        try:
            limit = int(self.preview_limit.get_value())

            buffer_lines = list(self.data_buffer)
            lines_to_show = (
                buffer_lines[-limit:] if len(buffer_lines) > limit else buffer_lines
            )

            formatted_lines = []
            for line in lines_to_show:
                if self.timestamp_enabled.get_value() and self.timestamp_start is not None:
                    formatted_lines.append(format_elapsed_since(self.timestamp_start) + line)
                else:
                    formatted_lines.append(line)

            self.text_widget.delete("1.0", "end")
            if formatted_lines:
                content = "\n".join(formatted_lines)
                self.text_widget.insert("1.0", content)
            self.text_widget.see("end")

        except Exception as e:
            logger.error(f"Error updating preview: {e}")

    def add_message(self, message):
        self._add_message(message)

    def get_frame(self):
        return self.frame

    def get_data(self):
        return list(self.data_buffer)

    def cleanup(self):
        if self.capture_file:
            try:
                self.capture_file.close()
                logger.info(
                    f"Capture file closed during cleanup: {self.capture_filename}"
                )
            except Exception as e:
                logger.error(f"Error closing capture file during cleanup: {e}")
            finally:
                self.capture_file = None
                self.capture_filename = None
