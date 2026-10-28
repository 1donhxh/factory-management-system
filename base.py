import tkinter as tk
from tkinter import ttk, messagebox

from data import machines, products, employees, VALID_STATUSES, VALID_ROLES, VALID_SHIFTS


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
        from data import VALID_USERS
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


class BaseWindow(tk.Toplevel):
    def __init__(self, parent, title, size="600x700"):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.minsize(520, 400)
        self.transient(parent)
        self.configure(bg="#f0f0f0")

        self.button_bar = ttk.Frame(self, padding=12)
        self.button_bar.pack(side="bottom", fill="x")

        self.body = ttk.Frame(self, padding=20)
        self.body.pack(side="top", fill="both", expand=True)

        ttk.Label(self.body, text=title, style="Title.TLabel").pack(anchor="w", pady=(0, 12))

        self.subtitle = ttk.Label(self.body, text="", style="Sub.TLabel", foreground="#555")
        self.subtitle.pack(anchor="w", pady=(0, 10))

        self.fields = ttk.Frame(self.body)
        self.fields.pack(fill="both", expand=True)
        self.fields.columnconfigure(1, weight=1)

        self._field_row = 0

        self.after(20, lambda: self._centre_and_grab(parent))

    def _centre_and_grab(self, parent):
        try:
            self.update_idletasks()
            w = self.winfo_width()
            h = self.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            x = max(0, px + (pw - w) // 2)
            y = max(0, py + (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
            self.lift()
            self.grab_set()
        except tk.TclError:
            pass

    def add_field(self, label, widget):
        ttk.Label(self.fields, text=label).grid(
            row=self._field_row, column=0, sticky="e", padx=6, pady=6)
        widget.grid(row=self._field_row, column=1, sticky="ew", padx=6, pady=6)
        self._field_row += 1
        return widget

    def add_button(self, text, command, primary=False):
        style = "Action.TButton" if primary else "TButton"
        btn = ttk.Button(self.button_bar, text=text, command=command, style=style)
        btn.pack(side="right", padx=4)
        return btn

    def set_subtitle(self, text):
        self.subtitle.config(text=text)


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app, username):
        super().__init__(parent)
        self.app = app
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

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

    def open_production(self):
        from windows.production import ProductionWindow
        ProductionWindow(self); self.show_welcome()

    def open_add_machine(self):
        from windows.machine import AddMachineWindow
        AddMachineWindow(self); self.show_welcome()

    def open_products(self):
        from windows.product import ProductWindow
        ProductWindow(self); self.show_welcome()

    def open_add_employee(self):
        from windows.employee import AddEmployeeWindow
        AddEmployeeWindow(self); self.show_welcome()

    def open_update_status(self):
        from windows.machine import UpdateStatusWindow
        UpdateStatusWindow(self); self.show_welcome()

    def open_maintenance(self):
        from windows.maintenance import MaintenanceWindow
        MaintenanceWindow(self); self.show_welcome()

    def open_reports(self):
        from windows.reports import ReportsWindow
        ReportsWindow(self)
