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

opened_count = 0
total_products_found = 0
unique_product_urls = set()

while True:
    # Wait for products to load on current page.
    time.sleep(5)
    product_links = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.products li.product a")
    ))
    # Extract the href attributes of the product links.
    product_urls = [link.get_attribute('href') for link in product_links]

    # Accumulate the total number of products encountered.
    total_products_found += len(product_urls)

    # Save the main window handle.
    main_window = driver.current_window_handle
    unique_product_urls.update(product_urls)
    
    total_products_found += len(product_urls)
    # Visit each product page in a new tab.
    for url in product_urls:
        opened_count += 1
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)
        # Here you could add BeautifulSoup scraping code using driver.page_source
        driver.close()
        driver.switch_to.window(main_window)
        # Optional: wait until the products reappear.
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.products li.product a")
        ))

    # Click the next page button.
    try:
        # Remove cookie notice if it exists.
        try:
            cookie_notice = driver.find_element(By.CSS_SELECTOR, ".cookie-notice-container")
            driver.execute_script("arguments[0].remove();", cookie_notice)
        except Exception:
            pass

        next_button = driver.find_element(
            By.XPATH, "//button[contains(@class, 'page-link-btn') and normalize-space(text())='>']"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.products li.product a")
        ))
    except Exception as e:
        print("No more pages or error:", e)
        break

print(f"Opened {opened_count} product pages out of {total_products_found} products found.")
print(f"Unique products found: {len(unique_product_urls)}")
driver.quit()