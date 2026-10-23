"""
FACTORY AUTOMATION MANAGEMENT SYSTEM — GUI EDITION
SmartTech Manufacturing Ltd.
Contemporary Programming Project
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


# ============================================================
# DATA STORES
# ============================================================
machines = []
products = []
employees = []
production_orders = []
maintenance_records = []

counters = {"machine": 0, "product": 0, "employee": 0, "order": 0, "maintenance": 0}

VALID_USERS = {"admin": "pass123", "manager": "mgr456", "tech": "tech789"}

VALID_STATUSES = ["Available", "In Production", "Maintenance", "Out of Service"]
VALID_ROLES = ["Machine Operator", "Maintenance Technician",
               "Electrical Technician", "Automation Technician", "Production Supervisor"]
VALID_SHIFTS = ["Morning", "Evening", "Night"]
VALID_MAINT_TYPES = ["Preventive", "Corrective", "Electrical", "Mechanical", "Software/Control"]

SAVE_FILE = "fams_data.json"


# ============================================================
# PERSISTENCE
# ============================================================
def save_data():
    data = {
        "machines": machines, "products": products, "employees": employees,
        "production_orders": production_orders, "maintenance_records": maintenance_records,
        "counters": counters,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_data():
    if not os.path.exists(SAVE_FILE):
        return
    with open(SAVE_FILE) as f:
        data = json.load(f)
    machines.extend(data.get("machines", []))
    products.extend(data.get("products", []))
    employees.extend(data.get("employees", []))
    production_orders.extend(data.get("production_orders", []))
    maintenance_records.extend(data.get("maintenance_records", []))
    counters.update(data.get("counters", {}))


# ============================================================
# HELPERS
# ============================================================
def generate_id(prefix, counter, width=3):
    return f"{prefix}{str(counter).zfill(width)}"


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_machine(mid):
    return next((m for m in machines if m["id"].lower() == mid.lower()), None)


def find_product(pid):
    return next((p for p in products if p["id"].lower() == pid.lower()), None)


def find_employee(eid):
    return next((e for e in employees if e["id"].lower() == eid.lower()), None)


# ============================================================
# MAIN WINDOW
# ============================================================
class FactoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Factory Automation Management System")
        self.geometry("1100x680")
        self.minsize(900, 560)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=26)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Menu.TButton", font=("Segoe UI", 11), padding=12)
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.current_frame = None
        self.show_login()

    def swap(self, frame_class, *args):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.container, self, *args)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_login(self):
        self.swap(LoginFrame)

    def show_dashboard(self, username):
        self.swap(DashboardFrame, username)


# ============================================================
# LOGIN
# ============================================================
class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=40)
        self.app = app
        self.attempts = 0
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        card = ttk.Frame(self, padding=30)
        card.grid(row=0, column=0)

        ttk.Label(card, text="Factory Automation Management System",
                  style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 6))
        ttk.Label(card, text="SmartTech Manufacturing Ltd.",
                  style="Sub.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 24))

        ttk.Label(card, text="Username:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.user_var = tk.StringVar()
        self.user_entry = ttk.Entry(card, textvariable=self.user_var, width=28)
        self.user_entry.grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(card, text="Password:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.pass_var = tk.StringVar()
        self.pass_entry = ttk.Entry(card, textvariable=self.pass_var, show="*", width=28)
        self.pass_entry.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        ttk.Button(card, text="Login", command=self.try_login).grid(
            row=4, column=0, columnspan=2, pady=(20, 6), sticky="ew")

        self.status_lbl = ttk.Label(card, text="", foreground="#b00020")
        self.status_lbl.grid(row=5, column=0, columnspan=2)

        self.pass_entry.bind("<Return>", lambda e: self.try_login())
        self.user_entry.focus_set()

    def try_login(self):
        u = self.user_var.get().strip()
        p = self.pass_var.get().strip()
        if not u or not p:
            self.status_lbl.config(text="Username and password cannot be empty.")
            return
        if u in VALID_USERS and VALID_USERS[u] == p:
            self.app.show_dashboard(u)
            return
        self.attempts += 1
        remaining = 3 - self.attempts
        if remaining <= 0:
            messagebox.showerror("Access Denied",
                                 "Maximum login attempts exceeded. The system will now close.")
            self.app.destroy()
            return
        self.status_lbl.config(text=f"Invalid credentials. Attempts remaining: {remaining}")
        self.pass_var.set("")


# ============================================================
# DASHBOARD
# ============================================================
class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app, username):
        super().__init__(parent)
        self.app = app
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ttk.Frame(self, padding=12, relief="ridge")
        sidebar.grid(row=0, column=0, sticky="ns")

        ttk.Label(sidebar, text="FAMS", style="Title.TLabel").pack(pady=(0, 4))
        ttk.Label(sidebar, text=f"User: {username}", style="Sub.TLabel").pack(pady=(0, 14))

        entries = [
            ("Start Production Order", self.open_production),
            ("Add Machine(s)", self.open_add_machine),
            ("Add / Update Product", self.open_products),
            ("Add Operator / Technician", self.open_add_employee),
            ("Update Machine Status", self.open_update_status),
            ("Record Maintenance", self.open_maintenance),
            ("Print Reports", self.open_reports),
        ]
        for text, cmd in entries:
            ttk.Button(sidebar, text=text, style="Menu.TButton",
                       command=cmd, width=26).pack(pady=4)
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=14)
        ttk.Button(sidebar, text="Logout / Exit", style="Menu.TButton",
                   command=self.app.destroy, width=26).pack(pady=4)

        # Content
        self.content = ttk.Frame(self, padding=20)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.show_welcome()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_welcome(self):
        self.clear_content()
        self.content.columnconfigure(0, weight=1)
        self.content.columnconfigure(1, weight=1)

        # Machines
        left = ttk.LabelFrame(self.content, text="Machines", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        tree = ttk.Treeview(left, columns=("ID", "Name", "Status", "Hrs"),
                            show="headings", height=12)
        for c in ("ID", "Name", "Status", "Hrs"):
            tree.heading(c, text=c)
            tree.column(c, width=90, anchor="w")
        for m in machines:
            tree.insert("", "end", values=(m["id"], m["name"], m["status"],
                                           f"{m['hours_operated']:.1f}"))
        tree.grid(row=0, column=0, sticky="nsew")
        ttk.Label(left, text=f"Total machines: {len(machines)}").grid(
            row=1, column=0, pady=(6, 0), sticky="w")

        # Right column
        right = ttk.Frame(self.content)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        prod_box = ttk.LabelFrame(right, text="Products", padding=10)
        prod_box.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        prod_box.rowconfigure(0, weight=1)
        prod_box.columnconfigure(0, weight=1)
        ptree = ttk.Treeview(prod_box, columns=("ID", "Name", "Sell $"),
                             show="headings", height=6)
        for c in ("ID", "Name", "Sell $"):
            ptree.heading(c, text=c)
            ptree.column(c, width=110, anchor="w")
        for p in products:
            ptree.insert("", "end", values=(p["id"], p["name"],
                                            f"${p['selling_price']:,.2f}"))
        ptree.grid(row=0, column=0, sticky="nsew")

        emp_box = ttk.LabelFrame(right, text="Employees", padding=10)
        emp_box.grid(row=1, column=0, sticky="nsew")
        emp_box.rowconfigure(0, weight=1)
        emp_box.columnconfigure(0, weight=1)
        etree = ttk.Treeview(emp_box, columns=("ID", "Name", "Role"),
                             show="headings", height=6)
        for c in ("ID", "Name", "Role"):
            etree.heading(c, text=c)
            etree.column(c, width=110, anchor="w")
        for e in employees:
            etree.insert("", "end", values=(e["id"],
                                            f"{e['first_name']} {e['last_name']}",
                                            e["role"]))
        etree.grid(row=0, column=0, sticky="nsew")

    # Handlers
    def open_production(self):
        ProductionWindow(self); self.show_welcome()

    def open_add_machine(self):
        AddMachineWindow(self); self.show_welcome()

    def open_products(self):
        ProductWindow(self); self.show_welcome()

    def open_add_employee(self):
        AddEmployeeWindow(self); self.show_welcome()

    def open_update_status(self):
        UpdateStatusWindow(self); self.show_welcome()

    def open_maintenance(self):
        MaintenanceWindow(self); self.show_welcome()

    def open_reports(self):
        ReportsWindow(self)


# ============================================================
# BASE POPUP — pack-based layout (title top, buttons bottom, form middle)
# ============================================================
class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title, size="600x700"):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.minsize(520, 400)
        self.transient(parent)                                # Tie to parent
        self.configure(bg="#f0f0f0")

        # ---- BUTTON BAR pinned to bottom (created FIRST) ----
        self.button_bar = ttk.Frame(self, padding=12)
        self.button_bar.pack(side="bottom", fill="x")

        # ---- BODY fills the remaining space ----
        self.body = ttk.Frame(self, padding=20)
        self.body.pack(side="top", fill="both", expand=True)

        # Title
        ttk.Label(self.body, text=title, style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        # Optional subtitle line
        self.subtitle = ttk.Label(self.body, text="", style="Sub.TLabel", foreground="#555")
        self.subtitle.pack(anchor="w", pady=(0, 10))

        # Field container (form area)
        self.fields = ttk.Frame(self.body)
        self.fields.pack(fill="both", expand=True)
        self.fields.columnconfigure(1, weight=1)

        self._field_row = 0                                   # Row counter for fields

        # Center over parent, then make modal (deferred so sizes are known)
        self.after(20, lambda: self._centre_and_grab(parent))

    def _centre_and_grab(self, parent):
        """Center the popup over its parent, then lock interaction (modal)."""
        try:
            self.update_idletasks()                           # Let Tk measure everything
            w = self.winfo_width()
            h = self.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = max(0, px + (pw - w) // 2)
            y = max(0, py + (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
            self.lift()                                       # Bring to front
            self.grab_set()                                   # Make modal
        except tk.TclError:
            pass

    def add_field(self, label, widget):
        """Add a label + input row to the form (auto-incremented row)."""
        ttk.Label(self.fields, text=label).grid(
            row=self._field_row, column=0, sticky="e", padx=6, pady=6)
        widget.grid(row=self._field_row, column=1, sticky="ew", padx=6, pady=6)
        self._field_row += 1
        return widget

    def add_button(self, text, command, primary=False):
        """Add a button to the bottom bar. primary=True gives it action styling."""
        style = "Action.TButton" if primary else "TButton"
        btn = ttk.Button(self.button_bar, text=text, command=command, style=style)
        btn.pack(side="right", padx=4)
        return btn

    def set_subtitle(self, text):
        self.subtitle.config(text=text)


# ============================================================
# ADD MACHINE
# ============================================================
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


# ============================================================
# ADD / UPDATE PRODUCT
# ============================================================
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


# ============================================================
# ADD EMPLOYEE
# ============================================================
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


# ============================================================
# UPDATE MACHINE STATUS
# ============================================================
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


# ============================================================
# START PRODUCTION ORDER
# ============================================================
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


# ============================================================
# RECORD MAINTENANCE
# ============================================================
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


# ============================================================
# REPORTS
# ============================================================
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


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    load_data()
    app = FactoryApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (save_data(), app.destroy()))
    app.mainloop()
