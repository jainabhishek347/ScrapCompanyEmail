import re
import time
import pandas as pd
import traceback
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
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
                '^xyz.*', '^abc.*']

PATTERNS_TO_SEARCH = [
    'company email pattern example', 
    'email patterns',
    'employee email pattern format', 
    'employee email pattern', 
    'employee email', 
    'company employee email pattern format',
    'employee email in linkedin', 
    'get email pattern of employee in linkedin'
]

PAGES_TO_CRAWL = 4
MAX_RECORDS = 5
DOMAIIN_EMAIL_MAP = {}

def match_with_sample_email(email, sample_email):
    email_left, sample_email_left = email.split('@')[0], sample_email.split('@')[0]
    
    if '_' in sample_email_left and '_' not in email_left:
        return False
    
    if '.' in sample_email_left and '.' not in email_left:
        return False

    return True
    
def find_domain_email(csf_file):
    df = pd.read_csv(csv_file, engine='python', encoding='ISO-8859-1')
    if 1 :#try:
        df = df[:MAX_RECORDS]
        df.fillna('', inplace=True)
        for i in range(len(df)):
            domain, sample_email = df.loc[i, "domain"], df.loc[i, "sample_email"]
            email_right = sample_email.split("@")[1]

            print("\n\n")
            print("* "*20)
            print(f"start scraping email for ({i+1}) {domain} ...")
            DOMAIIN_EMAIL_MAP[domain] = None

            for search_pattern in PATTERNS_TO_SEARCH:
                print(f"\ttrying for pattern - [{search_pattern}]")
                time.sleep(5)
                driver.implicitly_wait(10)
                driver.delete_all_cookies()
                driver.get(f'https://www.google.com/search?q='+(domain +' '+ search_pattern))
                driver.implicitly_wait(10)

                page_no = 1
                while page_no < PAGES_TO_CRAWL:
                    print(f"\tcrawling page - [{page_no}]")
                    try:
                        email = extract_email(driver.page_source, domain, sample_email)
                        if email:
                            print(f"\t[ FOUND !! ], making entry for {domain}:{email}")
                            df.at[i,'email_right'], df.at[i,'relevent_email'] = email_right, email
                            break
                        time.sleep(5)
                        WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.ID, "pnnext"))).click()
                    except NoSuchElementException as err:
                        print(f'\tError Occured(NoSuchElement), No more Pages to crawl !!..')
                        break
                    except TimeoutException as err:
                        print(traceback.format_exc())
                        # or
                        print(sys.exc_info()[2])
                        print(f'\tError(Timeout)({err}) Occured, No more Pages to crawl !!..')
                        return df
                    page_no += 1
            
                if DOMAIIN_EMAIL_MAP[domain]:
                    break
                else:
                    print("\tnot found email!")
                    DOMAIIN_EMAIL_MAP[domain] = None


    # except Exception as err:
    #     print(err)
    #     print(f'\tError Ocurred !!..')

    return df

def extract_email(PAGE_SOURCE, domain, sample_email):
    EMAIL_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    combined_email_left_to_ignore = "(" + ")|(".join(IGNORE_EMAIL_LEFT) + ")"
    for re_match in re.finditer(EMAIL_REGEX, PAGE_SOURCE):
        email = re_match.group()

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
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.delete_all_cookies()
    csv_file = 'data_getemail_public.csv'
    result_df = find_domain_email(csv_file)
    print(result_df)
    print("saving result into csv - data_getemail_public_result.csv ")
    result_df.to_csv('data_getemail_public_result.csv')

    driver.close()
