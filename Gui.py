# Why the frick did I write a gui in python, this sucks.
import os
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import importlib.util
from GenerateHTMLSummary import count_plays_from_directory, VERSION

CONFIG_PATH = "config.py"

def load_config():
    spec = importlib.util.spec_from_file_location("config", CONFIG_PATH)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config

config = load_config()

def load_style(root):
    style = ttk.Style(root)
    style.theme_use("default")

    root.configure(bg="#121212")

    style.configure("TLabel", background="#121212", foreground="#e0e0e0", font=("Helvetica", 12))
    style.configure("TCheckbutton", background="#121212", foreground="#e0e0e0", font=("Helvetica", 16))
    style.map("TCheckbutton", background=[('active', '#3a3a3a'), ('!active', '#2a2a2a')], foreground=[('active', '#ffffff'), ('!active', '#e0e0e0')])
    style.configure("TEntry", fieldbackground="#1e1e1e", foreground="#e0e0e0", background="#121212", font=("Helvetica", 16))
    style.configure("TButton", background="#2a2a2a", foreground="#e0e0e0", font=("Helvetica", 16))
    style.map("TButton", background=[('active', '#3a3a3a'), ('!active', '#2a2a2a')], foreground=[('active', '#ffffff'), ('!active', '#e0e0e0')])
    style.configure("TFrame", background="#121212", font=("Helvetica", 16))
    style.configure("TLabelframe", background="#121212", foreground="#e0e0e0", font=("Helvetica", 16))
    style.configure("TLabelframe.Label", background="#121212", foreground="#e0e0e0", font=("Helvetica", 16))

class ConfigApp:
    def __init__(self, root):
        self.root = root
        root.title("SESH Summary Config - V:" + VERSION)

        self.min_millis_var = tk.IntVar(value=config.MIN_MILLISECONDS)
        self.input_dir_var = tk.StringVar(value=config.INPUT_DIR)
        self.output_file_var = tk.StringVar(value=config.OUTPUT_FILE)
        self.items_per_page_var = tk.IntVar(value=config.ITEMS_PER_PAGE)

        self.build_ui()

    def build_ui(self):
        padding = {'padx': 10, 'pady': 5}

        # Minimum Milliseconds (hidden if playtime mode is on)
        self.millis_frame = ttk.LabelFrame(self.root, text="Minimum Milliseconds")
        self.millis_frame.grid(row=1, column=0, sticky="ew", **padding)

        ttk.Label(
            self.millis_frame,
            text="Minimum number of milliseconds for a listen to count.\n"
                 "Changing this will drastically alter the final results."
        ).pack(anchor="w", padx=10, pady=(5, 0))

        ttk.Entry(self.millis_frame, textvariable=self.min_millis_var, width=10, font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        # Input Directory
        input_frame = ttk.LabelFrame(self.root, text="Input Directory")
        input_frame.grid(row=2, column=0, sticky="ew", **padding)

        ttk.Label(
            input_frame,
            text="Folder where your Spotify JSON files are located.\n"
                 "Easiest method is to put them in the default 'sesh' folder."
        ).pack(anchor="w", padx=10, pady=(5, 0))

        ttk.Entry(input_frame, textvariable=self.input_dir_var, width=40, font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        # Output File
        output_frame = ttk.LabelFrame(self.root, text="Output File")
        output_frame.grid(row=3, column=0, sticky="ew", **padding)

        ttk.Label(
            output_frame,
            text="Name of the output HTML file.\n"
                 "If unchanged, it will be created in the current folder."
        ).pack(anchor="w", padx=10, pady=(5, 0))

        ttk.Entry(output_frame, textvariable=self.output_file_var, width=40, font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        # Items per Page
        page_frame = ttk.LabelFrame(self.root, text="Items Per Page")
        page_frame.grid(row=4, column=0, sticky="ew", **padding)

        ttk.Label(
            page_frame,
            text="How many items to show per table page in the output HTML."
        ).pack(anchor="w", padx=10, pady=(5, 0))

        ttk.Entry(page_frame, textvariable=self.items_per_page_var, width=10, font=("Helvetica", 14)).pack(anchor="w", padx=10, pady=5)

        # Run Button
        ttk.Button(self.root, text="Generate Summary", command=self.run).grid(row=5, column=0, pady=15)

    def validate_inputs(self):
        """
        Validate user inputs before processing.

        Returns:
            bool: True if all inputs are valid, False otherwise
        """
        # Validate minimum milliseconds
        try:
            min_ms = int(self.min_millis_var.get())
            if min_ms < 0:
                tk.messagebox.showerror("Invalid Input", "Minimum milliseconds must be a positive number. This value determines how long a track must be played to count as a listen.")
                return False
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Minimum milliseconds must be a number. Please enter a valid integer value (e.g., 20000 for 20 seconds).")
            return False

        # Validate input directory
        input_dir = self.input_dir_var.get().strip()
        if not input_dir:
            tk.messagebox.showerror("Invalid Input", "Input directory cannot be empty. Please specify the folder where your Spotify JSON files are located.")
            return False
        if not os.path.exists(input_dir):
            response = tk.messagebox.askquestion("Directory Not Found", 
                f"The directory '{input_dir}' does not exist. Would you like to create it?")
            if response == 'yes':
                try:
                    os.makedirs(input_dir, exist_ok=True)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Failed to create directory: {e}")
                    return False
            else:
                return False

        # Validate output file
        output_file = self.output_file_var.get().strip()
        if not output_file:
            tk.messagebox.showerror("Invalid Input", "Output file name cannot be empty. Please specify a name for the HTML report file that will be generated.")
            return False
        try:
            # Check if the directory part of the path exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                response = tk.messagebox.askquestion("Directory Not Found", 
                    f"The directory for output file '{output_dir}' does not exist. Would you like to create it?")
                if response == 'yes':
                    os.makedirs(output_dir, exist_ok=True)
                else:
                    return False
        except Exception as e:
            tk.messagebox.showerror("Error", f"Invalid output file path: {e}")
            return False

        # Validate items per page
        try:
            items_per_page = int(self.items_per_page_var.get())
            if items_per_page <= 0:
                tk.messagebox.showerror("Invalid Input", "Items per page must be a positive number. This controls how many items are displayed per page in the generated HTML report.")
                return False
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Items per page must be a number. Please enter a valid integer value (e.g., 10).")
            return False

        return True

    def run(self):
        # Validate inputs before processing
        if not self.validate_inputs():
            return

        # Update config values from UI
        config.MIN_MILLISECONDS = int(self.min_millis_var.get())
        config.INPUT_DIR = self.input_dir_var.get().strip()
        config.OUTPUT_FILE = self.output_file_var.get().strip()
        config.ITEMS_PER_PAGE = int(self.items_per_page_var.get())

        # Run your main function
        count_plays_from_directory(config)

        # Show the result window
        result_win = tk.Toplevel(self.root)
        result_win.title("Report Generated")
        result_win.geometry("400x150")
        result_win.configure(bg="#1e1e1e")  # dark background

        # Message
        label = ttk.Label(result_win,
                          text=f"✅ HTML report generated:\n{config.OUTPUT_FILE + '.html'}\n\nWould you like to open it or close the app?",
                          justify="center",
                          anchor="center")
        label.pack(pady=20)

        # Buttons
        button_frame = ttk.Frame(result_win)
        button_frame.pack()

        def open_file():
            webbrowser.open('file://' + os.path.realpath(config.OUTPUT_FILE + ".html"))
            result_win.destroy()

        def close_app():
            self.root.quit()

        ttk.Button(button_frame, text="Open Report", command=open_file).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Close App", command=close_app).pack(side="right", padx=10)
