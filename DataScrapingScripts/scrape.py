import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
path = 'chromedriver.exe'
service = Service(path = path)
driver = webdriver.Chrome(service=service)
df = pd.read_csv('scheme_data.csv')
content = []
for index, row in df.iterrows():
    link = row['scheme_link']
    title = row['scheme_name']
    driver.get(link)
    print(title)
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'field-content'))
        )
    except:
        continue
    # print('element is present')
    try:
        p = driver.find_element(By.XPATH, "//div[@class='field-content']//p").text
    except:
        p = "$error$"
        print('error occured')
    # print(p)
    content.append(title+ ' = '+ p)
    # print(content[index])
    print(p)
    print('\n')
    time.sleep(3)
    if index%5 == 0:
        print('sleeping long')
        time.sleep(10)
    # time.sleep(10)
new_df = pd.DataFrame({'content':content})
new_df.to_csv('scraped.csv', index=False)
driver.quit()