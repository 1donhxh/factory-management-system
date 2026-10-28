import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES)
from base import BaseWindow

class ProductionWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Start Production Order", size="620x700")

        if not (products and machines and employees):
            self.set_subtitle("Add at least one product, machine and employee first.")
            self.add_button("Close", self.destroy)
            return

        self.add_button("Start & Complete Order", self.process, primary=True)
        self.add_button("Close", self.destroy)

        self.product_var = tk.StringVar()
        self.machine_var = tk.StringVar()
        self.operator_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.good_var = tk.StringVar()
        self.def_var = tk.StringVar()

        self.add_field("Product:", ttk.Combobox(self.fields, textvariable=self.product_var,
                                                values=[f"{p['id']} - {p['name']}" for p in products],
                                                state="readonly", width=28))
        self.add_field("Machine:", ttk.Combobox(self.fields, textvariable=self.machine_var,
                                                values=[f"{m['id']} - {m['name']} ({m['status']})"
                                                        for m in machines],
                                                state="readonly", width=28))
        self.add_field("Operator:", ttk.Combobox(self.fields, textvariable=self.operator_var,
                                                 values=[f"{e['id']} - {e['first_name']} {e['last_name']}"
                                                         for e in employees],
                                                 state="readonly", width=28))
        self.add_field("Quantity Required:", ttk.Entry(self.fields, textvariable=self.qty_var, width=30))
        self.add_field("Good Units:", ttk.Entry(self.fields, textvariable=self.good_var, width=30))
        self.add_field("Defective Units:", ttk.Entry(self.fields, textvariable=self.def_var, width=30))

    def process(self):
        try:
            pid = self.product_var.get().split(" - ")[0]
            mid = self.machine_var.get().split(" - ")[0]
            eid = self.operator_var.get().split(" - ")[0]
        except IndexError:
            messagebox.showerror("Invalid", "Please select product, machine, and operator.", parent=self)
            return
        product = find_product(pid)
        machine = find_machine(mid)
        operator = find_employee(eid)
        if not (product and machine and operator):
            messagebox.showerror("Invalid", "One of the selections could not be found.", parent=self)
            return
        if machine["status"] != "Available":
            messagebox.showerror("Unavailable",
                                 f"Machine {machine['id']} is currently {machine['status']}.",
                                 parent=self)
            return
        try:
            qty = int(self.qty_var.get())
            good = int(self.good_var.get())
            defective = int(self.def_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Quantity fields must be whole numbers.", parent=self)
            return
        if qty <= 0 or good < 0 or defective < 0 or good + defective > qty:
            messagebox.showerror("Invalid", "Check quantities (must be positive; good+defective <= qty).",
                                 parent=self)
            return
        hours = (product["production_time"] * qty) / 60
        cost = (hours * machine["cost_per_hour"]) + (product["material_cost"] * qty)
        counters["order"] += 1
        oid = generate_id("PO", counters["order"], 4)
        machine["status"] = "Available"
        machine["hours_operated"] += hours
        production_orders.append({"id": oid, "product_id": pid, "machine_id": mid,
                                  "operator_id": eid, "quantity": qty, "good_qty": good,
                                  "defective_qty": defective, "estimated_cost": cost,
                                  "date": now_str()})
        messagebox.showinfo("Order Recorded",
                            f"Order {oid} recorded.\nEstimated Cost: ${cost:,.2f}",
                            parent=self)
        self.destroy()


