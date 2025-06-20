import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

MENU_FILE = "menu.json"

class MenuSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Menu Setup")

        # Section Labels
        ttk.Label(root, text="Healthy Meal Options").grid(row=0, column=0, sticky="w")
        self.healthy_frame = ttk.Frame(root)
        self.healthy_frame.grid(row=1, column=0, padx=10, pady=5)

        ttk.Label(root, text="Today's Special - Meats").grid(row=2, column=0, sticky="w")
        self.meat_frame = ttk.Frame(root)
        self.meat_frame.grid(row=3, column=0, padx=10, pady=5)

        ttk.Label(root, text="Today's Special - Side Combos").grid(row=4, column=0, sticky="w")
        self.side_frame = ttk.Frame(root)
        self.side_frame.grid(row=5, column=0, padx=10, pady=5)

        # Add Buttons
        ttk.Button(root, text="+", command=self.add_healthy_meal).grid(row=1, column=1, sticky="n")
        ttk.Button(root, text="+", command=self.add_meat).grid(row=3, column=1, sticky="n")
        ttk.Button(root, text="+", command=self.add_side).grid(row=5, column=1, sticky="n")

        # Save & Clear Buttons
        self.save_button = ttk.Button(root, text="Save Menu", command=self.save_menu)
        self.save_button.grid(row=6, column=0, pady=10, sticky="w", padx=10)

        self.clear_button = ttk.Button(root, text="Clear", command=self.clear_menu)
        self.clear_button.grid(row=6, column=1, pady=10, sticky="e", padx=10)

        # Lists to track widgets
        self.healthy_meals = []
        self.meat_entries = []
        self.side_entries = []

        # Load existing menu if available
        existing_menu = self.load_existing_menu()

        if existing_menu:
            for name, price in existing_menu.get("healthy_meal", {}).get("name", {}).items():
                self.add_healthy_meal(name, str(price))
            for name, price in existing_menu.get("todays_special", {}).get("meats", {}).items():
                self.add_meat(name, str(price))
            for side in existing_menu.get("todays_special", {}).get("sides", []):
                self.add_side(side)
        else:
            self.add_healthy_meal()
            self.add_meat()
            self.add_meat()
            self.add_side()
            self.add_side()

    def load_existing_menu(self):
        if os.path.exists(MENU_FILE):
            try:
                with open(MENU_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Warning", "Menu file is corrupted. Starting fresh.")
        return None

    def add_healthy_meal(self, name="", price=""):
        name_entry = ttk.Entry(self.healthy_frame, width=25)
        name_entry.insert(0, name)

        price_entry = ttk.Entry(self.healthy_frame, width=10)
        price_entry.insert(0, price)

        remove_btn = ttk.Button(self.healthy_frame, text="−")
        widget_tuple = (name_entry, price_entry, remove_btn)
        self.healthy_meals.append(widget_tuple)
        index = len(self.healthy_meals) - 1

        name_entry.grid(row=index, column=0)
        price_entry.grid(row=index, column=1)
        remove_btn.config(command=lambda: self.remove_entry(self.healthy_meals, self.healthy_frame, widget_tuple))
        remove_btn.grid(row=index, column=2)

    def add_meat(self, name="", price=""):
        name_entry = ttk.Entry(self.meat_frame, width=25)
        name_entry.insert(0, name)

        price_entry = ttk.Entry(self.meat_frame, width=10)
        price_entry.insert(0, price)

        remove_btn = ttk.Button(self.meat_frame, text="−")
        widget_tuple = (name_entry, price_entry, remove_btn)
        self.meat_entries.append(widget_tuple)
        index = len(self.meat_entries) - 1

        name_entry.grid(row=index, column=0)
        price_entry.grid(row=index, column=1)
        remove_btn.config(command=lambda: self.remove_entry(self.meat_entries, self.meat_frame, widget_tuple))
        remove_btn.grid(row=index, column=2)

    def add_side(self, text=""):
        side_entry = ttk.Entry(self.side_frame, width=50)
        side_entry.insert(0, text)

        remove_btn = ttk.Button(self.side_frame, text="−")
        widget_tuple = (side_entry, remove_btn)
        self.side_entries.append(widget_tuple)
        index = len(self.side_entries) - 1

        side_entry.grid(row=index, column=0)
        remove_btn.config(command=lambda: self.remove_entry(self.side_entries, self.side_frame, widget_tuple))
        remove_btn.grid(row=index, column=1)

    def remove_entry(self, entry_list, frame, widget_tuple):
        if widget_tuple in entry_list:
            for widget in widget_tuple:
                widget.destroy()
            entry_list.remove(widget_tuple)

            for i, widgets in enumerate(entry_list):
                for j, widget in enumerate(widgets):
                    widget.grid(row=i, column=j)

    def clear_menu(self):
        for entries, frame in [(self.healthy_meals, self.healthy_frame),
                               (self.meat_entries, self.meat_frame),
                               (self.side_entries, self.side_frame)]:
            for widgets in entries:
                for widget in widgets:
                    widget.destroy()
            entries.clear()

    def save_menu(self):
        menu = {}

        # Healthy meals
        healthy_options = {}
        try:
            for widgets in self.healthy_meals:
                name = widgets[0].get().strip()
                price = float(widgets[1].get())
                if name:
                    healthy_options[name] = price
        except ValueError:
            messagebox.showerror("Error", "Invalid price in healthy meal options.")
            return

        menu["healthy_meal"] = {"name": healthy_options}

        # Meats
        meats = {}
        try:
            for widgets in self.meat_entries:
                name = widgets[0].get().strip()
                price = float(widgets[1].get())
                if name:
                    meats[name] = price
        except ValueError:
            messagebox.showerror("Error", "Invalid price in meat options.")
            return

        # Sides
        sides = [widgets[0].get().strip() for widgets in self.side_entries if widgets[0].get().strip()]

        menu["todays_special"] = {
            "meats": meats,
            "sides": sides
        }

        with open(MENU_FILE, "w") as f:
            json.dump(menu, f, indent=2)

        messagebox.showinfo("Saved", "Menu saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MenuSetupApp(root)
    root.mainloop()