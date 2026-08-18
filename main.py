import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Імпортуємо ваш модуль для заповнення
from form_filler import CertificateFiller

def get_resource_path(relative_path):
    """Отримує абсолютний шлях до ресурсів (працює і для звичайного запуску, і для EXE)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class VetBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VetControl Automation Bot")
        self.root.geometry("450x420")
        self.root.resizable(False, False)

        # Selenium Driver та дані JSON
        self.driver = None
        self.current_json_data = None

        # --- Елементи графічного інтерфейсу ---
        
        # Крок 1: Запуск браузера
        tk.Label(
            root, 
            text="Крок 1: Підготовка сесії", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 2))

        self.btn_open_browser = tk.Button(
            root, 
            text="1. Відкрити FoodControl у Chrome", 
            command=self.start_browser, 
            bg="#2196F3", 
            fg="white", 
            font=("Arial", 9, "bold")
        )
        self.btn_open_browser.pack(fill="x", padx=20, pady=2)

        tk.Label(
            root, 
            text="* Увійдіть у систему вручну та відкрийте потрібну форму", 
            fg="gray", 
            font=("Arial", 8)
        ).pack(anchor="w", padx=20, pady=(0, 10))

        # Крок 2: Завантаження JSON
        tk.Label(
            root, 
            text="Крок 2: Завантаження даних сертифіката", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(5, 2))

        self.btn_load_json = tk.Button(
            root, 
            text="Завантажити JSON сертифіката", 
            command=self.load_from_json,
            font=("Arial", 9)
        )
        self.btn_load_json.pack(fill="x", padx=20, pady=5)

        # Інформаційна мітка про стан завантаженого JSON
        self.lbl_status = tk.Label(
            root, 
            text="Файл не обрано", 
            fg="red", 
            font=("Arial", 9, "italic")
        )
        self.lbl_status.pack(anchor="w", padx=20, pady=2)

        # Крок 3: Виконання автоматизації
        tk.Label(
            root, 
            text="Крок 3: Запуск процесу", 
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 2))

        self.btn_run_bot = tk.Button(
            root, 
            text="2. Виконати автоматизацію", 
            command=self.run_automation, 
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 10, "bold")
        )
        self.btn_run_bot.pack(fill="x", padx=20, pady=5)

        # Обробка закриття вікна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_browser(self):
        """Запускає браузер Chrome один раз і відкриває потрібний сайт."""
        if self.driver is not None:
            messagebox.showinfo("Інформація", "Браузер уже запущено!")
            return

        try:
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")

            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get("https://login.vd.foodcontrol.gov.ua/")
            
            messagebox.showinfo(
                "Браузер відкрито", 
                "Виконайте вхід вручну та перейдіть до створення сертифіката.\n\n"
                "Після цього оберіть JSON та натисніть 'Виконати автоматизацію'."
            )
        except Exception as e:
            messagebox.showerror("Помилка запуску", f"Не вдалося відкрити браузер:\n{e}")

    def load_from_json(self):
        """Зчитує дані з JSON-файлу стандартної структури."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Оберіть JSON файл сертифіката"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.current_json_data = json.load(file)

            # Перевірка базової структури
            cert = self.current_json_data.get("certificate", {})
            dogs = self.current_json_data.get("dogs", [])
            seria = cert.get("seria", "")
            number = cert.get("number", "")

            # Оновлюємо статус на формі
            status_text = f"Завантажено: Серія {seria} №{number} | Тварин: {len(dogs)}"
            self.lbl_status.config(text=status_text, fg="green")

            messagebox.showinfo("Успіх", f"JSON успішно завантажено!\n{status_text}")
        except Exception as e:
            self.current_json_data = None
            self.lbl_status.config(text="Помилка читання JSON", fg="red")
            messagebox.showerror("Помилка", f"Не вдалося прочитати JSON:\n{e}")

    def run_automation(self):
        if self.driver is None or not self.current_json_data:
            messagebox.showwarning("Увага", "Відкрийте браузер та завантажте JSON!")
            return

        try:
            filler = CertificateFiller(self.driver)
            filler.fill_full_form(self.current_json_data)
            messagebox.showinfo("Успіх", "Автоматичне заповнення завершено!")

        except Exception as e:
            # Виводимо назву помилки та її деталі
            error_message = f"Тип помилки: {type(e).__name__}\nДеталі: {str(e)}"
            messagebox.showerror("Помилка автоматизації", error_message)

    def on_closing(self):
        """Коректне закриття браузера при закритті програми."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VetBotApp(root)
    root.mainloop()
