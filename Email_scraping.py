import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

LIST_OF_EMAIL = []
IGNORE_EMAIL_LEFT = [".*career.*", '.*info.*',
                '.*investor.*', '.*corporate.*',
                '.*help.*', '.*contact.*', '.*enquiry.*'
                '.*communications.*', '.*gmail.*', '.*inquiry.*'
                '.*outlook.*', '.*ymail.*', '.*yahoo.*']

options = Options()
options.add_argument("start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

PAGES_TO_CRAWL = 4

def search_email_for_company():
    i=1
    # df = pd.read_csv('data_getemail_public_ge_emailtofinds.csv', engine='python', encoding='ISO-8859-1')
    # for domain in df['doamin'][:5]:
    driver.get('https://www.google.com/search?q='+('ferrovial.com'+' email pattern'))
    while i < PAGES_TO_CRAWL:
        try:
            isValidEmail(driver.page_source)
            click_next = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "pnnext"))).click()
            i+=1
        except NoSuchElementException as err:
            print(f'Error Occured due to {err},No more Pages to crawl !!..')
            break
        except TimeoutException as err:
            print(f'Error Occured due to {err},No more Pages to crawl !!..')
            break
    
def isValidEmail(PAGE_SOURCE):
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    combined_email_left_to_ignore = "(" + ")|(".join(IGNORE_EMAIL_LEFT) + ")"

    for re_match in re.finditer(EMAIL_REGEX, PAGE_SOURCE):
        if not re.match(combined_email_left_to_ignore, re_match.group()):
            # if re.match('.*nuvodia.*', re_match.group()):
            LIST_OF_EMAIL.append(re_match.group())

def getValidEmail():
    for i, email in enumerate(LIST_OF_EMAIL):
        print(f'{i+1} :: email:: {email}')

if __name__ =='__main__':
    search_email_for_company()
    getValidEmail()
    driver.close()