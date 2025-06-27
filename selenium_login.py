import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_with_selenium(username, password):
    options = Options()
    options.add_argument("--headless")  # Use --headless for compatibility
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    final_url = driver.current_url
    try:
        driver.get("https://www.jokerapp888e.net/GameIndex")

        # Wait for the username field to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form#form_login input[type=submit]"))).click()

        # Wait for the page to load and check the URL
        WebDriverWait(driver, 10).until(EC.url_contains("Agreement"))
        final_url = driver.current_url
        base_url = "https://www.jokerapp888e.net/Agreement?redirectUrl"
        success = final_url.startswith(base_url)

        result = {
            # "Redirect": final_url,
            "Success": success,
            "Message": "Success" if success else "Username or password is incorrect",
            "Data": None
        }
        cookies = driver.get_cookies()

    except Exception as e:
        result = {
            # "Redirect": None,
            "Success": False,
            "Message": "Username or password is incorrect",
            "Data": None
        }
        cookies = None

    finally:
        driver.quit()

    return cookies, result, final_url
