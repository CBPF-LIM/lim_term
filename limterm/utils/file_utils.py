from ..i18n import t
from ..utils.ui_builder import ask_save_as


class FileManager:
    @staticmethod
    def save_data_to_file(data, default_extension=".txt"):
        file_path = ask_save_as(
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
