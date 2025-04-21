# Why the frick did I write a gui in python, this sucks.
import os
import webbrowser
import tkinter as tk
from tkinter import ttk
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

        self.playtime_var = tk.BooleanVar(value=config.PLAYTIME_MODE)
        self.min_millis_var = tk.IntVar(value=config.MIN_MILLISECONDS)
        self.input_dir_var = tk.StringVar(value=config.INPUT_DIR)
        self.output_file_var = tk.StringVar(value=config.OUTPUT_FILE)
        self.items_per_page_var = tk.IntVar(value=config.ITEMS_PER_PAGE)

        self.build_ui()

    def build_ui(self):
        padding = {'padx': 10, 'pady': 5}

        # Playback Mode Section
        mode_frame = ttk.LabelFrame(self.root, text="How to Rank")
        mode_frame.grid(row=0, column=0, sticky="ew", **padding)

        ttk.Checkbutton(
            mode_frame,
            text="Use total playtime instead of number of plays",
            variable=self.playtime_var,
            command=self.toggle_millis_field
        ).pack(anchor="w", padx=10, pady=5)

        ttk.Label(
            mode_frame,
            text="Checked: Ranked by how long you listened to each Artist/Song/Album\n"
                 "Unchecked: Ranked by how many times you listened"
        ).pack(anchor="w", padx=10)

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

        self.toggle_millis_field()

    def toggle_millis_field(self):
        if self.playtime_var.get():
            self.millis_frame.grid_remove()
        else:
            self.millis_frame.grid()

    def run(self):
        # Update config values from UI
        config.PLAYTIME_MODE = self.playtime_var.get()
        config.MIN_MILLISECONDS = int(self.min_millis_var.get())
        config.INPUT_DIR = self.input_dir_var.get()
        config.OUTPUT_FILE = self.output_file_var.get()
        config.ITEMS_PER_PAGE = self.items_per_page_var.get()

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