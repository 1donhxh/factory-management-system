import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES,
    VALID_ROLES, VALID_SHIFTS)
from base import BaseWindow

class AddEmployeeWindow(BaseWindow):
    def __init__(self, parent):
        super().__init__(parent, "Add Operator / Technician", size="600x660")

        self.add_button("Add Employee", self.save, primary=True)
        self.add_button("Close", self.destroy)

        self.first_var = tk.StringVar()
        self.last_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.role_var = tk.StringVar(value=VALID_ROLES[0])
        self.spec_var = tk.StringVar()
        self.shift_var = tk.StringVar(value=VALID_SHIFTS[0])

        self.add_field("First Name:", ttk.Entry(self.fields, textvariable=self.first_var, width=30))
        self.add_field("Last Name:", ttk.Entry(self.fields, textvariable=self.last_var, width=30))
        self.add_field("Contact Number:", ttk.Entry(self.fields, textvariable=self.contact_var, width=30))
        self.add_field("Role:", ttk.Combobox(self.fields, textvariable=self.role_var,
                                             values=VALID_ROLES, state="readonly", width=28))
        self.add_field("Specialization:", ttk.Entry(self.fields, textvariable=self.spec_var, width=30))
        self.add_field("Shift:", ttk.Combobox(self.fields, textvariable=self.shift_var,
                                              values=VALID_SHIFTS, state="readonly", width=28))

    def save(self):
        first = self.first_var.get().strip()
        last = self.last_var.get().strip()
        contact = self.contact_var.get().strip()
        spec = self.spec_var.get().strip()
        if not all([first, last, contact, spec]):
            messagebox.showerror("Invalid Input", "All fields are required.", parent=self)
            return
        counters["employee"] += 1
        eid = generate_id("E", counters["employee"], 4)
        employees.append({"id": eid, "first_name": first, "last_name": last,
                          "contact": contact, "role": self.role_var.get(),
                          "specialization": spec, "shift": self.shift_var.get()})
        messagebox.showinfo("Success", f"Employee {eid} added.", parent=self)
        self.destroy()


