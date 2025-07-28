import tkinter as tk
from tkinter import ttk
from ..utils import FileManager
from ..i18n import t


class DataTab:
    def _on_user_scroll(self, event=None):
        self.autoscroll = self._is_scrolled_to_end()

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.data = []

        self._create_widgets()

    def _create_widgets(self):
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(expand=1, fill="both", padx=10, pady=10)

        self.data_text = tk.Text(text_frame, wrap="word")
        self.data_text.pack(side="left", expand=1, fill="both")

        self.scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.data_text.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.data_text.config(yscrollcommand=self.scrollbar.set)

        self.save_button = ttk.Button(
            self.frame, text=t("ui.data_tab.save"), command=self._save_data
        )
        self.save_button.pack(side="left", padx=10, pady=10)

        self.load_button = ttk.Button(
            self.frame, text=t("ui.data_tab.load"), command=self._load_data
        )
        self.load_button.pack(side="left", padx=10, pady=10)

        self.clear_button = ttk.Button(
            self.frame, text=t("ui.data_tab.clear"), command=self._clear_data
        )
        self.clear_button.pack(side="left", padx=10, pady=10)

        self.autosave_var = tk.BooleanVar(value=False)
        self.autosave_checkbox = ttk.Checkbutton(
            self.frame,
            text=t("ui.data_tab.autosave"),
            variable=self.autosave_var,
            command=self._on_autosave_toggle,
        )
        self.autosave_checkbox.pack(side="left", padx=10, pady=10)

        self.autosave_file = None
        self.autosave_filename = None

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
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
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

    def _on_autosave_toggle(self):
        import os
        import datetime

        if self.autosave_var.get():
            output_dir = "autosave"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            now = datetime.datetime.now()
            fname = f"data-{now.strftime('%Y-%m-%d-%H%M%S')}.txt"
            self.autosave_filename = os.path.join(output_dir, fname)

            try:
                self.autosave_file = open(self.autosave_filename, "a", encoding="utf-8")
                print(f"Autosave enabled: {self.autosave_filename}")
            except Exception as e:
                print(f"Error opening autosave file: {e}")
                self.autosave_var.set(False)
                self.autosave_file = None
                self.autosave_filename = None
        else:
            if self.autosave_file:
                try:
                    self.autosave_file.close()
                    print(f"Autosave disabled: {self.autosave_filename}")
                except Exception as e:
                    print(f"Error closing autosave file: {e}")
                finally:
                    self.autosave_file = None
                    self.autosave_filename = None

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

            if self.autosave_var.get() and self.autosave_file:
                try:
                    self.autosave_file.write(line + "\n")
                    self.autosave_file.flush()
                except Exception as e:
                    print(f"Error writing to autosave file: {e}")

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
        if self.autosave_file:
            try:
                self.autosave_file.close()
                print(f"Autosave file closed during cleanup: {self.autosave_filename}")
            except Exception as e:
                print(f"Error closing autosave file during cleanup: {e}")
            finally:
                self.autosave_file = None
                self.autosave_filename = None
