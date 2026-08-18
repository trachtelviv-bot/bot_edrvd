import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException






class CertificateFiller:
    def __init__(self, driver, timeout=5):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _safe_step(self, step_name: str, action_func):
        """Виконує крок і якщо виникає помилка — виводить її, не зупиняючи наступні поля"""
        try:
            print(f"[RUNNING] {step_name}...")
            action_func()
            print(f"[SUCCESS] {step_name}")
        except Exception as e:
            print(f"[ERROR] {step_name}: {type(e).__name__} -> {e}")

    def fill_full_form(self, json_payload: dict):
        cert_data = json_payload.get("certificate", {})
        dogs_data = json_payload.get("dogs", [])

        # 1. Заповнення основної секції сертифіката
        self.fill_certificate_section(cert_data)

        # 2. Перехід до секції собак/товару та заповнення таблиці
        self.fill_dogs_section(dogs_data)

        

    def fill_certificate_section(self, cert_data: dict):
        """Заповнення полів із покроковим логуванням"""
        
        # 1. Телефон
        self._safe_step(
            "1. Номер телефону", 
            lambda: self.fill_telephone(cert_data.get("telephone"))
        )

        # 2. Відправник
        self._safe_step(
            "2. Назва відправника", 
            lambda: self.fill_owner_name(cert_data.get("first_name"), cert_data.get("last_name"))
        )

        # 3. Отримувач
        self._safe_step(
            "3. Назва отримувача", 
            lambda: self.fill_recipient_name(cert_data.get("first_name"), cert_data.get("last_name"))
        )

        # 4. Адреса відправника
        self._safe_step(
            "4. Юридична адреса відправника", 
            lambda: self.fill_sender_address(cert_data.get("home_address"))
        )

        # 5. Країна
        self._safe_step(
            "5. Країна походження", 
            lambda: self.fill_sender_country("Україна")
        )

        # 6. Регіон
        self._safe_step(
            "6. Регіон походження", 
            lambda: self.fill_origin_region("Львівська")
        )

        # 7. Місце отримання
        self._safe_step(
            "7. Місце отримання", 
            lambda: self.fill_receipt_place(cert_data.get("address_destination"))
        )

        # 8. Телефон отримувача (telephone_destination або telephone)
        self._safe_step(
            "8. Телефон отримувача",
            lambda: self.fill_recipient_phone(
                cert_data.get("telephone_destination"), 
                cert_data.get("telephone")
            )
        )

        # 9. Індекс отримувача (postcode_destination або нічого)
        self._safe_step(
            "9. Індекс отримувача",
            lambda: self.fill_recipient_zipcode(cert_data.get("postcode_destination"))
        )

        # 10. Перша транзитна країна (мапінг за ключем entry_country)
        self._safe_step(
            "10. Перша транзитна країна",
            lambda: self.fill_first_transit_country(cert_data.get("entry_country"))
        )

        # 11. Вид транспорту (мапінг за ключем means_transport)
        self._safe_step(
            "11. Вид транспорту",
            lambda: self.fill_transport_type(cert_data.get("means_transport"))
        )

        # 12. Номер транспортного засобу (number_transport або '-' якщо порожньо)
        self._safe_step(
            "12. Номер транспортного засобу",
            lambda: self.fill_transport_number(cert_data.get("number_transport"))
        )

        # 13. Країна транзиту (завжди прочерк)
        self._safe_step(
            "13. Країна транзиту",
            lambda: self.fill_transit_country()
        )

        # 14. Пункт пропуску (bip_entry або пропускаємо, якщо порожньо)
        self._safe_step(
            "14. Пункт пропуску",
            lambda: self.fill_border_crossing_point(cert_data.get("bip_entry"))
        )

        # 15. Перехід на наступну сторінку/секцію
        self._safe_step(
            "15. Кнопка Далі",
            lambda: self.click_next_button()
        )

        

    def fill_dogs_section(self, dogs_data: list):
        """2. ГОЛОВНА ФУНКЦІЯ: Оркеструє процес для кожної тварини у циклі"""
        if not dogs_data:
            return

        for idx, animal in enumerate(dogs_data, start=1):
            # Крок A: Відкрити модальне вікно
            self._safe_step(
                f"16.{idx} Натискання кнопки 'Додати' для тварини №{idx}",
                lambda: self.click_add_button()
            )

            # Крок B: Викликаємо точкову функцію для вибору виду тварини
            animal_kind = animal.get("animal_kind") or animal.get("animal_type")
            if animal_kind:
                self._safe_step(
                    f"17.{idx} Вибір виду тварини: {animal_kind}",
                    lambda: self.select_animal_kind(animal_kind)
                )

            # TODO: Тут будуть інші поля Вкладки 1 (Чіп, Кличка)

            # TODO: Перехід на Вкладку 2 (Процедури) та заповнення процедур

            # Крок C: Збереження модального вікна тварини
            # self._safe_step(
            #     f"20.{idx} Збереження модального вікна тварини №{idx}",
            #     lambda: self.click_save_and_close()
            # )






        

    # --- Окремі методи полів ---

    def fill_telephone(self, phone_number: str):
        if not phone_number: return
        css_selector = "div[data-name='sendplace'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(phone_number))

    def fill_owner_name(self, first_name: str, last_name: str):
        """Заповнення поля 'Назва відправника' з виправленим синтаксисом та обходом перекриття"""
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            return

        css_selector = "div[data-name='VetDocumentDeclarationsExporter'] div[data-name='sendertext'] input"
        
        field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

        # 1. Прокручуємо поле до центру екрана
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        time.sleep(0.2)

        # 2. Клікаємо через JS, щоб зняти перекриття іншим елементом
        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(0.1)

        # 3. Реальне очищення та введення тексту з клавіатури (щоб спрацювали всі обробники сторінки)
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(full_name)

        # 4. Тригеруємо події зміни значення та знімаємо фокус
        self.driver.execute_script("""
            var input = arguments[0];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, field)
        
        field.send_keys(Keys.TAB)

    def fill_recipient_name(self, first_name: str, last_name: str):
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name: return
        css_selector = "div[data-name='recipienttext'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(full_name)

    def fill_sender_address(self, address: str):
        if not address: return
        css_selector = "div[data-name='senderaddress'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(address))

    def fill_sender_country(self, country_name: str = "Україна"):
        css_selector = "div[data-name='sendercountry.nameukr'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокрутка та відкриття поля
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        field.click()
        time.sleep(0.3)

        # 2. Очищення та введення тексту
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(country_name)
        
        # Викликаємо подію введення
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
        time.sleep(1.2)  # Даємо час випадаючому списку завантажитися (dd-load)

        # 3. Спроба обрати варіант зі списку підказок (якщо з'явилося меню), інакше — натиснути Enter
        try:
            # Шукаємо активний/перший елемент випадаючого списку
            dropdown_option = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".typeahead-items div, .dropdown-menu div, .airt-style_typeahead .item"))
            )
            dropdown_option.click()
        except Exception:
            # Якщо кастомний список не зловився окремим селектором — обираємо клавішами
            field.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.3)
            field.send_keys(Keys.ENTER)

    def fill_origin_region(self, region_name: str = "Львівська"):
        """Заповнення випадаючого списку 'Регіон походження' з точним вибором значення"""
        css_selector = "div[data-name='vetdocumentcargosorigin.regioncodes.name'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокрутка та активація поля
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(0.3)

        # 2. Повне очищення
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        
        # 3. Введення назви регіону
        field.send_keys(region_name)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
        time.sleep(1.0)  # Чекаємо фільтрації списку під "Львівська"

        # 4. Спроба кликнути елемент списку зі словом "Львівська" або підтвердити Enter
        try:
            # Шукаємо відфільтрований варіант у випадаючому меню
            option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(@class, 'item') or contains(@class, 'option') or contains(@class, 'dropdown')][contains(text(), '{region_name}')]"))
            )
            option.click()
        except Exception:
            # Якщо кастомний пункт не з'явився окремим XPATH — натискаємо Enter по відфільтрованому списку
            field.send_keys(Keys.ENTER)

    def fill_receipt_place(self, address_destination: str):
        if not address_destination: return
        css_selector = "div[data-name='receiptplace'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(address_destination))

    def fill_recipient_phone(self, phone_dest: str, phone_default: str):
        """Заповнення поля 'Телефон отримувача' з перевіркою джерела даних"""
        # Логіка: якщо є telephone_destination — беремо його, інакше telephone
        phone_to_use = phone_dest if phone_dest else phone_default
        if not phone_to_use:
            return

        css_selector = "div[data-name='recipientphone'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(phone_to_use))

    def fill_recipient_zipcode(self, zipcode: str):
        """Заповнення поля 'Індекс отримувача'"""
        if not zipcode:
            return

        css_selector = "div[data-name='recipientzipcode'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        field.click()
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(zipcode))

    def fill_first_transit_country(self, entry_country: str):
        """Заповнення поля 'Перша транзитна країна' за ключем entry_country"""
        # Словник відповідності країн
        country_map = {
            "Poland": "Польща",
            "Hungary": "Угорщина",
            "Slovakia": "Словацька Республіка",
            "Romania": "Румунія"
        }

        target_country = country_map.get(entry_country)
        if not target_country:
            return

        css_selector = "div[data-name='vetdocumentext.firsttransitcountry.nameukr'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокрутка та активація
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(0.3)

        # 2. Очищення та введення значення
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(target_country)
        
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
        time.sleep(1.0)  # Чекаємо фільтрації списку

        # 3. Вибір значення зі списку або Enter
        try:
            option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(@class, 'item') or contains(@class, 'option') or contains(@class, 'dropdown')][contains(text(), '{target_country}')]"))
            )
            option.click()
        except Exception:
            field.send_keys(Keys.ENTER)


    def fill_transport_type(self, means_transport: str):
        """Заповнення поля 'Вид транспорту' за ключем means_transport"""
        # Словник мапінгу транспортних засобів
        transport_map = {
            "By car": "Автомобіль",
            "By bus": "Автомобіль",
            "By train": "Вагон",
            "By aircraft": "Літак",
            "By ship": "Судно",
            "On foot": "Автомобіль"
        }

        target_transport = transport_map.get(means_transport)
        if not target_transport:
            return

        css_selector = "div[data-name='vetdocumentext.transporttype.name'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокрутка та активація
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)
        time.sleep(0.3)

        # 2. Очищення та введення значення
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(target_transport)

        self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", field)
        time.sleep(1.0)  # Чекаємо фільтрації списку

        # 3. Вибір значення зі списку або Enter
        try:
            option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(@class, 'item') or contains(@class, 'option') or contains(@class, 'dropdown')][contains(text(), '{target_transport}')]"))
            )
            option.click()
        except Exception:
            field.send_keys(Keys.ENTER)


    def fill_transport_number(self, transport_num: str):
        """Заповнення поля 'Номер транспортного засобу' (якщо порожньо — вставляємо '-')"""
        # Якщо значення відсутнє або порожній рядок — використовуємо '-'
        val_to_send = str(transport_num).strip() if transport_num and str(transport_num).strip() else "-"

        css_selector = "div[data-name='vetdocumentext.transportnmb'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)
        
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(val_to_send)

        self.driver.execute_script("""
            var input = arguments[0];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, field)

    def fill_transit_country(self):
        """Заповнення поля 'Країна транзиту' значенням '-'"""
        css_selector = "div[data-name='vetdocumentext.transitCountry'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокручуємо та активуємо поле
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)

        # 2. Очищаємо та вставляємо прочерк
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys("-")

        # 3. Викликаємо події оновлення станa для веб-форми
        self.driver.execute_script("""
            var input = arguments[0];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, field)

    def fill_border_crossing_point(self, bip_entry: str):
        """Заповнення поля 'Пункт пропуску товарів через митний кордон'"""
        if not bip_entry or not str(bip_entry).strip():
            return

        css_selector = "div[data-name='vetdocumentext.vetdoccontentinfo'] input"
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокрутка та активація
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
        self.driver.execute_script("arguments[0].click();", field)

        # 2. Очищення та введення тексту
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(str(bip_entry))

        # 3. Викликаємо події для оновлення стану форми
        self.driver.execute_script("""
            var input = arguments[0];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, field)

    def click_next_button(self):
        """Натискання кнопки 'Далі' для переходу на наступний крок"""
        css_selector = "div[data-name='btNext']"
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        # 1. Прокручуємо кнопку у видиму область
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.3)

        # 2. Клікаємо через JS, щоб гарантовано оминати будь-які перекриття
        self.driver.execute_script("arguments[0].click();", button)
        
        # 3. Даємо сторінці час на завантаження наступного блоку
        time.sleep(1.5)


    def click_add_button(self):
        """Натискання кнопки 'Додати' (btgtNew) у сітці/таблиці"""
        css_selector = "div[data-name='btgtNew']"
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.2)
        
        # Клік через JS для обходу можливих прозорих шарів або tooltip-ів
        self.driver.execute_script("arguments[0].click();", button)
        time.sleep(1.0)
        

    def select_animal_kind(self, animal_kind_key: str):
        """Вибір виду тварини через прямі умови if/elif: Enter -> Літера -> Enter -> Tab."""
        if not animal_kind_key:
            return
    
        print(f"  [*] Емуляція вибору вида тварини: {animal_kind_key}...")
    
        try:
            # 1. Знаходимо останній контейнер у модальному вікні
            containers = self.driver.find_elements(
                By.CSS_SELECTOR, "div[data-name='animaltype.name']"
            )
            if not containers:
                print("  [!] Помилка: Контейнер 'animaltype.name' не знайдено.")
                return
    
            modal_container = containers[-1]
            input_field = modal_container.find_element(
                By.CSS_SELECTOR, "input.value"
            )
    
            # 2. Клікаємо в поле для фокусу
            input_field.click()
            time.sleep(0.3)
    
            actions = ActionChains(self.driver)
    
            # =============================================================
            # 1. Dog -> Enter, "с", Enter, Tab
            # =============================================================
            if animal_kind_key == "Dog":
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys("с").pause(0.3)
                actions.send_keys("о").pause(0.3)
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys(Keys.TAB)
    
            # =============================================================
            # 2. Cat -> Enter, "к", Enter, Tab
            # =============================================================
            elif animal_kind_key == "Cat":
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys("к").pause(0.3)
                actions.send_keys("і").pause(0.3)
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys(Keys.TAB)
    
            # =============================================================
            # 3. Ferret -> Enter, "ф", Enter, Tab
            # =============================================================
            elif animal_kind_key == "Ferret":
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys("ф").pause(0.3)
                actions.send_keys("р").pause(0.3)
                actions.send_keys(Keys.ENTER).pause(0.3)
                actions.send_keys(Keys.TAB)
    
            else:
                print(f"  [!] Невідомий тип тварини: {animal_kind_key}")
                return
    
            # 3. Виконуємо послідовність дій
            actions.perform()
    
            time.sleep(0.3)
            print(f"  [+] Успішно обрано '{animal_kind_key}'.")
    
        except Exception as e:
            print(f"  [!] Помилка при виборі вида тварини: {e}")
            

    def fill_animal_chip(self, chip_code: str):
        """Заповнення поля № Чіпу тварини"""
        if not chip_code:
            return
    
        css_selector = "div[data-name='identitynum'] input.value"
        
        # Очікування елемента
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # Клік та фокусування через JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # Очищення
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        
        # Введення
        field.send_keys(str(chip_code))
        
        # Тригер подій зміни для кастомного інпута
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
        """, field)

    def fill_animal_name(self, name: str):
        """
        Заповнює поле 'Кличка тварини' (data-name='name')
        """
        if not name:
            return
    
        css_selector = "div[data-name='name'] input.value"
        
        # 1. Чекаємо появу та клікабельність поля
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручуємо та фокусуємо за допомогою JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення значення
        field.send_keys(str(name))
        
        # 5. Тригер подій input, change та blur для збереження значення в інтерфейсі
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
        
    def fill_animal_sex(self, sex: str):
        """
        Заповнює поле 'Стать' (data-name='sex')
        """
        if not sex:
            return
    
        css_selector = "div[data-name='sex'] input.value"
        
        # 1. Чекаємо появу та клікабельність поля
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручуємо та фокусуємо через JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення значення
        field.send_keys(str(sex))
        
        # 5. Тригер подій для збереження стану кастомного інпута
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_animal_birth_date(self, birth_date: str):
        """
        Заповнює поле 'Дата народження' (data-name='birthday')
        """
        if not birth_date:
            return
    
        css_selector = "div[data-name='birthday'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(birth_date))
        
        # 4. Виклик JS-подій (input, change, blur), щоб календар закрився та зафіксував дату
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_animal_breed(self, breed: str):
        """
        Заповнює поле 'Порода' (data-name='breedname')
        """
        if not breed:
            return
    
        css_selector = "div[data-name='breedname'] input.value"
        
        # 1. Чекаємо появу та клікабельність поля
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручуємо та фокусуємо через JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення значення
        field.send_keys(str(breed))
        
        # 5. Тригер подій для збереження стану в інтерфейсі
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_animal_passport(self, passport_num: str):
        """
        Заповнює поле 'Серія та № номер паспорта тварини' (data-name='passportnumber')
        """
        if not passport_num:
            return
    
        css_selector = "div[data-name='passportnumber'] input.value"
        
        # 1. Очікування та клікабельність
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручуємо та фокусуємо за допомогою JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення значення
        field.send_keys(str(passport_num))
        
        # 5. Тригер подій для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_animal_note(self, color_desc: str):
        """
        Заповнює поле 'Опис тварини' (data-name='note')
        """
        if not color_desc:
            return
    
        css_selector = "div[data-name='note'] input.value"
        
        # 1. Очікування та клікабельність
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручуємо та фокусуємо за допомогою JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення значення
        field.send_keys(str(color_desc))
        
        # 5. Тригер подій для обов'язкового поля (required)
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def click_save_and_close_button(self):
        """
        Натискає кнопку 'Зберегти та закрити' (data-name='btSaveClose')
        """
        css_selector = "div[data-name='btSaveClose']:not(.hidden)"
        
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        
        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)
    
    
    def click_next_button(self):
        """
        Натискає кнопку 'Далі' (data-name='btNext')
        """
        css_selector = "div[data-name='btNext']:not(.hidden)"
        
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        
        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)
        
    def click_finish_button(self):
        """
        Натискає кнопку 'Закрити' (data-name='btFinish')
        """
        css_selector = "div[data-name='btFinish']:not(.hidden)"
        
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        
        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)
            

    def click_add_procedure_button(self, force: bool = True):
        """
        Натискає тулбар-кнопку Додати ('+') для процедур тварини (data-name='btgtNew').
        
        :param force: Якщо True, примусово видаляє клас 'hidden' та робить кнопку клікабельною.
        """
        css_selector = "div[data-name='btgtNew']"
        
        # Чекаємо наявність елемента у DOM (навіть якщо він hidden)
        button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        
        if force:
            # Видаляємо клас hidden та робимо елемент видимим
            self.driver.execute_script("""
                var elem = arguments[0];
                elem.classList.remove('hidden');
                elem.style.display = 'inline-block';
                elem.style.visibility = 'visible';
                elem.style.opacity = '1';
            """, button)
        
        # Прокручуємо та викликаємо клік
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        
        try:
            button.click()
        except Exception:
            # Якщо стандартний клік блокується, викликаємо JS-подію click
            self.driver.execute_script("arguments[0].click();", button)
            

    def fill_action_date(self, action_date: str):
        """
        Заповнює поле 'Дата проведення дії' (data-name='dateaction')
        """
        if not action_date:
            return
    
        css_selector = "div[data-name='dateaction'] input.value"
        
        # 1. Очікування появу та клікабельності
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        
        # 2. Прокручування та фокусування за допомогою JS
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 3. Повне очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 4. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(action_date))
        
        # 5. Тригер подій input, change та blur для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
        

    def select_action_type(self, action_type_text: str = "Вакцинація"):
        """
        Вибирає значення у полі 'Вид дії з твариною' (data-name='animalsactiontype.name')
        шляхом покрокового введення символів та натискання Enter.
        """
        css_selector = "div[data-name='animalsactiontype.name'] input.value"
        
        # 1. Чекаємо появу та фокусуємо поле
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Політеральне введення перших літер (наприклад, 'Вакц')
        search_str = action_type_text[:4] if len(action_type_text) >= 4 else action_type_text
        for char in search_str:
            field.send_keys(char)
            time.sleep(0.1)  # Пауза для відгуку скриптів випадаючого списку
            
        time.sleep(0.3)
        
        # 4. Підтвердження вибору
        field.send_keys(Keys.ENTER)
        
        # 5. Тригер подій для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def select_animal_disease(self, disease_text: str = "Сказ"):
        """
        Вибирає значення у полі 'Хвороба тварини' (data-name='animaldisease.name')
        шляхом введення 'Сказ', Enter та Tab.
        """
        css_selector = "div[data-name='animaldisease.name'] input.value"
        
        # 1. Чекаємо появу та фокусуємо поле
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Політеральне введення літер ("Сказ")
        search_str = disease_text[:4] if len(disease_text) >= 4 else disease_text
        for char in search_str:
            field.send_keys(char)
            time.sleep(0.1)
            
        time.sleep(0.3)
        
        # 4. Підтвердження вибору (ENTER) та перехід (TAB)
        field.send_keys(Keys.ENTER)
        time.sleep(0.1)
        field.send_keys(Keys.TAB)
        
        # 5. Тригер подій для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
        

    def fill_vet_drug(self, vaccine_name: str):
        """
        Заповнює поле 'Вет. препарат' (data-name='vetdrug')
        """
        if not vaccine_name:
            return
    
        css_selector = "div[data-name='vetdrug'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення назви вакцини/препарату
        field.send_keys(str(vaccine_name))
        
        # 4. Тригер подій для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
    
    def fill_batch_number(self, batch_number: str):
        """
        Заповнює поле 'Номер партії' (data-name='drugbatchnumber')
        """
        if not batch_number:
            return
    
        css_selector = "div[data-name='drugbatchnumber'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Повне очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення номера партії
        field.send_keys(str(batch_number))
        
        # 4. Тригер подій для збереження стану
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_valid_from_date(self, valid_from: str):
        """
        Заповнює поле 'Термні дії з' (data-name='drugvalidfrom')
        """
        if not valid_from:
            return
    
        css_selector = "div[data-name='drugvalidfrom'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(valid_from))
        
        # 4. Тригер подій input, change та blur для збереження дати
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
    
    def fill_valid_to_date(self, valid_to: str):
        """
        Заповнює поле 'Термні дії по' (data-name='drugvalidto')
        """
        if not valid_to:
            return
    
        css_selector = "div[data-name='drugvalidto'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(valid_to))
        
        # 4. Тригер подій input, change та blur для збереження дати
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_blood_sample_date(self, sample_date: str):
        """
        Заповнює поле 'Дата взяття проби крові' (data-name='datebloodaction')
        """
        if not sample_date:
            return
    
        css_selector = "div[data-name='datebloodaction'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(sample_date))
        
        # 4. Тригер подій input, change та blur для фіксації значення
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def click_procedure_save_and_close(self):
        """
        Натискає кнопку 'Зберегти та закрити' у модальному вікні процедури (data-name='btSaveClose')
        """
        css_selector = "div[data-name='btSaveClose']:not(.hidden)"
        
        # Отримуємо всі видимі кнопки 'Зберегти та закрити' і беремо останню (з активного вікна)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        buttons = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
        
        visible_buttons = [b for b in buttons if b.is_displayed()]
        if not visible_buttons:
            return
            
        target_button = visible_buttons[-1]
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_button)
        
        try:
            target_button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", target_button)

    def fill_procedure_card(self, data: dict):
        """
        Заповнює всю картку процедури/вакцинації та зберігає її
        """
        # 1. Дата проведення дії
        if data.get("vaccination_date"):
            self.fill_action_date(data.get("vaccination_date"))
            
        # 2. Вид дії з твариною ("Вакцинація")
        self.select_action_type("Вакцинація")
        
        # 3. Хвороба тварини ("Сказ")
        self.select_animal_disease(data.get("disease", "Сказ"))
        
        # 4. Препарат
        if data.get("vaccine_name"):
            self.fill_vet_drug(data.get("vaccine_name"))
            
        # 5. Номер партії
        if data.get("vaccine_batch"):
            self.fill_batch_number(data.get("vaccine_batch"))
            
        # 6. Термін дії з / по
        if data.get("vaccination_date"):
            self.fill_valid_from_date(data.get("vaccination_date"))
        if data.get("valid_vaccination"):
            self.fill_valid_to_date(data.get("valid_vaccination"))
            
        # 7. Дата проби крові
        if data.get("sample_date"):
            self.fill_blood_sample_date(data.get("sample_date"))
            
        # 8. Зберегти процедуру
        self.click_procedure_save_and_close()

    def switch_tab(self, tab_identifier: str):
        """
        Перемикає вкладки форми за data-item або за назвою (текстом) вкладки.
        
        Приклади використання:
          self.switch_tab("1")
          self.switch_tab("vetdocumentanimals.animalsactions")
          self.switch_tab("Загальна інформація")
          self.switch_tab("Проведені дії з твариною")
        """
        # 1. Спроба знайти за data-item
        css_by_item = f"li.tab-item[data-item='{tab_identifier}']"
        tabs = self.driver.find_elements(By.CSS_SELECTOR, css_by_item)
        
        # 2. Якщо за data-item не знайдено, шукаємо за текстом
        if not tabs:
            all_tabs = self.driver.find_elements(By.CSS_SELECTOR, "li.tab-item")
            tabs = [t for t in all_tabs if tab_identifier.strip().lower() in t.text.strip().lower()]
            
        if not tabs:
            raise Exception(f"Вкладку '{tab_identifier}' не знайдено!")
            
        target_tab = tabs[0]
        
        # 3. Прокручування та клік
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_tab)
        
        try:
            target_tab.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", target_tab)
            

    def fill_chip_implant_date(self, chip_date: str):
        """
        Заповнює поле 'Дата імплантації чіпу' (data-name='animalextpets.implantdate')
        """
        if not chip_date:
            return
    
        css_selector = "div[data-name='animalextpets.implantdate'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(chip_date))
        
        # 4. Тригер подій input, change та blur для збереження дати
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
    
    def fill_identification_system(self, id_system: str):
        """
        Заповнює поле 'Вид ідентифікації' (data-name='animalextpets.identitysystem')
        """
        if not id_system:
            return
    
        css_selector = "div[data-name='animalextpets.identitysystem'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення значення (наприклад, "Транспондер" або "Тавро")
        field.send_keys(str(id_system))
        
        # 4. Тригер подій input, change та blur для збереження значення
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
    
    def fill_identity_locality(self, chip_location: str):
        """
        Заповнює поле 'Місце ідентифікації' (data-name='animalextpets.identitylocality')
        """
        if not chip_location:
            return
    
        css_selector = "div[data-name='animalextpets.identitylocality'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення значення (наприклад, "Підхолка", "Шия зліва")
        field.send_keys(str(chip_location))
        
        # 4. Тригер подій input, change та blur для збереження значення
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_issuer_institution(self, veterinarian_name: str):
        """
        Заповнює поле 'Ким виданий документ' (data-name='institution')
        """
        if not veterinarian_name:
            return
    
        css_selector = "div[data-name='institution'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Повне очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення значення (назва установи або ПІБ лікаря)
        field.send_keys(str(veterinarian_name))
        
        # 4. Тригер подій input, change та blur для збереження
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def select_action_type_treatment(self):
        """
        Вибирає 'Лікування' у полі 'Вид дії з твариною' (data-name='animalsactiontype.name')
        """
        css_selector = "div[data-name='animalsactiontype.name'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Побуквене введення "Ліку"
        for char in "Ліку":
            field.send_keys(char)
            time.sleep(0.1)
            
        time.sleep(0.3)
        
        # 4. Підтвердження та перехід
        field.send_keys(Keys.ENTER)
        time.sleep(0.1)
        field.send_keys(Keys.TAB)
        
        # 5. Фіксація подій
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)
    
    def fill_treatment_date(self, treatment_date: str):
        """
        Заповнює поле 'Дата проведення дії' (data-name='dateaction') для процедури лікування
        """
        if not treatment_date:
            return
    
        css_selector = "div[data-name='dateaction'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення дати у форматі DD.MM.YYYY
        field.send_keys(str(treatment_date))
        
        # 4. Тригер подій input, change та blur для збереження дати
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def select_disease_echinococcus(self):
        """
        Вибирає 'Ехінококоз' у полі 'Хвороба тварини' (data-name='animaldisease.name')
        """
        css_selector = "div[data-name='animaldisease.name'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Побуквене введення "Ехіно"
        for char in "Ехінок":
            field.send_keys(char)
            time.sleep(0.1)
            
        time.sleep(0.3)
        
        # 4. Підтвердження вибору та перехід
        field.send_keys(Keys.ENTER)
        time.sleep(0.1)
        field.send_keys(Keys.TAB)
        
        # 5. Тригер подій для фіксації
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_treatment_drug(self, drug_name: str):
        """
        Заповнює поле 'Вет. препарат' (data-name='vetdrug') для процедури лікування
        """
        if not drug_name:
            return
    
        css_selector = "div[data-name='vetdrug'] input.value"
        
        # 1. Очікування та фокусування
        field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].focus();", field)
        field.click()
        
        # 2. Очищення поля
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        self.driver.execute_script("arguments[0].value = '';", field)
        
        # 3. Введення назви препарату
        field.send_keys(str(drug_name))
        
        # 4. Тригер подій input, change та blur для збереження
        self.driver.execute_script("""
            var elem = arguments[0];
            elem.dispatchEvent(new Event('input', { bubbles: true }));
            elem.dispatchEvent(new Event('change', { bubbles: true }));
            elem.dispatchEvent(new Event('blur', { bubbles: true }));
        """, field)

    def fill_treatment_card(self, data: dict):
        """
        Повністю заповнює та зберігає картку процедури 'Лікування' (проти ехінококозу)
        """
        # 1. Дата проведення дії
        if data.get("date_treatment"):
            self.fill_treatment_date(data.get("date_treatment"))
    
        # 2. Вид дії з твариною ("Лікування")
        self.select_action_type_treatment()
    
        # 3. Хвороба тварини ("Ехінококоз")
        self.select_disease_echinococcus()
    
        # 4. Препарат
        if data.get("name_treatment"):
            self.fill_treatment_drug(data.get("name_treatment"))
    
        # 5. Номер партії (якщо вказаний у даних)
        if data.get("batch_treatment"):
            self.fill_batch_number(data.get("batch_treatment"))
    
        # 6. Зберегти та закрити
        self.click_procedure_save_and_close()
        
    


    def configure_certification_attributes(self, exclude_ids: list = None):
        """1. Переходить на вкладку 'Сертифікація'
    
        2. Натискає кнопку 'Додати' (btgtaddManyVetDocPrintAttributes)
        3. Примусово вмикає ВСІ чекбокси.
        4. Точково вимикає лише ті, що зазначені в exclude_ids.
        """
        if exclude_ids is None:
            # Список ID, які необхідно ВИКЛЮЧИТИ (із вашого HTML)
            exclude_ids = ["433", "434", "435", "438", "441", "443"]
        else:
            exclude_ids = [str(eid) for eid in exclude_ids]
    
        # 1. Перехід на вкладку "Сертифікація"
        self.switch_tab("vetcertificatepetseu.vetdocprintattributes")
        time.sleep(0.5)
    
        # 2. Натискання кнопки "Додати"
        btn_add_css = "div[data-name='btgtaddManyVetDocPrintAttributes']"
        btn_add = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, btn_add_css))
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", btn_add
        )
    
        try:
            btn_add.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn_add)
    
        # 3. Очікування завантаження чекбоксів у таблиці
        checkbox_css = "input.printattributes-checkbox"
        self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, checkbox_css))
        )
        time.sleep(0.5)
    
        # 4. Двоетапне встановлення станів через JavaScript
        js_script = """
            var excludeIds = arguments[0];
            var checkboxes = document.querySelectorAll('input.printattributes-checkbox');
            
            checkboxes.forEach(function(cb) {
                var cbId = cb.getAttribute('data-id');
                
                // КРОК 1: Спочатку вмикаємо ВСІ чекбокси
                if (!cb.checked) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                    cb.dispatchEvent(new Event('click', { bubbles: true }));
                }
                
                // КРОК 2: Якщо цей ID у списку виключень — вимикаємо його
                if (excludeIds.includes(cbId)) {
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                    cb.dispatchEvent(new Event('click', { bubbles: true }));
                }
            });
        """
    
        self.driver.execute_script(js_script, exclude_ids)
    
    



