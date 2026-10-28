import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES)
from base import BaseWindow

class AddMachineWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Add Machine", size="600x620")

        # Buttons (bottom)
        self.add_button("Add Machine", self.save, primary=True)
        self.add_button("Close", self.destroy)

        # Info line
        self.set_subtitle(f"Existing machines: {len(machines)}")

        # Variables
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.cap_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Available")

        # Fields
        self.add_field("Machine Name:", ttk.Entry(self.fields, textvariable=self.name_var, width=30))
        self.add_field("Machine Type:", ttk.Entry(self.fields, textvariable=self.type_var, width=30))
        self.add_field("Capacity (units/hr):", ttk.Entry(self.fields, textvariable=self.cap_var, width=30))
        self.add_field("Operating Cost/hr ($):", ttk.Entry(self.fields, textvariable=self.cost_var, width=30))
        self.add_field("Status:", ttk.Combobox(self.fields, textvariable=self.status_var,
                                               values=VALID_STATUSES, state="readonly", width=28))

    def save(self):
        name = self.name_var.get().strip()
        mtype = self.type_var.get().strip()
        try:
            cap = float(self.cap_var.get())
            cost = float(self.cost_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Capacity and cost must be numbers.", parent=self)
            return
        if not name or not mtype:
            messagebox.showerror("Invalid Input", "Name and type cannot be empty.", parent=self)
            return
        if cap <= 0 or cost < 0:
            messagebox.showerror("Invalid Input", "Capacity must be > 0 and cost non-negative.", parent=self)
            return

        counters["machine"] += 1
        mid = generate_id("M", counters["machine"], 3)
        machines.append({"id": mid, "name": name, "type": mtype, "capacity": cap,
                         "cost_per_hour": cost, "status": self.status_var.get(),
                         "hours_operated": 0.0})
        messagebox.showinfo("Success", f"Machine {mid} added.", parent=self)
        self.destroy()


class UpdateStatusWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Update Machine Status", size="560x480")

        self.add_button("Update", self.save, primary=True)
        self.add_button("Look Up", self.lookup)
        self.add_button("Close", self.destroy)

        self.id_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Available")

        self.add_field("Machine ID:", ttk.Entry(self.fields, textvariable=self.id_var, width=30))
        self.add_field("New Status:", ttk.Combobox(self.fields, textvariable=self.status_var,
                                                   values=VALID_STATUSES, state="readonly", width=28))

        self.info = ttk.Label(self.fields, text="", foreground="#555")
        self.info.grid(row=self._field_row, column=0, columnspan=2, pady=(10, 0), sticky="w")

    def lookup(self):
        m = find_machine(self.id_var.get().strip())
        if not m:
            self.info.config(text="Machine not found.")
            return
        self.info.config(text=f"Current: {m['name']} — Status: {m['status']}")
        self.status_var.set(m["status"])

    def save(self):
        m = find_machine(self.id_var.get().strip())
        if not m:
            messagebox.showerror("Not Found", "Machine ID does not exist.", parent=self)
            return
        m["status"] = self.status_var.get()
        messagebox.showinfo("Updated", f"{m['id']} status set to {m['status']}.", parent=self)


