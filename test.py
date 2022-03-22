from selenium import webdriver
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys

def test(username, password):
    # init geckodriver
    opt = webdriver.FirefoxOptions()
    opt.add_argument('--headless') # don't show browser's window
    driver = webdriver.Firefox(options=opt)

    # fetch login page
    driver.get("https://en.elvenar.com/")

    # fill username and password
    driver.find_element_by_id('login_userid').send_keys(username)
    driver.find_element_by_id('login_password').send_keys(password)
    driver.find_element_by_id('login_Login').click() # click "login" button

    # wait for page Jump
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.worlds:nth-child(2) > .button')))

    # select server and enter game
    # driver.find_element_by_css_selector('.worlds:nth-child(2) > .button').click()

    # wait for page Jump
    # WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.ID, 'openfl-content')))

    # print cookies
    cookies = driver.get_cookies()

    for cookie in cookies:
        print(json.dumps(cookie))

    # quit
    driver.quit()


# usage:
# python test.py username password
if __name__ == '__main__':
    test(sys.argv[1], sys.argv[2])