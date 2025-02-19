from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.swirecocacolahk.com/all-items/')

wait = WebDriverWait(driver, 5)
page_num = 1

while True:
    print(f"On page {page_num}")
    time.sleep(5)  # wait for the page to load
    
    # Remove cookie notice if it exists.
    try:
        cookie_notice = driver.find_element(By.CSS_SELECTOR, ".cookie-notice-container")
        driver.execute_script("arguments[0].remove();", cookie_notice)
    except Exception:
        pass

    try:
        next_button = driver.find_element(By.XPATH, "//button[contains(@class, 'page-link-btn') and normalize-space(text())='>']")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.products li.product a")))
        page_num += 1
    except Exception as e:
        print("No more pages or error:", e)
        break

driver.quit()