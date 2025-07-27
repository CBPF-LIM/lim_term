from tkinter import filedialog


class FileManager:


    @staticmethod
    def save_data_to_file(data, default_extension=".txt"):

        file_path = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=[("Text files", "*.txt")]
        )

        if file_path:
            with open(file_path, "w") as file:
                if isinstance(data, list):
                    file.write("\n".join(data))
                else:
                    file.write(str(data))
            return file_path
        return None
