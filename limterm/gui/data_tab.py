import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ..utils import FileManager
from ..i18n import t, get_config_manager
from .preference_widgets import PrefCheckbutton, PrefCombobox, PrefEntry
import logging
import os
import datetime

logger = logging.getLogger(__name__)


class DataTab:
    def _on_user_scroll(self, event=None):
        self.autoscroll = self._is_scrolled_to_end()

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.data = []
        self.config_manager = get_config_manager()
        self.capture_file = None
        self.capture_filename = None

        self._create_widgets()

    def _create_widgets(self):
        settings_frame = ttk.LabelFrame(
            self.frame, text=t("ui.data_tab.data_capture_settings")
        )
        settings_frame.pack(fill="x", padx=10, pady=10)

        self.capture_enabled = PrefCheckbutton(
            settings_frame,
            pref_key="data_capture.enabled",
            default_value=False,
            text=t("ui.data_tab.capture_enabled"),
            on_change=self._on_capture_enabled_change,
        )
        self.capture_enabled.grid(column=0, row=0, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Label(settings_frame, text=t("ui.data_tab.filename_mode_label")).grid(
            column=0, row=1, padx=5, pady=5, sticky="w"
        )
        self.filename_mode = PrefCombobox(
            settings_frame,
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
            width=15,
            on_change=self._on_filename_mode_change,
        )
        self.filename_mode.grid(column=1, row=1, padx=5, pady=5, sticky="w")

        ttk.Label(settings_frame, text=t("ui.data_tab.fixed_filename_label")).grid(
            column=0, row=2, padx=5, pady=5, sticky="w"
        )
        self.fixed_filename = PrefEntry(
            settings_frame,
            pref_key="data_capture.fixed_filename",
            default_value="data.txt",
            width=20,
            on_change=self._on_capture_setting_change,
        )
        self.fixed_filename.grid(column=1, row=2, padx=5, pady=5, sticky="w")

        ttk.Label(settings_frame, text=t("ui.data_tab.file_mode_label")).grid(
            column=0, row=3, padx=5, pady=5, sticky="w"
        )
        self.file_mode = PrefCombobox(
            settings_frame,
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
            width=15,
            on_change=self._on_capture_setting_change,
        )
        self.file_mode.grid(column=1, row=3, padx=5, pady=5, sticky="w")

        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.save_button = ttk.Button(
            button_frame, text=t("ui.data_tab.save"), command=self._save_data
        )
        self.save_button.pack(side="left", padx=5)

        self.load_button = ttk.Button(
            button_frame, text=t("ui.data_tab.load"), command=self._load_data
        )
        self.load_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(
            button_frame, text=t("ui.data_tab.clear"), command=self._clear_data
        )
        self.clear_button.pack(side="left", padx=5)

        text_frame = ttk.Frame(self.frame)
        text_frame.pack(expand=1, fill="both", padx=10, pady=5)

        self.data_text = tk.Text(text_frame, wrap="word", height=15)
        self.data_text.pack(side="left", expand=1, fill="both")

        self.scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.data_text.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.data_text.config(yscrollcommand=self.scrollbar.set)

        self._update_widget_states()
        self._setup_initial_capture_state()

    def _update_widget_states(self):
        filename_mode = self.filename_mode.get_value()
        if filename_mode == "fixed":
            self.fixed_filename.config(state="normal")
            self.file_mode.config(state="readonly")
        else:
            self.fixed_filename.config(state="disabled")
            self.file_mode.config(state="disabled")

    def _setup_initial_capture_state(self):
        if self.capture_enabled.get_value():
            self._setup_capture_file()

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

    def _setup_capture_file(self):
        try:
            filename_mode = self.filename_mode.get_value()
            
            if filename_mode == "auto":
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.capture_filename = f"data_capture_{timestamp}.txt"
            else:
                self.capture_filename = self.fixed_filename.get_value()

            file_mode = self.file_mode.get_value()
            mode = "a" if file_mode == "append" else "w"

            self.capture_file = open(self.capture_filename, mode, encoding="utf-8")
            
            self.add_message(t("ui.data_tab.capture_enabled_msg").format(filename=self.capture_filename))
            logger.info(f"Data capture enabled: {self.capture_filename} (mode: {mode})")

        except Exception as e:
            self.capture_enabled.set_value(False)
            self.capture_file = None
            self.capture_filename = None
            error_msg = t("ui.data_tab.capture_error").format(error=str(e))
            self.add_message(error_msg)
            logger.error(f"Error setting up capture file: {e}")

    def _close_capture_file(self):
        if self.capture_file:
            try:
                self.capture_file.close()
                self.add_message(t("ui.data_tab.capture_disabled_msg"))
                logger.info(f"Data capture disabled: {self.capture_filename}")
            except Exception as e:
                logger.error(f"Error closing capture file: {e}")
            finally:
                self.capture_file = None
                self.capture_filename = None

    def _load_data(self):
        from tkinter import filedialog, messagebox

        if self.data:
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
                    self.data.append({"type": "data", "value": line})
                    self.data_text.insert("end", line + "\n")
                self.data_text.see("end")
                self.add_message(t("ui.data_tab.data_loaded").format(path=file_path))
            except Exception as e:
                self.add_message(t("ui.data_tab.error_loading").format(error=e))

        self.autoscroll = True
        self.data_text.bind("<Button-1>", self._on_user_scroll)
        self.data_text.bind("<MouseWheel>", self._on_user_scroll)
        self.data_text.bind("<Key>", self._on_user_scroll)
        self.data_text.bind("<ButtonRelease-1>", self._on_user_scroll)
        self.data_text.bind("<Configure>", self._on_user_scroll)

    def _clear_data(self):
        self.data.clear()
        self.data_text.delete("1.0", "end")

        self.autoscroll = True
        self.data_text.bind("<Button-1>", self._on_user_scroll)
        self.data_text.bind("<MouseWheel>", self._on_user_scroll)
        self.data_text.bind("<Key>", self._on_user_scroll)
        self.data_text.bind("<ButtonRelease-1>", self._on_user_scroll)
        self.data_text.bind("<Configure>", self._on_user_scroll)

    def add_data(self, line, save_to_history=True):
        if save_to_history:
            self.data.append({"type": "data", "value": line})

            if self.capture_enabled.get_value() and self.capture_file:
                try:
                    self.capture_file.write(line + "\n")
                    self.capture_file.flush()
                except Exception as e:
                    logger.error(f"Error writing to capture file: {e}")
                    self.add_message(t("ui.data_tab.capture_error").format(error=str(e)))

        try:
            at_end = self._is_scrolled_to_end()
            self.data_text.insert("end", line + "\n")
            if at_end:
                self.data_text.see("end")
        except tk.TclError:
            pass

    def add_message(self, message):
        self.data.append({"type": "msg", "value": message})
        try:
            at_end = self._is_scrolled_to_end()
            self.data_text.insert("end", message + "\n")
            if at_end:
                self.data_text.see("end")
        except tk.TclError:
            pass

    def _is_scrolled_to_end(self):
        try:
            last_visible = self.data_text.index("@0,%d" % self.data_text.winfo_height())
            end_index = self.data_text.index("end-1c")

            return last_visible >= end_index
        except tk.TclError:
            return True

    def _save_data(self):
        valid_lines = [item["value"] for item in self.data if item["type"] == "data"]
        if valid_lines:
            file_path = FileManager.save_data_to_file(valid_lines)
            if file_path:
                self.add_message(t("ui.data_tab.data_saved").format(path=file_path))

    def get_frame(self):
        return self.frame

    def get_data(self):
        return [item["value"] for item in self.data if item["type"] == "data"]

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
