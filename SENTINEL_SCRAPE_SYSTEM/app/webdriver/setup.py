from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_chrome_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Configurações adicionais podem ser adicionadas aqui
    driver = webdriver.Chrome(options=options)
    return driver
