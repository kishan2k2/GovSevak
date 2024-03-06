#Visiting the website
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
path = "chromedriver.exe"
service = Service(path = path)
driver = webdriver.Chrome(service=service)
driver.get("https://www.india.gov.in/my-government/schemes")
WebDriverWait(driver, 40).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "field-content"))
)
next_page = driver.find_element(By.CLASS_NAME, "pager-next")
while(next_page):
    time.sleep(2)
    to_extract = driver.find_elements(By.CLASS_NAME, 'field-content')
    for i in range(5):
        element = to_extract[i]
        scheme_name = element.text
        link = element.find_element(By.XPATH, "./a").get_attribute('href')
        print(scheme_name)
        print(link)
    next_page = driver.find_element(By.CLASS_NAME, "pager-next")
    next_page.click()
# click_to_view.click()
time.sleep(10)
driver.quit()