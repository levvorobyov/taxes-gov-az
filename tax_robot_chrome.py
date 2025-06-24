# -*- coding: utf-8 -*-
# Файл: tax_robot_chrome.py (Финальная версия с цифровым меню)

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
import chromedriver_autoinstaller

def parse_invoice_details(driver):
    """
    Эта функция парсит данные с открытой страницы детального просмотра накладной.
    """
    print("\n" + "="*20)
    print("Начинаю парсинг данных накладной...")
    
    invoice_data = {
        "invoice_number": "Не найдено", "supplier": "Не найдено",
        "creation_date": "Не найдено", "total_amount": "Не найдено",
        "vat_amount": "Не найдено", "products": []
    }
    
    try:
        main_info_block = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'main-info-block')]"))
        )
        print("Информация о накладной загружена, приступаю к сбору данных...")

        try:
            header_element = main_info_block.find_element(By.XPATH, ".//h3")
            invoice_data["invoice_number"] = header_element.text.replace("Elektron qaimə-faktura ", "").strip()
            print(f"  - Номер накладной: {invoice_data['invoice_number']}")
        except NoSuchElementException:
            print("  - Не удалось найти номер накладной.")

        try:
            supplier_element = driver.find_element(By.XPATH, "//div[text()=\"Qaiməni təqdim edənin VÖEN-i/Adı\"]/following-sibling::div")
            invoice_data["supplier"] = supplier_element.text
            print(f"  - Поставщик: {invoice_data['supplier']}")
        except NoSuchElementException:
            print("  - Не удалось найти поставщика.")
        
        try:
            date_element = driver.find_element(By.XPATH, "//div[text()='Qaimənin yaranma tarixi']/following-sibling::div")
            invoice_data["creation_date"] = date_element.text
            print(f"  - Дата создания: {invoice_data['creation_date']}")
        except NoSuchElementException:
            print("  - Не удалось найти дату создания.")

        try:
            total_amount_element = driver.find_element(By.XPATH, "//h4[contains(., 'CƏMİ:')]")
            invoice_data["total_amount"] = total_amount_element.text.replace("CƏMİ:", "").strip()
            print(f"  - Итоговая сумма: {invoice_data['total_amount']}")
        except NoSuchElementException:
            print("  - Не удалось найти итоговую сумму.")
            
        try:
            vat_amount_element = driver.find_element(By.XPATH, "//h4[contains(., 'O cümlədən ƏDV:')]")
            invoice_data["vat_amount"] = vat_amount_element.text.replace("O cümlədən ƏDV:", "").strip()
            print(f"  - Сумма НДС: {invoice_data['vat_amount']}")
        except NoSuchElementException:
            print("  - Не удалось найти сумму НДС.")

        print("  - Парсинг товаров в таблице...")
        try:
            product_rows = driver.find_elements(By.XPATH, "//table[contains(@class, 'invoice-table-view')]//tbody/tr[contains(@class, 'table-content')]")
            for row in product_rows:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) >= 18:
                    product = {
                        "name": columns[1].text, "quantity": columns[5].text,
                        "unit_price": columns[6].text, "final_amount": columns[17].text
                    }
                    invoice_data["products"].append(product)
                    print(f"    * {product['name']}, Кол-во: {product['quantity']}, Сумма: {product['final_amount']}")
            if not product_rows:
                 print("    - Таблица с товарами пуста или не найдена.")
        except Exception as e:
            print(f"    - Ошибка при парсинге таблицы с товарами: {e}")
        
    except TimeoutException:
        print("!!! Страница с деталями накладной не загрузилась за 15 секунд.")
    except Exception as e:
        print(f"!!! Произошла непредвиденная ошибка при парсинге: {e}")
        
    print("Завершил парсинг накладной.")
    print("="*20 + "\n")
    return invoice_data

def display_menu():
    """Отображает меню команд для пользователя."""
    print("\n--------- МЕНЮ КОМАНД РОБОТА ---------")
    print("1. Спарсить все накладные с ТЕКУЩЕЙ страницы")
    print("2. Сохранить ТЕКУЩУЮ страницу в файл (save_html)")
    print("0. Выход из программы")
    print("------------------------------------")

# --- 1. НАСТРОЙКА И ЗАПУСК БРАУЗЕРА CHROME ---
chromedriver_autoinstaller.install()
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
print("Информация: Запускаю новый экземпляр браузера Google Chrome...")
try:
    driver = webdriver.Chrome(options=options)
except WebDriverException as e:
    print(f"!!! КРИТИЧЕСКАЯ ОШИБКА: Не удалось запустить WebDriver. {e}")
    input("Нажмите Enter для выхода...")
    exit()

# --- 2. ПЕРЕХОД НА САЙТ И АВТОВВОД ДАННЫХ ---
url = "https://new.e-taxes.gov.az/eportal/login/asan"
try:
    print(f"Информация: Открываю страницу: {url}")
    driver.get(url)
    print("Информация: Жду появления полей для ввода...")
    user_id_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "userId")))
    user_id_input.clear()
    user_id_input.send_keys("071176")
    print("✓ ID пользователя '071176' введен.")
    time.sleep(0.5)
    phone_input = driver.find_element(By.ID, "phone")
    phone_input.clear()
    phone_input.send_keys("773483937")
    print("✓ Мобильный номер '773483937' введен.")
except Exception as e:
    print(f"!!! ОШИБКА: Произошла ошибка при загрузке или вводе данных: {e}")
    driver.quit()
    exit()

print("-" * 50)
print(">>> Робот ввел данные. Пожалуйста, в окне браузера нажмите кнопку 'Daxil ol'.")
print(">>> Затем подтвердите вход на вашем мобильном телефоне.")
input(">>> После успешного входа в личный кабинет, вернитесь сюда и нажмите Enter...")
print("-" * 50)
print("✓ Отлично! Робот готов к работе.")

# --- 3. ОСНОВНОЙ ЦИКЛ ПРИЕМА КОМАНД ---
all_parsed_data = []
while True:
    display_menu() # Показываем меню
    choice = input("Выберите номер команды: ").strip()
    
    if choice == '0':
        break

    # ================== КОМАНДА 1: ПАРСИНГ НАКЛАДНЫХ ==================
    elif choice == '1':
        print("\nНачинаю процедуру парсинга всех накладных со страницы...")
        try:
            invoice_links = []
            link_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/eportal/invoice/view/')]")
            for link in link_elements:
                invoice_links.append(link.get_attribute('href'))
            
            print(f"Найдено {len(invoice_links)} накладных для обработки.")
            if not invoice_links:
                print("Не найдено ссылок на накладные. Убедитесь, что вы на странице со списком.")
                continue

            for i, link_url in enumerate(invoice_links):
                print(f"\n--- Обработка накладной {i+1}/{len(invoice_links)} ---")
                print(f"Перехожу по ссылке: {link_url}")
                driver.get(link_url)
                
                print("Пауза 3 секунды для надежной загрузки страницы...")
                time.sleep(3)
                
                parsed_data = parse_invoice_details(driver)
                all_parsed_data.append(parsed_data)
                
                print("Пауза 2 секунды перед следующей накладной...")
                time.sleep(2)
            
            print("\n*** ЗАВЕРШЕН ПАРСИНГ ВСЕХ НАКЛАДНЫХ НА СТРАНИЦЕ ***")

        except Exception as e:
            print(f"!!! Произошла критическая ошибка в процессе парсинга: {e}")
    
    # ================== КОМАНДА 2: СОХРАНИТЬ HTML ==================
    elif choice == '2':
        try:
            html_content = driver.page_source
            file_name = "saved_page.html"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✓ Страница успешно сохранена в файл: {file_name}")
        except Exception as e:
            print(f"!!! ОШИБКА: Не удалось сохранить HTML. {e}")
    
    else:
        print(f"\n!!! Неверный выбор. Пожалуйста, введите номер из меню (1, 2 или 0).")

print("Программа завершена.")
driver.quit()