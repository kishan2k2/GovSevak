#Visiting the website
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import time
path = "chromedriver.exe"
service = Service(path = path)
driver = webdriver.Chrome(service=service)
driver.get("https://www.india.gov.in/my-government/schemes")
WebDriverWait(driver, 40).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "field-content"))
)
next_page = driver.find_element(By.CLASS_NAME, "pager-next")
name_of_scheme = []
link_of_scheme = []
j = 0
while(next_page):
    if j==208:
        df = pd.DataFrame({'scheme_name':name_of_scheme, 'scheme_link':link_of_scheme})
        df.to_csv('scheme_data.csv', index=False)
        break
    time.sleep(5)
    to_extract = driver.find_elements(By.CLASS_NAME, 'field-content')
    for i in range(5):
        element = to_extract[i]
        scheme_name = element.text
        try:
            link = element.find_element(By.XPATH, "./a").get_attribute('href')
        except:
            link = None
        print(scheme_name)
        print(link)
        name_of_scheme.append(scheme_name)
        link_of_scheme.append(link)
    next_page = driver.find_element(By.CLASS_NAME, "pager-next")
    print("currently in page no ", j)
    j += 1
    next_page.click()
# df = pd.DataFrame({'scheme_name':name_of_scheme, 'scheme_link':link_of_scheme})
# df.to_csv('scheme_data.csv', index=False)
# click_to_view.click()
time.sleep(10)
driver.quit()