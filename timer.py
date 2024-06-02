import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import json

# Constants
HOURS = 100
APP_FILE = 'applications.json'

class AppSelector:
    def __init__(self, root):
        self.root = root

        self.root.title("Select or Create Application")

        # Load existing applications
        self.load_applications()

        # Create widgets
        self.create_widgets()

    def load_applications(self):
        try:
            with open(APP_FILE, "r") as file:
                self.app_data = json.load(file)
        except FileNotFoundError:
            self.app_data = {}

    def save_applications(self):
        with open(APP_FILE, "w") as file:
            json.dump(self.app_data, file)

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="Select an Application or Create a New One:", font=("Helvetica", 14))
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.app_var = tk.StringVar()
        self.app_menu = ttk.Combobox(self.root, textvariable=self.app_var, values=list(self.app_data.keys()), state="readonly")
        self.app_menu.grid(row=1, column=0, columnspan=2, padx=20, pady=10)

        self.create_button = ttk.Button(self.root, text="Create New Application", command=self.show_create_window, bootstyle="info")
        self.create_button.grid(row=2, column=0, padx=20, pady=10)

        self.select_button = ttk.Button(self.root, text="Select Application", command=self.select_app, bootstyle="success")
        self.select_button.grid(row=2, column=1, padx=20, pady=10)

    def show_create_window(self):
        self.create_window = tk.Toplevel(self.root)
        self.create_window.title("Create New Application")

        self.new_app_var = tk.StringVar()

        self.label_new_app = ttk.Label(self.create_window, text="Enter Application Name:", font=("Helvetica", 14))
        self.label_new_app.pack(padx=20, pady=20)

        self.entry_new_app = ttk.Entry(self.create_window, textvariable=self.new_app_var)
        self.entry_new_app.pack(padx=20, pady=10)

        self.button_create_app = ttk.Button(self.create_window, text="Create", command=self.create_app, bootstyle="success")
        self.button_create_app.pack(padx=20, pady=10)

    def create_app(self):
        app_name = self.new_app_var.get().strip()
        if app_name:
            if app_name not in self.app_data:
                self.app_data[app_name] = 3600 * HOURS  # Default to 100 hours
                self.save_applications()
                self.on_app_selected(app_name)
                self.create_window.destroy()
                self.root.withdraw()
            else:
                tk.messagebox.showerror("Error", "Application name already exists.")
        else:
            tk.messagebox.showerror("Error", "Application name cannot be empty.")

    def select_app(self):
        app_name = self.app_var.get().strip()
        if app_name:
            self.on_app_selected(app_name)
            self.root.withdraw()
        else:
            tk.messagebox.showerror("Error", "Please select an application.")

    def on_app_selected(self, app_name):
        CountdownApp(self.root, app_name, self.app_data)

class CountdownApp:
    def __init__(self, root, app_name, app_data):
        self.parent_root = root
        self.root = tk.Toplevel(root)
        self.root.title(f"Countdown Timer - {app_name}")
        self.app_name = app_name
        self.app_data = app_data

        # Variables
        self.total_seconds = self.app_data[self.app_name]
        self.time_left = tk.IntVar(value=self.total_seconds)
        self.running = False

        # Create Widgets
        self.create_widgets()

        # Update the time display
        self.update_display()

        # Bind the window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Frame for grid layout
        frame = ttk.Frame(self.root)
        frame.pack(expand=True, fill="both")

        # Time display
        self.time_label = ttk.Label(frame, font=("Helvetica", 48), style="success.TLabel")
        self.time_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Start/Stop Button
        self.start_stop_button = ttk.Button(frame, text="Start", command=self.toggle_start_stop, bootstyle="success")
        self.start_stop_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Reset Button
        self.reset_button = ttk.Button(frame, text="Reset", command=self.reset, bootstyle="info")
        self.reset_button.grid(row=2, column=2, padx=10, pady=10, sticky="se")

    def toggle_start_stop(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if not self.running:
            self.running = True
            self.start_stop_button.config(text="Stop", bootstyle="danger")
            self.countdown()

    def stop(self):
        self.running = False
        self.start_stop_button.config(text="Start", bootstyle="success")

    def reset(self):
        self.time_left.set(3600 * HOURS)
        self.update_display()

    def countdown(self):
        if self.running and self.time_left.get() > 0:
            self.time_left.set(self.time_left.get() - 1)
            self.update_display()
            self.root.after(1000, self.countdown)
        else:
            self.running = False

    def update_display(self):
        total_seconds = self.time_left.get()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_label.config(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))

    def on_closing(self):
        self.running = False
        self.confirm_window = tk.Toplevel(self.root)
        self.confirm_window.title("Save Timer")
        
        label = ttk.Label(self.confirm_window, text="Do you want to save the current time for next time?", font=("Helvetica", 14))
        label.pack(padx=20, pady=20)

        button_frame = ttk.Frame(self.confirm_window)
        button_frame.pack(pady=10)

        yes_button = ttk.Button(button_frame, text="Yes", command=self.save_time, bootstyle="success")
        yes_button.grid(row=0, column=0, padx=10)

        no_button = ttk.Button(button_frame, text="No", command=self.exit_without_saving, bootstyle="danger")
        no_button.grid(row=0, column=1, padx=10)

    def save_time(self):
        self.app_data[self.app_name] = self.time_left.get()
        with open(APP_FILE, "w") as file:
            json.dump(self.app_data, file)
        self.confirm_window.destroy()
        self.root.destroy()
        self.parent_root.destroy()

    def exit_without_saving(self):
        self.confirm_window.destroy()
        self.root.destroy()
        self.parent_root.destroy()

if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app_selector = AppSelector(root)
    root.mainloop()
