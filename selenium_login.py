import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def login_with_selenium(username, password):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.jokerapp888e.net/GameIndex")
    time.sleep(2)

    user_elem = driver.find_element(By.ID, "Username")
    pass_elem = driver.find_element(By.ID, "Password")
    user_elem.clear()
    user_elem.send_keys(username)
    pass_elem.clear()
    pass_elem.send_keys(password)

    driver.find_element(By.CSS_SELECTOR, "form#form_login input[type=submit]").click()
    time.sleep(3)

    # Get the current URL after submission
    final_url = driver.current_url
    print("Final URL:", final_url)

    # Check if the final URL starts with the specified base URL
    base_url = "https://www.jokerapp888e.net/Agreement?redirectUrl"
    success = final_url.startswith(base_url)

    # Prepare the success object based on the login result
    success_object = {
        "Success": success,
        "Message": "Success" if success else "Username or password is incorrect",
        "Data": None
    }
    
    # Get cookies
    cookies = driver.get_cookies()
    driver.quit()

    return cookies, success_object, final_url
