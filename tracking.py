import tkinter as tk
from tkinter import ttk
import json
import os

ORDERS_FILE = "orders.json"
STATUS_ORDER = ["Pending", "Prepping", "Pick-Up", "Finished"]

class DragCard(ttk.Frame):
    def __init__(self, master, order_id, order, move_callback):
        super().__init__(master, relief="raised", borderwidth=2)
        self.order_id = order_id
        self.order = order
        self.move_callback = move_callback
        self.label = ttk.Label(self, text=f"{order['name']} – {order['details']}")
        self.label.pack(padx=5, pady=5)
        self.bind_events()
        self.start_x = 0
        self.start_y = 0

    def bind_events(self):
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_drop)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<ButtonRelease-1>", self.on_drop)

    def on_click(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.lift()

    def on_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y
        self.place_configure(x=self.winfo_x() + dx, y=self.winfo_y() + dy)

    def on_drop(self, event):
        root = self.winfo_toplevel()
        for status, canvas in root.canvases.items():
            fx = canvas.winfo_rootx()
            fy = canvas.winfo_rooty()
            fw = canvas.winfo_width()
            fh = canvas.winfo_height()
            mx, my = self.winfo_pointerxy()

            if fx <= mx <= fx + fw and fy <= my <= fy + fh:
                self.move_callback(self.order_id, status)
                return

        self.move_callback(self.order_id, self.order.get("status", "Pending"))

class TrackingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Order Tracking – Drag Anywhere")
        self.geometry("1000x500")
        self.frames = {}
        self.cards = {}
        self.orders = {}
        self.canvases = {}
        self.scrollables = {}

        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        for idx, status in enumerate(STATUS_ORDER):
            container = ttk.LabelFrame(self, text=status)
            container.grid(row=0, column=idx, padx=5, pady=10, sticky="n")

            canvas = tk.Canvas(container, width=240, height=450)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            canvas.bind("<Enter>", lambda e, c=canvas: c.bind("<MouseWheel>", lambda ev: c.yview_scroll(int(-1 * (ev.delta / 120)), "units")))
            canvas.bind("<Leave>", lambda e, c=canvas: c.unbind("<MouseWheel>"))

            self.canvases[status] = canvas
            self.frames[status] = scrollable_frame

    def load_orders(self):
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                data = json.load(f) or []
        else:
            data = []
        self.orders = {i: o for i, o in enumerate(data)}
        self.redraw()

    def redraw(self):
        for card in self.cards.values():
            card.destroy()
        self.cards.clear()

        for frame in self.frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

        for i, (oid, order) in enumerate(self.orders.items()):
            status = order.get("status", "Pending")
            frame = self.frames.get(status)
            card = DragCard(self, oid, order, self.move_order)
            card.pack(in_=frame, fill="x", pady=5, padx=5)
            self.cards[oid] = card

    def move_order(self, oid, new_status):
        self.orders[oid]["status"] = new_status
        self.save_orders()
        self.redraw()

    def save_orders(self):
        with open(ORDERS_FILE, "w") as f:
            json.dump(list(self.orders.values()), f, indent=2)

if __name__ == "__main__":
    TrackingApp().mainloop() 