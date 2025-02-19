from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import re

def get_element_text(selector):
    """Extracts text from an element using CSS selector."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.text.strip()
    except NoSuchElementException:
        return None

def get_element_attribute(selector, attribute):
    """Extracts a specific attribute from an element using CSS selector."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.get_attribute(attribute)
    except NoSuchElementException:
        return None

def get_product_price():
    """Extracts the correct product price, prioritizing the current price in <ins>."""
    try:
        # Try to get the discounted price inside <ins> first
        price_element = driver.find_element(By.CSS_SELECTOR, "ins .woocommerce-Price-amount bdi")
    except NoSuchElementException:
        try:
            # If no <ins> tag exists, get the regular price
            price_element = driver.find_element(By.CSS_SELECTOR, ".price .woocommerce-Price-amount bdi")
        except NoSuchElementException:
            return None  # No price available

    currency_symbol = driver.find_element(By.CSS_SELECTOR, ".woocommerce-Price-currencySymbol").text
    price_value = price_element.text.replace(currency_symbol, "").strip()
    
    return f"{currency_symbol}{price_value}"

# Define a list of known brands
known_brands = [
    "Coca-Cola", "Sprite", "Fanta", "Schweppes", "OOHA", "Bonaqua", "Aquarius",
    "Authentic Tea House", "Kochakaden", "Hi-C", "Minute Maid", "HealthWorks",
    "Monster", "Nescafe", "Nestea"
]

# Create a regex pattern to match any of the known brands
brand_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(brand) for brand in known_brands) + r')\b', re.IGNORECASE)

# ---- Setup WebDriver ----
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.swirecocacolahk.com/all-items/')
wait = WebDriverWait(driver, 10)  # Increased timeout

opened_count = 0
total_products_found = 0
unique_product_urls = set()

while True:
    # Wait for products to load on the current page.
    time.sleep(5)
    product_links = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "ul.products li.product a")
    ))
    # Check for notification pop-up and click "Cancel" if present
    try:
        cancel_button = driver.find_element(By.CSS_SELECTOR, ".notification-popup__button-cancel")
        if cancel_button.is_displayed() and cancel_button.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView(true);", cancel_button)
            cancel_button.click()
            time.sleep(1)  # Wait for the pop-up to close
    except NoSuchElementException:
        pass  # No pop-up found, continue
    # Extract href attributes from product links.
    product_urls = [link.get_attribute('href') for link in product_links]
    unique_product_urls.update(product_urls)
    total_products_found += len(product_urls)

    main_window = driver.current_window_handle

    # Filter out URLs that contain 'add-to-cart'
    product_urls = [url for url in product_urls if 'add-to-cart' not in url]

    # Visit each product page in a new tab.
    for url in product_urls:
        opened_count += 1
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(3)

        # Check for notification pop-up and click "Cancel" if present
        try:
            cancel_button = driver.find_element(By.CSS_SELECTOR, ".notification-popup__button-cancel")
            if cancel_button.is_displayed() and cancel_button.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView(true);", cancel_button)
                cancel_button.click()
                time.sleep(1)  # Wait for the pop-up to close
        except NoSuchElementException:
            pass  # No pop-up found, continue

        # ---- Extract product details ----
        product_name = get_element_text("h1.product_title.entry-title.elementor-heading-title.elementor-size-default")
        
        # Extract unit and package from the product name (if available)
        if product_name:
            # Matches digits with optional decimals followed by whitespace and then 'ml', 'l', 'oz', or 'pcs'
            unit_match = re.search(r'\b(\d+(?:\.\d+)?\s*(?:ml|l|oz|pcs))\b', product_name, flags=re.IGNORECASE)
            product_unit = unit_match.group(1) if unit_match else None

            package_match = re.search(r'\b(\d+\s*(?:P|pcs))\b', product_name, flags=re.IGNORECASE)
            product_package = package_match.group(1) if package_match else None

            # Extract brand from the product name using regex
            brand_match = brand_pattern.search(product_name)
            product_brand = brand_match.group(0) if brand_match else None

            # Handle edge case for "Qoo" or "qoo"
            if re.search(r'\bQoo\b', product_name, flags=re.IGNORECASE):
                product_brand = "Minute Maid"
        else:
            product_unit = None
            product_package = None
            product_brand = None

        product_code = driver.current_url.split('/')[-2]  # Extract from URL
        product_category = get_element_text(".product-category")
        product_sku = get_element_text("span.sku")
        product_description = get_element_text(".woocommerce-product-details__short-description")
        product_photo_url = get_element_attribute(".woocommerce-product-gallery__image img", "src")
        product_price = get_product_price()  # Extract price

        # Store extracted details in a dictionary
        product_details = {
            "Product Name": product_name,
            "Product Code": product_code,
            "Product Unit": product_unit,
            "Product Package": product_package,
            "Product Brand": product_brand,
            "Product Category": product_category,
            "Product SKU": product_sku,
            "Product Description": product_description,
            "Product Photo URL": product_photo_url,
            "Product Price": product_price if product_price else 'Not Available'
        }
        try:
            cancel_button = driver.find_element(By.CSS_SELECTOR, ".notification-popup__button-cancel")
            if cancel_button.is_displayed() and cancel_button.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView(true);", cancel_button)
                cancel_button.click()
                time.sleep(1)  # Wait for the pop-up to close
        except NoSuchElementException:
            pass  # No pop-up found, continue
        # ---- Change language to Chinese and extract product name again ----
        try:
            language_button = driver.find_element(By.CSS_SELECTOR, "li.wpml-ls-item-zh-hant")
            driver.execute_script("arguments[0].scrollIntoView(true);", language_button)
            language_button.click()
            time.sleep(3)  # Wait for the page to reload
            product_name_chinese = get_element_text("h1.product_title.entry-title.elementor-heading-title.elementor-size-default")
            product_details["Product Name (Chinese)"] = product_name_chinese
            if re.search(r'\bQoo\b', product_name, flags=re.IGNORECASE):
                product_brand = "Minute Maid"
            elif re.search(r'\bAqueous\b', product_name, flags=re.IGNORECASE):
                product_brand = "Bonaqua"
        except (NoSuchElementException, ElementNotInteractableException):
            print("Language change button not found or not interactable")
            product_details["Product Name (Chinese)"] = None

        # Print all details together
        print("\n" + "="*40)
        print(f"Product URL: {url}")
        for key, value in product_details.items():
            print(f"{key}: {value}")
        print("="*40 + "\n")

        driver.close()
        driver.switch_to.window(main_window)

        # Optional: wait until products reappear before continuing.
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.products li.product a")
        ))

    # Click the next page button.
    try:
        # Remove cookie notice if present.
        try:
            cookie_notice = driver.find_element(By.CSS_SELECTOR, ".cookie-notice-container")
            driver.execute_script("arguments[0].remove();", cookie_notice)
        except NoSuchElementException:
            pass

        next_button = driver.find_element(
            By.XPATH, "//button[contains(@class, 'page-link-btn') and normalize-space(text())='>']"
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)

        # Wait for the new page to load.
        wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "ul.products li.product a")
        ))
    except Exception as e:
        print("No more pages or error:", e)
        break

print(f"Opened {opened_count} product pages out of {total_products_found} products found.")
print(f"Unique products found: {len(unique_product_urls)}")
driver.quit()