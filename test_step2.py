# test_step2.py
import time
from selenium import webdriver
from form_filler import CertificateFiller

driver = webdriver.Chrome()
driver.get("https://your-system-url.com")

input("Авторизуйтесь та відкрийте потрібну вкладку вручну, після чого натисніть Enter у консолі...")

filler = CertificateFiller(driver)

# Тестуємо лише натискання кнопки "Додати"
filler.click_add_button()

input("Перевірте результат на екрані та натисніть Enter для закриття...")
driver.quit()
