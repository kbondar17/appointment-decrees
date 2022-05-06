import time
from random import choice

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


from fake_useragent import UserAgent

agent = UserAgent().google
 
chrome_options = Options()
chrome_options.add_argument(f"user-agent={agent}")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

window_sizes = ['1280,800', '1650,900', '2100,1115', '1330,650'], 
chrome_options.add_argument(f"window-size={choice(window_sizes)}")

search_url = r'http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1'
test_url = r'http://pravo.gov.ru/'  
# chrome_path = r"C:\Users\ironb\прогр\program_files\chromedriver\chromedriver.exe"
chrome_path = r"C:\Users\ironb\прогр\program_files\chromedriver_copy\chromedriver.exe"
driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

class PravoInterface:
    def __init__(self, gov_body:str, date_type:str, date:str='', date_from='', date_to='', doc_number='') -> None:
        self.url = r'http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1'
        self.gov_body = gov_body
        self.date_type = date_type
        self.date = date
        self.date_from = date_from
        self.date_to = date_to
        self.doc_number = doc_number

        self.timeout = 0.4


    def paste_data(self):

        driver.get(search_url )

        who_box = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "a6label")))
        who_box.click()
        who_box.send_keys(self.gov_body)
        apearing_hint = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CLASS_NAME, "yui-ac-highlight"))) 
        apearing_hint.click() 

        time.sleep(self.timeout)
        if self.doc_number: 
            doc_number = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "a8")))
            doc_number.click()
            doc_number.send_keys(self.doc_number)


        time.sleep(self.timeout)
        if self.date_type == 'Период':
            select_date = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "a7type")))
            select_date = Select(select_date)
            select_date.select_by_visible_text('Период')

            from_date = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, "a7from")))
            from_date.click()
            from_date.send_keys(self.date_from)

            time.sleep(self.timeout)

            to_date = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.NAME, "a7to")))
            to_date.click()
            to_date.send_keys(self.date_to)

            time.sleep(self.timeout)

        go_butt_path = '//*[@id="searchfields"]/tbody/tr[16]/td[2]/input[1]'
        go_butt = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, go_butt_path)))
        go_butt.click()


def get_links():        

    download_path = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=cd00000&a3=&a3type=1&a3value=&a6=102000070&a6type=1&a6value=%CF%F0%E5%E7%E8%E4%E5%ED%F2&a15=&a15type=1&a15value=&a7type=4&a7from=11.01.2021&a7to=&a7date=&a8=&a8type=1&a1=&a0=&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=102006375&a23type=1&a23value=%CD%C0%C7%CD%C0%D7%C5%CD%C8%C5&textpres=&sort=7&x=62&y=15'
    driver.get(download_path)
    time.sleep(3)

    driver.switch_to.frame('topmenu') 
    driver.switch_to.frame('list') 
    docs = driver.find_elements(by=By.CLASS_NAME, value='l_pics')

    docs_hrefs = [e.find_element_by_tag_name('a').get_attribute('href') for e in docs]
    docs_hrefs = ['&'.join(href.split('/')[-1].split("&")[1:-1]) for href in docs_hrefs]
    for href in docs_hrefs:
        # print('выуженная ссылка для скачивания', href)
        download_href = f'http://pravo.gov.ru/proxy/ips/?savertf=&{href}&page=all'
        # print('download_href---', download_href)


# переключение между фреймами (тупо)
#docs = driver.find_elements(by=By.CLASS_NAME, value='list_elem odd')
# tables = driver.find_elements(by=By.CSS_SELECTOR, value='table.list_elem')

# # save_butt_path = '//*[@id="xdoc_toolbar"]/td/div/table/tbody/tr/td[1]/nobr/a/img'
# save_butt_path = 'img[alt="Экспорт документа в RTF"]'
# # img src="?pic_rtf.gif" alt="Экспорт списка в RTF"

'''for e in tables:
    e.click()
    print('---кликнули')
    time.sleep(1)
    driver.switch_to.default_content() 
    print('переключились на дефолт')
    time.sleep(1)
    driver.switch_to.frame('contents') 
    print('переклчились на contents')
    time.sleep(1)
    save_butt = driver.find_element(by=By.CSS_SELECTOR, value=save_butt_path)
    save_butt.click()
    print('сохранили!')
    driver.switch_to.default_content() 
    driver.switch_to.frame('topmenu') 
    driver.switch_to.frame('list') 
    time.sleep(0.5)

''' #list_results_4fontsize > table.list_elem.cur

# iframes = driver.find_elements_by_tag_name('iframe')[1]
    # switch to selected iframe
# driver.switch_to.frame(iframe)
# driver.switch_to.frame('contents')
# time.sleep(0.5)

# # doc_list = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "list_elem")))


# docs = driver.find_elements(by=By.CSS_SELECTOR, value='table')
# print('НАЙДЕНО---',len(docs)) 
# print('docs---', docs)   


# apearing_hint = driver.find_element(by=By.CLASS_NAME, value="yui-ac-highlight") 


# for e in 'Правительс': 
#     # breakpoint() 
#     apearing_hint = ''  
#     who_box.send_keys(e)
#     time.sleep(0.5)  
#     try: 
#         apearing_hint = driver.find_element(by=By.CLASS_NAME, value="yui-ac-highlight") 
#         print('НАШЛИ--', apearing_hint)
#         apearing_hint.click()
#         print('Кликнули!! ')
#     except NoSuchElementException:
#         pass  

    # if apearing_hint: 
    #     print('Кликнули в ифе ')
    #     apearing_hint.click()
    #     break 
 
    # apearing_hint = WebDriverWait(driver, 0.2, ignored_exceptions=[TimeoutException]).until(EC.element_to_be_clickable((By.CLASS_NAME, "yui-ac-highlight"))) 
    # apearing_hint.click()
  
# apearing_hint = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CLASS_NAME, "'yui-ac-highlight'"))) 
# apearing_hint.click()

 
 
# ActionChains(driver).move_to_element(who_box)
# who_box = driver.find_element_by_id('a6label')
# number = driver.find_element_by_id('a8')
# number.send_keys('1')

# select_date.se
#ActionChains(driver).move_to_element(menu).click(hidden_submenu).perform()


