import json, os
from datetime import datetime

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
