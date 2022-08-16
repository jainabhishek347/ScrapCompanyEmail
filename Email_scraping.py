import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

IGNORE_EMAIL_LEFT = [".*career.*", '.*info.*',
                '.*investor.*', '.*corporate.*',
                '.*help.*', '.*contact.*', '.*enquiry.*'
                '.*communications.*', '.*gmail.*', '.*inquiry.*'
                '.*outlook.*', '.*ymail.*', '.*yahoo.*',
                '^first@.*', '^last@.*', '^flast@.*', '^lfirst@.*',
                '^l.first@.*', '^f.last@.*', '^last.first@.*', '^first.last@.*',
                '^firstname_lastname@.*', '^lastname_firstname@.*', 
                '^firstname.lastname@.*', '^lastname.firstname@.*', '^xx.*', '^xxx.*',
                '^xyz.*', '^abc.*', '.*xx.*']

PATTERNS_TO_SEARCH = ['company email pattern example', 'email patterns',
                    'employee email pattern format', 'employee email pattern', 
                    'employee email', 'company employee email pattern format',
                    'employee email in linkedin', 'get email pattern of employee in linkedin']

PAGES_TO_CRAWL = 4
DOMAIIN_EMAIL_MAP = {}


def match_with_sample_email(email, sample_email):
    email_left, sample_email_left = email.split('@')[0], sample_email.split('@')[0]
    
    if '_' in sample_email_left and '_' not in email_left:
        return False
    
    if '.' in sample_email_left and '.' not in email_left:
        return False
    return True

def find_domain_email():
    df = pd.read_csv('data_getemail_public_ge_emailtofinds.csv', engine='python', encoding='ISO-8859-1')
    domain_with_sample_email = zip(df['doamin'].tolist(), df['email'].tolist())
    try:
        for domain, sample_email in list(domain_with_sample_email)[:10]:
            for search_pattern in PATTERNS_TO_SEARCH:
                page_no = 1
                driver.delete_all_cookies()
                driver.implicitly_wait(10)
                time.sleep(4)
                driver.get('https://www.google.com/search?q='+(domain +' '+ search_pattern))
                time.sleep(5)
                driver.implicitly_wait(10)
                while page_no < PAGES_TO_CRAWL:
                    try:
                        email = extract_email(driver.page_source, domain, sample_email)
                        if email:
                            print(f"making entry for {domain}:{email}")
                            DOMAIIN_EMAIL_MAP[domain] = email
                            break
                        WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.ID, "pnnext"))).click()
                    except NoSuchElementException as err:
                        print(f'Error Occured due to {err},No more Pages to crawl !!..')
                        break
                    except TimeoutException as err:
                        print(f'Error Occured due to {err},No more Pages to crawl !!..')
                        break
                    page_no += 1
            
    except Exception as err:
        print(f'Error Ocurred due to {err}!!..')

def extract_email(PAGE_SOURCE, domain, sample_email):
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    combined_email_left_to_ignore = "(" + ")|(".join(IGNORE_EMAIL_LEFT) + ")"
    for re_match in re.finditer(EMAIL_REGEX, PAGE_SOURCE):
        email = re_match.group()
        print('\t\nverifying email:: ', email)

        # skip if email is it ignored list
        if re.match(combined_email_left_to_ignore, email):
            continue

        # skip if email would not have correct domian
        if not re.match(f'.*@{domain}.*', email):
            continue
   
        # skip if email would not match sample-email
        if not match_with_sample_email(email, sample_email):
            continue

        # skip email left is less then 3 character
        if len(email.split("@")[0]) < 3:
            continue
        return email
    return None

if __name__ =='__main__':
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
    options.add_experimental_option("prefs", {"profile.block_third_party_cookies": True})
    s = Service(r'chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=options)
    driver.delete_all_cookies()
    find_domain_email()
    print(DOMAIIN_EMAIL_MAP)
    driver.close()

