import sys
import time
import importlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Імпортуємо модулі
import form_filler
import test_config




def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://login.vd.foodcontrol.gov.ua/")
    
    # Первинна ініціалізація
    filler = form_filler.CertificateFiller(driver)
    actions = test_config.build_actions(filler)

    print("\n" + "="*60)
    print("🚀 БРАУЗЕР ВІДКРИТО!")
    print("1. Увійдіть у систему та відкрийте ПОТРІБНУ ФОРМУ.")
    print("2. Для оновлення обох файлів (form_filler.py ТА test_config.py) введіть: 'r' або 'reload'")
    print("="*60 + "\n")

    while True:
        print("\nДоступні команди ('r' - оновити код і конфіг, 'q' - вийти):")
        print(", ".join(actions.keys()))
        cmd = input("\nВведіть команду: ").strip().lower()

        if cmd == 'q':
            print("Завершення роботи...")
            break

        # 🔄 ПОДВІЙНЕ ГАРАЧЕ ПЕРЕЗАВАНТАЖЕННЯ (Код + Конфіг/Дані)
        if cmd in ['r', 'reload']:
            try:
                importlib.reload(form_filler)   # Перезавантажуємо логіку полів
                importlib.reload(test_config)   # Перезавантажуємо TEST_DATA та build_actions
                
                filler = form_filler.CertificateFiller(driver)
                actions = test_config.build_actions(filler)
                
                print("🔄 [SUCCESS] Модулі form_filler.py та test_config.py успішно оновлено!")
            except Exception as e:
                print(f"❌ Помилка при перезавантаженні: {e}")
            continue

        if cmd in actions:
            filler._safe_step(f"Тест поля [{cmd}]", actions[cmd])
        else:
            print(f"❌ Невідома команда '{cmd}'. Спробуйте ще раз.")

    driver.quit()

if __name__ == "__main__":
    main()
