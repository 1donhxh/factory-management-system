import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES)
from base import BaseWindow

class MaintenanceWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Record Maintenance", size="620x680")

        self.add_button("Record", self.save, primary=True)
        self.add_button("Close", self.destroy)

        self.machine_var = tk.StringVar()
        self.tech_var = tk.StringVar()
        self.type_var = tk.StringVar(value=VALID_MAINT_TYPES[0])
        self.prob_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.complete_var = tk.BooleanVar(value=True)

        self.add_field("Machine:", ttk.Combobox(self.fields, textvariable=self.machine_var,
                                                values=[f"{m['id']} - {m['name']}" for m in machines],
                                                state="readonly", width=28))
        self.add_field("Technician:", ttk.Combobox(self.fields, textvariable=self.tech_var,
                                                   values=[f"{e['id']} - {e['first_name']} {e['last_name']}"
                                                           for e in employees
                                                           if e["role"] == "Maintenance Technician"],
                                                   state="readonly", width=28))
        self.add_field("Maintenance Type:", ttk.Combobox(self.fields, textvariable=self.type_var,
                                                         values=VALID_MAINT_TYPES,
                                                         state="readonly", width=28))
        self.add_field("Problem Description:", ttk.Entry(self.fields, textvariable=self.prob_var, width=30))
        self.add_field("Cost ($):", ttk.Entry(self.fields, textvariable=self.cost_var, width=30))

        ttk.Checkbutton(self.fields, text="Mark maintenance as completed now",
                        variable=self.complete_var).grid(
            row=self._field_row, column=1, sticky="w", pady=6)
        self._field_row += 1

    def save(self):
        try:
            mid = self.machine_var.get().split(" - ")[0]
            eid = self.tech_var.get().split(" - ")[0]
        except IndexError:
            messagebox.showerror("Invalid", "Select a machine and technician.", parent=self)
            return
        machine = find_machine(mid)
        tech = find_employee(eid)
        if not machine or not tech:
            messagebox.showerror("Invalid", "Machine or technician not found.", parent=self)
            return
        prob = self.prob_var.get().strip()
        if not prob:
            messagebox.showerror("Invalid", "Problem description is required.", parent=self)
            return
        try:
            cost = float(self.cost_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Cost must be a number.", parent=self)
            return
        if cost < 0:
            messagebox.showerror("Invalid", "Cost cannot be negative.", parent=self)
            return
        counters["maintenance"] += 1
        mtid = generate_id("MT", counters["maintenance"], 4)
        maintenance_records.append({"id": mtid, "machine_id": mid, "technician_id": eid,
                                    "type": self.type_var.get(), "problem": prob, "cost": cost,
                                    "date": now_str(), "hours_at_service": machine["hours_operated"],
                                    "status": "Completed" if self.complete_var.get() else "In Progress"})
        machine["status"] = "Available" if self.complete_var.get() else "Maintenance"
        messagebox.showinfo("Recorded",
                            f"Maintenance {mtid} recorded.\nMachine status: {machine['status']}",
                            parent=self)
        self.destroy()


