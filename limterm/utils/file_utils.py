from tkinter import filedialog
from ..i18n import t


class FileManager:
    @staticmethod
    def save_data_to_file(data, default_extension=".txt"):
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=[(t("dialogs.text_files"), "*.txt")],
        )

        if file_path:
            with open(file_path, "w") as file:
                if isinstance(data, list):
                    file.write("\n".join(data))
                else:
                    file.write(str(data))
            return file_path
        return None
