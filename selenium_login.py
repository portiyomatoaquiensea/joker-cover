import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def login_with_selenium(username, password):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.jokerapp888e.net/GameIndex")
    time.sleep(2)

    driver.find_element(By.ID, "Username").send_keys(username)
    driver.find_element(By.ID, "Password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "form#form_login input[type=submit]").click()
    time.sleep(3)

    final_url = driver.current_url
    base_url = "https://www.jokerapp888e.net/Agreement?redirectUrl"
    success = final_url.startswith(base_url)

    result = {
        "Success": success,
        "Message": "Success" if success else "Username or password is incorrect",
        "Data": None
    }
    cookies = driver.get_cookies()
    driver.quit()

    return cookies, result, final_url
