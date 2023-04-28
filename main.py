import tkinter as tk
from datetime import datetime
from decimal import Decimal
import tkinter.font as tkfont
import yfinance as yf
import webbrowser
import os


def close_settings_window(entry):
    entry.master.destroy()


def show_history():
    if os.path.exists("history.log") and os.path.isfile("history.log") and os.stat(
            "history.log").st_size > 0:
        os.system("notepad.exe history.log")
    else:
        print("History file not found")


class CurrencyWidget:
    def __init__(self):
        self.usd_rate_value = Decimal(0)
        self.eur_rate_value = Decimal(0)
        self.root = tk.Tk()
        self.root.title("Döviz Kuru")
        self.root.geometry("220x100")
        self.root.wm_attributes("-topmost", 1)
        self.root.geometry("+{}+0".format(self.root.winfo_screenwidth() - self.root.winfo_reqwidth() - 140))
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.attributes("-alpha", 0.5)
        self.precision = 2
        self.saveHistory = True
        self.interval = 30000
        self.load_settings()
        self.usd_label = tk.Label(self.root, text="1 $ = 00.00 ₺", font=("Arial", 18))
        self.usd_label.bind("<Button-1>", self.open_yahoo_finance_usd)
        self.usd_label.pack()
        self.eur_label = tk.Label(self.root, text="1 € = 00.00 ₺", font=("Arial", 18))
        self.eur_label.bind("<Button-1>", self.open_yahoo_finance_eur)
        self.eur_label.pack()
        font = tkfont.Font(family="Arial", weight="bold")
        self.time_label = tk.Label(self.root, text="00:00:00", font=font, fg="blue", cursor="hand2")
        self.time_label.pack()
        self.load_exchange_rates()
        self.root.bind("<Double-Button-1>", self.quit_app_dc)
        self.time_label.bind("<Button-1>", self.open_yahoo_finance)

        self.right_click_menu = tk.Menu(self.root, tearoff=0)
        self.right_click_menu.add_command(label="Ayarlar", command=self.show_settings_window)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Geçmiş", command=show_history)
        self.right_click_menu.add_separator()
        self.right_click_menu.add_command(label="Çıkış", command=self.quit_app)

        self.root.bind("<Button-3>", self.show_right_click_menu)

        self.root.mainloop()

    def load_exchange_rates(self):
        try:
            currency_pair = "USDTRY=X"
            usd_data = yf.download(currency_pair, period="1d", interval="1m")
            self.usd_rate_value = Decimal(str(usd_data["Close"].iloc[-1]))

            currency_pair = "EURTRY=X"
            eur_data = yf.download(currency_pair, period="1d", interval="1m")
            self.eur_rate_value = Decimal(str(eur_data["Close"].iloc[-1]))

            self.update_labels()

            if self.saveHistory:
                with open("history.log", "a") as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"{timestamp} USD={self.usd_rate_value} EUR={self.eur_rate_value}\n")
        except Exception as e:
            print("Error: ", e)

        self.root.after(self.interval, self.load_exchange_rates)
        print("Rates updated eur: ", self.eur_rate_value, " usd: ", self.usd_rate_value)

    def update_labels(self):
        self.usd_label["text"] = f"1 $ = {self.usd_rate_value:.{self.precision}f} ₺"
        self.eur_label["text"] = f"1 € = {self.eur_rate_value:.{self.precision}f} ₺"
        self.time_label["text"] = "yahoo! : {0}".format(datetime.now().strftime("%H:%M:%S"))

    def open_yahoo_finance(self, event):
        if event.widget == self.time_label and event.x < 50:
            webbrowser.open_new_tab("https://finance.yahoo.com/")

    def open_yahoo_finance_usd(self, event):
        if event.widget == self.usd_label:
            webbrowser.open_new_tab("https://finance.yahoo.com/quote/USDTRY=X/")

    def open_yahoo_finance_eur(self, event):
        if event.widget == self.eur_label:
            webbrowser.open_new_tab("https://finance.yahoo.com/quote/EURTRY=X/")

    def show_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ayarlar")
        settings_window.geometry("220x100")
        settings_window.geometry(
            "+{}+{}".format(int(self.root.winfo_screenwidth() / 2 - 110), int(self.root.winfo_screenheight() / 2 - 50)))

        settings_window.wm_attributes("-topmost", 1)
        settings_window.overrideredirect(True)
        settings_window.resizable(False, False)
        settings_window.attributes("-alpha", 1)

        precision_label = tk.Label(settings_window, text="Basamak Hassasiyeti:")
        precision_label.pack()
        precision_entry = tk.Entry(settings_window)
        precision_entry.insert(tk.END, str(self.precision))
        precision_entry.pack()
        save_button = tk.Button(settings_window, text="Kaydet", command=lambda: self.save_precision(precision_entry))
        save_button.pack()

    def save_precision(self, entry):
        self.precision = int(entry.get())
        self.save_settings()
        self.update_labels()
        close_settings_window(entry)

    def load_settings(self):
        if not os.path.exists("settings.properties"):
            with open("settings.properties", "w") as f:
                f.write("precision=2\nsaveHistory=True\ninterval=30000")
        try:
            with open("settings.properties", "r") as f:
                lines = f.readlines()
                for line in lines:
                    key, value = line.strip().split("=")
                    if key == "precision":
                        self.precision = int(value)
                    if key == "saveHistory":
                        self.saveHistory = bool(value)
                    if key == "interval":
                        self.interval = int(value)
        except Exception as e:
            print("Error loading settings: ", e)

    def save_settings(self):
        try:
            with open("settings.properties", "r") as f:
                contents = f.readlines()

            for index, line in enumerate(contents):
                if line.startswith("precision="):
                    key, value = line.strip().split("=")
                    contents[index] = "precision={}\n".format(self.precision)
                    break

            with open("settings.properties", "w") as f:
                contents = "".join(contents)
                f.write(contents)
        except Exception as e:
            print("Error updating settings: ", e)

    def show_right_click_menu(self, event):
        self.right_click_menu.post(event.x_root, event.y_root)

    def quit_app(self):
        self.root.quit()

    def quit_app_dc(self, event):
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    app = CurrencyWidget()
