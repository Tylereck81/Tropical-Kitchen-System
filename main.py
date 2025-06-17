import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"

def save_menu(menu):
    with open(MENU_FILE, "w") as f:
        json.dump(menu, f)

def load_menu():
    if os.path.exists(MENU_FILE):
        with open(MENU_FILE, "r") as f:
            return json.load(f)
    return None

def save_orders(orders):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

class TakeoutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Takeout Order Tracker")

        self.menu = load_menu()
        self.orders = load_orders()
        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="Customer Name:").grid(row=0, column=0, sticky="e")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(row=0, column=1)

        ttk.Label(self, text="Phone Number:").grid(row=1, column=0, sticky="e")
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=1, column=1)

        ttk.Label(self, text="Meal Type:").grid(row=2, column=0, sticky="e")
        self.meal_type = tk.StringVar()
        self.meal_type_combo = ttk.Combobox(self, textvariable=self.meal_type, values=["Healthy Meal", "Today's Special"], state="readonly")
        self.meal_type_combo.grid(row=2, column=1)
        self.meal_type_combo.bind("<<ComboboxSelected>>", self.update_meal_options)

        self.healthy_frame = ttk.Frame(self)
        self.healthy_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Label(self.healthy_frame, text="Select Healthy Option:").grid(row=0, column=0, sticky="e")
        self.healthy_choice = tk.StringVar()
        # healthy_names = [item["name"] for item in self.menu.get("healthy_meals", [])]
        self.healthy_combo = ttk.Combobox(self.healthy_frame, textvariable=self.healthy_choice, values=list(self.menu["healthy_meal"]["name"].keys()), state="readonly")
        self.healthy_combo.grid(row=0, column=1)
        self.healthy_frame.grid_remove()

        self.special_frame = ttk.Frame(self)
        self.special_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Label(self.special_frame, text="Select Meat:").grid(row=0, column=0, sticky="e")
        self.meat_choice = tk.StringVar()
        self.meat_combo = ttk.Combobox(self.special_frame, textvariable=self.meat_choice, values=list(self.menu["todays_special"]["meats"].keys()), state="readonly")
        self.meat_combo.grid(row=0, column=1)

        ttk.Label(self.special_frame, text="Select Side Combo:").grid(row=1, column=0, sticky="e")
        self.side_choice = tk.StringVar()
        self.side_combo = ttk.Combobox(self.special_frame, textvariable=self.side_choice, values=self.menu["todays_special"]["sides"], state="readonly")
        self.side_combo.grid(row=1, column=1)
        self.special_frame.grid_remove()

        # Extra Notes section
        ttk.Label(self, text="Notes (e.g. extra meat):").grid(row=5, column=0, sticky="e")
        self.notes_entry = ttk.Entry(self, width=40)
        self.notes_entry.grid(row=5, column=1)

        ttk.Label(self, text="Extra Cost ($):").grid(row=6, column=0, sticky="e")
        self.extra_price_entry = ttk.Entry(self, width=10)
        self.extra_price_entry.insert(0, "0")
        self.extra_price_entry.grid(row=6, column=1, sticky="w")


        self.order_button = ttk.Button(self, text="Add Order", command=self.add_order)
        self.order_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.summary_button = ttk.Button(self, text="View Summary", command=self.view_summary)
        self.summary_button.grid(row=8, column=0, columnspan=2)

        self.reset_button = ttk.Button(self, text="Reset Menu & Orders", command=self.reset_all)
        self.reset_button.grid(row=9, column=0, columnspan=2, pady=10)

    def update_meal_options(self, event):
        meal = self.meal_type.get()
        if meal == "Healthy Meal":
            self.healthy_frame.grid()
            self.special_frame.grid_remove()
        else:
            self.healthy_frame.grid_remove()
            self.special_frame.grid()

    def add_order(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        meal_type = self.meal_type.get()

        if not name or not phone or not meal_type:
            messagebox.showerror("Missing Info", "Please fill out all fields.")
            return

        if meal_type == "Healthy Meal":
            healthy_name = self.healthy_choice.get()
            if not healthy_name:
                messagebox.showerror("Missing Info", "Please select a healthy meal option.")
                return
            
            price = self.menu["healthy_meal"]["name"][healthy_name]

            # NOTES (If applicable)
            note = self.notes_entry.get().strip()
            try:
                extra_price = float(self.extra_price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Price", "Please enter a valid number for extra cost.")
                return

            price += extra_price


            order = {
                "name": name,
                "phone": phone,
                "meal_type": meal_type,
                "details": f"{healthy_name}",
                "note": note, 
                "extra_price":extra_price,
                "price": price
            }
        else:
            meat = self.meat_choice.get()
            side = self.side_choice.get()
            if not meat or not side:
                messagebox.showerror("Missing Info", "Please select meat and sides.")
                return
            price = self.menu["todays_special"]["meats"][meat]

            # NOTES (If applicable)
            note = self.notes_entry.get().strip()
            try:
                extra_price = float(self.extra_price_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid Price", "Please enter a valid number for extra cost.")
                return

            price += extra_price

            order = {
                "name": name,
                "phone": phone,
                "meal_type": meal_type,
                "details": f"{meat} with {side}",
                "note": note, 
                "extra_price":extra_price,
                "price": price
            }

        self.orders.append(order)
        save_orders(self.orders)
        messagebox.showinfo("Order Added", f"Order for {name} added. Total: ${order['price']:.2f}")
        self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.meal_type_combo.set('')
        self.healthy_combo.set('')
        self.meat_combo.set('')
        self.side_combo.set('')
        self.notes_entry.delete(0, tk.END)
        self.extra_price_entry.delete(0, tk.END)
        self.extra_price_entry.insert(0, "0")
        self.healthy_frame.grid_remove()
        self.special_frame.grid_remove()

    def view_summary(self):
        summary_win = tk.Toplevel(self)
        summary_win.title("Sales Summary")
        total = 0
        summary_text = ""
        for i, order in enumerate(self.orders, start=1):
            note = f" [Note: {order['note']} (+${order['extra_price']:.2f})]" if order.get("note") else ""
            summary_text += f"{i}. {order['name']} - {order['meal_type']}: {order['details']} (${order['price']:.2f}){note}\n"
            total += order['price']

        text_widget = tk.Text(summary_win, width=60, height=20)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, summary_text)
        text_widget.config(state="disabled")

    def reset_all(self):
        if messagebox.askyesno("Reset Confirmation", "This will clear all orders and the saved menu. Proceed?"):
            if os.path.exists(MENU_FILE):
                os.remove(MENU_FILE)
            if os.path.exists(ORDERS_FILE):
                os.remove(ORDERS_FILE)
            self.orders = []
            self.menu = None
            messagebox.showinfo("Reset", "Menu and orders have been cleared. The app will now close.")
            self.destroy()

if __name__ == "__main__":
    app = TakeoutApp()
    app.mainloop()

# Add stats page for number of plates sold 
#