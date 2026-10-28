import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES)
from base import BaseWindow

class ProductWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Add / Update Product", size="620x700")

        self.add_button("Save", self.save, primary=True)
        self.add_button("New / Clear", self.clear_form)
        self.add_button("Close", self.destroy)

        # Selector
        self.set_subtitle("Pick a product to update, or leave 'New' to add:")
        self.selector = ttk.Combobox(self.fields, state="readonly")
        self.selector.grid(row=self._field_row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.selector.bind("<<ComboboxSelected>>", self.load_selected)
        self._field_row += 1

        self.name_var = tk.StringVar()
        self.cat_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.mat_var = tk.StringVar()
        self.price_var = tk.StringVar()

        self.add_field("Product Name:", ttk.Entry(self.fields, textvariable=self.name_var, width=30))
        self.add_field("Category:", ttk.Entry(self.fields, textvariable=self.cat_var, width=30))
        self.add_field("Production Time (min):", ttk.Entry(self.fields, textvariable=self.time_var, width=30))
        self.add_field("Material Cost ($):", ttk.Entry(self.fields, textvariable=self.mat_var, width=30))
        self.add_field("Selling Price ($):", ttk.Entry(self.fields, textvariable=self.price_var, width=30))

        self.refresh_selector()

    def refresh_selector(self):
        items = ["<New Product>"] + [f"{p['id']} - {p['name']}" for p in products]
        self.selector["values"] = items
        self.selector.current(0)

    def load_selected(self, _=None):
        idx = self.selector.current()
        if idx == 0:
            self.clear_form()
            return
        p = products[idx - 1]
        self.name_var.set(p["name"])
        self.cat_var.set(p["category"])
        self.time_var.set(str(p["production_time"]))
        self.mat_var.set(str(p["material_cost"]))
        self.price_var.set(str(p["selling_price"]))
        self._editing_id = p["id"]

    def clear_form(self):
        self._editing_id = None
        self.selector.current(0)
        for v in (self.name_var, self.cat_var, self.time_var, self.mat_var, self.price_var):
            v.set("")

    def save(self):
        name = self.name_var.get().strip()
        cat = self.cat_var.get().strip()
        if not name or not cat:
            messagebox.showerror("Invalid Input", "Name and category are required.", parent=self)
            return
        try:
            t = float(self.time_var.get())
            mat = float(self.mat_var.get())
            price = float(self.price_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Numeric fields must be valid numbers.", parent=self)
            return
        if t <= 0 or mat < 0 or price < 0:
            messagebox.showerror("Invalid Input", "Time must be > 0 and costs non-negative.", parent=self)
            return

        existing = find_product(self._editing_id) if getattr(self, "_editing_id", None) else None
        if existing:
            existing.update(name=name, category=cat, production_time=t,
                            material_cost=mat, selling_price=price)
            messagebox.showinfo("Updated", f"Product {existing['id']} updated.", parent=self)
        else:
            counters["product"] += 1
            pid = generate_id("P", counters["product"], 3)
            products.append({"id": pid, "name": name, "category": cat,
                             "production_time": t, "material_cost": mat, "selling_price": price})
            messagebox.showinfo("Added", f"Product {pid} added.", parent=self)
        self.refresh_selector()
        self.clear_form()


