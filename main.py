from data import load_data, save_data
from base import FactoryApp

if __name__ == "__main__":
    load_data()
    app = FactoryApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (save_data(), app.destroy()))
    app.mainloop()
