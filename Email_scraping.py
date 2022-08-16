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
                '.*outlook.*', '.*ymail.*', '.*yahoo.*',
                '^first@.*', '^last@.*', '^flast@.*', '^lfirst@.*',
                '^l.first@.*', '^f.last@.*', '^last.first@.*', '^first.last@.*',
                '^firstname_lastname@.*', '^lastname_firstname@.*', 
                '^firstname.lastname@.*', '^lastname.firstname@.*']

PATTERNS_TO_SEARCH = ['company email pattern example', 'email patterns',
                    'employee email pattern format', 'employee email pattern', 
                    'employee email', 'company employee email pattern format',
                    'employee email in linkedin', 'get email pattern of employee in linkedin']

PAGES_TO_CRAWL = 4

def get_company_domain():
    df = pd.read_csv('data_getemail_public_ge_emailtofinds.csv', engine='python', encoding='ISO-8859-1')
    company_domains, sample_emails= df['doamin'], df['email']
    return company_domains, sample_emails

def search_email_for_company():
    company_domains, sample_emails  = get_company_domain()
    for company_domain in company_domains[:1]:
        for search_pattern in PATTERNS_TO_SEARCH:
            page_no=1
            driver.implicitly_wait(7)
            driver.get('https://www.google.com/search?q='+(company_domain +' '+ search_pattern))
            driver.implicitly_wait(7)
            while page_no < PAGES_TO_CRAWL:
                try:
                    isValidEmail(driver.page_source, company_domain, sample_emails)
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "pnnext"))).click()
                    page_no+=1 
                except NoSuchElementException as err:
                    print(f'Error Occured due to {err},No more Pages to crawl !!..')
                    break
                except TimeoutException as err:
                    print(f'Error Occured due to {err},No more Pages to crawl !!..')
                    break

def isValidEmail(PAGE_SOURCE, company_domain, sample_emails):
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    combined_email_left_to_ignore = "(" + ")|(".join(IGNORE_EMAIL_LEFT) + ")"
    for re_match in re.finditer(EMAIL_REGEX, PAGE_SOURCE):
        email = re_match.group()
        print('\t\nVerifying email:: ', email)

        if re.match(combined_email_left_to_ignore, email):
            continue
        if not re.match(f'.*@{company_domain}.*', email):
            continue
        if re.match(f'._*@{company_domain}.*', email):
            LIST_OF_EMAIL.append(email)
        LIST_OF_EMAIL.append(email)
            # LIST_OF_EMAIL[company_domain].append([email])

def getValidEmail():
    print('\t\n Email After Verfication')
    for i, email in enumerate(LIST_OF_EMAIL):
        print(f'\t\n {i+1}:: Verified email:: {email}')

if __name__ =='__main__':
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
    options.add_experimental_option("prefs", {"profile.block_third_party_cookies": True})
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    search_email_for_company()
    getValidEmail()
    driver.close()
