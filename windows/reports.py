import tkinter as tk
from tkinter import ttk, messagebox
from data import (machines, products, employees, production_orders,
    maintenance_records, counters, generate_id, now_str, find_machine,
    find_product, find_employee, VALID_STATUSES, VALID_MAINT_TYPES)
from base import BaseWindow

class ReportsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reports")
        self.geometry("1000x640")
        self.minsize(820, 520)
        self.transient(parent)

        top = ttk.Frame(self, padding=10)
        top.pack(side="bottom", fill="x")
        ttk.Button(top, text="Close", command=self.destroy).pack(side="right")

        tabs = ttk.Notebook(self)
        tabs.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.add_tree_tab(tabs, "Machines",
                          ("ID", "Name", "Type", "Capacity/hr", "Hours", "Status"),
                          self.machine_rows())
        self.add_tree_tab(tabs, "Production",
                          ("Order", "Product", "Machine", "Operator", "Qty",
                           "Good", "Defective", "Defect %", "Cost"),
                          self.production_rows())
        self.add_tree_tab(tabs, "Products",
                          ("ID", "Name", "Time(min)", "Material $", "Selling $", "Profit $"),
                          self.product_rows())
        self.add_tree_tab(tabs, "Machine Status", ("Status", "Count"), self.status_rows())
        self.add_tree_tab(tabs, "Maintenance",
                          ("ID", "Machine", "Technician", "Type", "Date", "Cost", "Status"),
                          self.maint_rows())
        self.add_tree_tab(tabs, "Employees",
                          ("ID", "Name", "Role", "Specialization", "Shift"),
                          self.employee_rows())

    def add_tree_tab(self, notebook, title, columns, rows):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for c in columns:
            tree.heading(c, text=c)
            tree.column(c, anchor="w", width=120, stretch=True)
        for r in rows:
            tree.insert("", "end", values=r)
        tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=sb.set)

    def machine_rows(self):
        return [(m["id"], m["name"], m["type"], m["capacity"],
                 f"{m['hours_operated']:.1f}", m["status"]) for m in machines]

    def production_rows(self):
        rows = []
        for o in production_orders:
            total = o["good_qty"] + o["defective_qty"]
            rate = (o["defective_qty"] / total * 100) if total else 0
            rows.append((o["id"], o["product_id"], o["machine_id"], o["operator_id"],
                         o["quantity"], o["good_qty"], o["defective_qty"],
                         f"{rate:.2f}", f"${o['estimated_cost']:,.2f}"))
        return rows

    def product_rows(self):
        return [(p["id"], p["name"], p["production_time"],
                 f"${p['material_cost']:,.2f}", f"${p['selling_price']:,.2f}",
                 f"${p['selling_price'] - p['material_cost']:,.2f}") for p in products]

    def status_rows(self):
        counts = {s: 0 for s in VALID_STATUSES}
        for m in machines:
            counts[m["status"]] = counts.get(m["status"], 0) + 1
        return [(s, counts[s]) for s in VALID_STATUSES]

    def maint_rows(self):
        return [(r["id"], r["machine_id"], r["technician_id"], r["type"],
                 r["date"], f"${r['cost']:,.2f}", r["status"]) for r in maintenance_records]

    def employee_rows(self):
        return [(e["id"], f"{e['first_name']} {e['last_name']}", e["role"],
                 e["specialization"], e["shift"]) for e in employees]


