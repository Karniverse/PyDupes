import os
import hashlib
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class DuplicateFilesFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Files Finder")

        self.file_list = []
        self.duplicates = []

        self.create_widgets()

    def create_widgets(self):
        self.label = tk.Label(self.root, text="Select a directory to find duplicate files:")
        self.label.pack(pady=10)

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_directory)
        self.browse_button.pack(pady=10)

        self.find_duplicates_button = tk.Button(self.root, text="Find Duplicates", command=self.find_duplicates)
        self.find_duplicates_button.pack(pady=10)

        self.auto_select_button = tk.Button(self.root, text="Auto Select Duplicates", command=self.auto_select_duplicates)
        self.auto_select_button.pack(pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10)

        # Create a Frame to contain the Text widget and the scrollbar
        frame = tk.Frame(self.root)
        frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.result_text = tk.Text(frame, wrap=tk.WORD, height=10, width=60)
        self.result_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)  # Pack with expand and fill options

        # Add a vertical scrollbar to the Frame
        scrollbar = tk.Scrollbar(frame, command=self.result_text.yview, cursor="hand2")  # Set the cursor to hand2
        scrollbar.bind("<Enter>", lambda event: self.root.config(cursor="hand2"))  # Change cursor on hover
        scrollbar.bind("<Leave>", lambda event: self.root.config(cursor=""))  # Change cursor back on leave
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)

        self.delete_button = tk.Button(self.root, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.file_list = self.get_files_in_directory(directory)

    def get_files_in_directory(self, directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    def hash_file(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def find_duplicates(self):
        self.duplicates = []
        seen_hashes = {}
        total_files = len(self.file_list)

        for i, file_path in enumerate(self.file_list):
            file_hash = self.hash_file(file_path)

            if file_hash in seen_hashes:
                # Compare modification timestamps
                current_timestamp = os.path.getmtime(file_path)
                existing_timestamp = os.path.getmtime(seen_hashes[file_hash])

                # Keep the file with the earliest modification timestamp
                if current_timestamp < existing_timestamp:
                    self.duplicates.append(file_path)
                else:
                    self.duplicates.append(seen_hashes[file_hash])
                    seen_hashes[file_hash] = file_path
            else:
                seen_hashes[file_hash] = file_path

            # Update progress bar
            progress_percentage = (i + 1) / total_files * 100
            self.progress_var.set(progress_percentage)
            self.root.update_idletasks()

        self.display_result()

    def display_result(self):
        self.result_text.delete(1.0, tk.END)  # Clear existing content

        for duplicate in self.duplicates:
            self.add_checkbox_to_result_text(duplicate)

    def add_checkbox_to_result_text(self, file_path):
        checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(self.result_text, variable=checkbox_var, onvalue=True, offvalue=False,
                                  cursor="hand2")  # Set the cursor to hand2
        checkbox.bind("<Enter>", lambda event: self.root.config(cursor="hand2"))  # Change cursor on hover
        checkbox.bind("<Leave>", lambda event: self.root.config(cursor=""))  # Change cursor back on leave
        self.result_text.window_create(tk.END, window=checkbox)
        self.result_text.insert(tk.END, f" {file_path}\n")
        self.result_text.tag_add("checkbox", self.result_text.index(tk.END) + "-1l", tk.END)
        checkbox.var = checkbox_var

    def auto_select_duplicates(self):
        for checkbox in self.result_text.children.values():
            checkbox.var.set(True)

    def delete_selected(self):
        selected_checkboxes = [checkbox.var for checkbox in self.result_text.children.values() if checkbox.var.get()]

        for checkbox_var in selected_checkboxes:
            checkbox_var.set(False)

        # Implement file deletion using os.remove for selected files
        for file_path in selected_checkboxes:
            try:
                os.remove(file_path.get())
            except Exception as e:
                print(f"Error deleting {file_path.get()}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFilesFinder(root)
    root.mainloop()
