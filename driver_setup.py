import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import random

def setup_driver():
    """
    Selenium WebDriverをセットアップし、ヘッドレスモードでFirefoxブラウザを起動する。
    ユーザーエージェントを設定し、WebDriverを返す。

    Returns:
        driver (WebDriver): 設定されたWebDriverインスタンス
    """
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver

def random_delay(min_delay=4, max_delay=6):
    """
    最小および最大遅延時間の間でランダムな遅延を挿入する。

    Args:
        min_delay (float): 最小遅延時間（秒）
        max_delay (float): 最大遅延時間（秒）
    """
    time.sleep(random.uniform(min_delay, max_delay))

def login_keibabook(driver, login_url, username, password):
    """
    指定されたURLにアクセスし、ユーザー名とパスワードを使用してログインする。

    Args:
        driver (WebDriver): WebDriverインスタンス
        login_url (str): ログインページのURL
        username (str): ログインID
        password (str): ログインパスワード
    """
    driver.get(login_url)
    random_delay()
    driver.find_element(By.NAME, 'login_id').send_keys(username)
    driver.find_element(By.NAME, 'pswd').send_keys(password)
    driver.find_element(By.NAME, 'submitbutton').click()
    random_delay()