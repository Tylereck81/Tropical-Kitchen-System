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
        json.dump(orders, f, indent=2)

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
        self.order_list = []
        self.create_widgets()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        entry_width = 30

        ttk.Label(self, text="Customer Name:").grid(row=0, column=0, sticky="e")
        self.name_entry = ttk.Entry(self, width=entry_width)
        self.name_entry.grid(row=0, column=1, sticky="w")

        ttk.Label(self, text="Phone Number:").grid(row=1, column=0, sticky="e")
        self.phone_entry = ttk.Entry(self, width=entry_width)
        self.phone_entry.grid(row=1, column=1, sticky="w")

        ttk.Label(self, text="Meal Type:").grid(row=2, column=0, sticky="e")
        self.meal_type = tk.StringVar()
        self.meal_type_combo = ttk.Combobox(self, textvariable=self.meal_type, values=["Healthy Meal", "Today's Special"], state="readonly", width=entry_width - 2)
        self.meal_type_combo.grid(row=2, column=1, sticky="w")
        self.meal_type_combo.bind("<<ComboboxSelected>>", self.update_meal_options)

        self.healthy_frame = ttk.Frame(self)
        self.healthy_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="w")
        ttk.Label(self.healthy_frame, text="Select Healthy Option:").grid(row=0, column=0, sticky="e")
        self.healthy_choice = tk.StringVar()
        self.healthy_combo = ttk.Combobox(self.healthy_frame, textvariable=self.healthy_choice, values=list(self.menu["healthy_meal"]["name"].keys()), state="readonly", width=entry_width - 2)
        self.healthy_combo.grid(row=0, column=1, sticky="w")
        self.healthy_frame.grid_remove()

        self.special_frame = ttk.Frame(self)
        self.special_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        ttk.Label(self.special_frame, text="Select Meat:").grid(row=0, column=0, sticky="e")
        self.meat_choice = tk.StringVar()
        self.meat_combo = ttk.Combobox(self.special_frame, textvariable=self.meat_choice, values=list(self.menu["todays_special"]["meats"].keys()), state="readonly", width=entry_width - 2)
        self.meat_combo.grid(row=0, column=1, sticky="w")

        ttk.Label(self.special_frame, text="Select Side Combo:").grid(row=1, column=0, sticky="e")
        self.side_choice = tk.StringVar()
        self.side_combo = ttk.Combobox(self.special_frame, textvariable=self.side_choice, values=self.menu["todays_special"]["sides"], state="readonly", width=entry_width - 2)
        self.side_combo.grid(row=1, column=1, sticky="w")
        self.special_frame.grid_remove()

        ttk.Label(self, text="Notes (e.g. extra meat):").grid(row=5, column=0, sticky="e")
        self.notes_entry = ttk.Entry(self, width=entry_width)
        self.notes_entry.grid(row=5, column=1, sticky="w")

        ttk.Label(self, text="Extra Cost ($):").grid(row=6, column=0, sticky="e")
        self.extra_price_entry = ttk.Entry(self, width=10)
        self.extra_price_entry.insert(0, "0")
        self.extra_price_entry.grid(row=6, column=1, sticky="w")

        self.add_item_button = ttk.Button(self, text="Add Meal to Cart", command=self.add_meal)
        self.add_item_button.grid(row=7, column=0, columnspan=2, pady=5)

        ttk.Label(self, text="Cart:").grid(row=8, column=0, sticky="ne")
        cart_frame = ttk.Frame(self)
        cart_frame.grid(row=8, column=1, sticky="w")
        self.cart_listbox = tk.Listbox(cart_frame, width=50, height=8)
        self.cart_listbox.pack(side="left")
        scrollbar = ttk.Scrollbar(cart_frame, orient="vertical", command=self.cart_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.cart_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=9, column=1, sticky="w")
        self.remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected_meal)
        self.remove_button.pack(side="left", padx=5)
        self.order_button = ttk.Button(button_frame, text="Finalize Order", command=self.finalize_order)
        self.order_button.pack(side="left")

        self.summary_button = ttk.Button(self, text="View Summary", command=self.view_summary)
        self.summary_button.grid(row=10, column=0, columnspan=2)

        self.reset_button = ttk.Button(self, text="Reset Menu & Orders", command=self.reset_all)
        self.reset_button.grid(row=11, column=0, columnspan=2, pady=10)

    def update_meal_options(self, event):
        meal = self.meal_type.get()
        if meal == "Healthy Meal":
            self.healthy_frame.grid()
            self.special_frame.grid_remove()
        else:
            self.healthy_frame.grid_remove()
            self.special_frame.grid()

    def add_meal(self):
        meal_type = self.meal_type.get()
        if meal_type == "Healthy Meal":
            healthy_name = self.healthy_choice.get()
            if not healthy_name:
                messagebox.showerror("Missing Info", "Please select a healthy meal option.")
                return
            price = self.menu["healthy_meal"]["name"][healthy_name]
            details = healthy_name
        else:
            meat = self.meat_choice.get()
            side = self.side_choice.get()
            if not meat or not side:
                messagebox.showerror("Missing Info", "Please select meat and sides.")
                return
            price = self.menu["todays_special"]["meats"][meat]
            details = f"{meat} with {side}"

        note = self.notes_entry.get().strip()
        try:
            extra_price = float(self.extra_price_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Price", "Please enter a valid number for extra cost.")
            return

        total_price = price + extra_price

        meal_summary = f"{meal_type}: {details} - ${total_price:.2f}"
        if note:
            meal_summary += f" (Note: {note})"

        self.cart_listbox.insert(tk.END, meal_summary)

        self.order_list.append({
            "meal_type": meal_type,
            "details": details,
            "note": note,
            "extra_price": extra_price,
            "price": total_price
        })

        self.meal_type_combo.set('')
        self.healthy_combo.set('')
        self.meat_combo.set('')
        self.side_combo.set('')
        self.notes_entry.delete(0, tk.END)
        self.extra_price_entry.delete(0, tk.END)
        self.extra_price_entry.insert(0, "0")
        self.healthy_frame.grid_remove()
        self.special_frame.grid_remove()

    def remove_selected_meal(self):
        selected = self.cart_listbox.curselection()
        if selected:
            index = selected[0]
            self.cart_listbox.delete(index)
            del self.order_list[index]

    def finalize_order(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if not name or not phone or not self.order_list:
            messagebox.showerror("Missing Info", "Please fill in name, phone, and at least one meal.")
            return

        order = {
            "name": name,
            "phone": phone,
            "meals": self.order_list,
            "status": "Pending"
        }

        self.orders.append(order)
        save_orders(self.orders)
        messagebox.showinfo("Order Finalized", f"Order for {name} added with {len(self.order_list)} meals.")
        self.order_list.clear()
        self.cart_listbox.delete(0, tk.END)
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
        self.orders = load_orders()  # Reload orders from file
        summary_win = tk.Toplevel(self)
        summary_win.title("Sales Summary")
        total = 0
        summary_text = ""
        count = 1
        for order in self.orders:
            summary_text += f"{count}. {order['name']} ({order['phone']}):\n"
            for meal in order.get("meals", []):
                note = f" [Note: {meal['note']} (+${meal['extra_price']:.2f})]" if meal.get("note") else ""
                summary_text += f"   - {meal['meal_type']}: {meal['details']} (${meal['price']:.2f}){note}\n"
                total += meal['price']
            count += 1
        summary_text += f"\nTotal Sales: ${total:.2f}"

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