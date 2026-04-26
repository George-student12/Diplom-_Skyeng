import pytest
from selenium import webdriver
import os
from dotenv import load_dotenv


load_dotenv()
BASE_URL = os.getenv("BASE_URL")
AUTHORIZATION = os.getenv("AUTHORIZATION")
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {AUTHORIZATION}'
  }

@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.maximize_window()
    yield driver
    driver.quit()