import calendar
import math
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from api.driver_setup import driver

SEARCH_URL = r'http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1'

class PravoInterface:
    def __init__(self, gov_body:str, date_type:str, date:str='', date_from='', date_to='', doc_number='', key_word='', filename='') -> None:
        """
        date_type: 'Период', 'Точно'
        """
        
        self.url = r'http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1'
        self.gov_body = gov_body[:-1]
        self.date_type = date_type
        self.date = date
        
        self.date_from = self._date_parser(date_from)
        self.date_to = self._date_parser(date_to)
        
        self.doc_number = doc_number
        self.key_word = key_word    
        self.filename = filename

        self.timeout = 0.4 

    def _date_parser(self, date:str)->dict[str, str]:
        year, month = date.split('.')[-1], date.split('.')[-2]
        month = month.replace('0','') 
        return {'year':year, 'month':month}

    def paste_data(self):

        driver.get(SEARCH_URL)
        
        who_box = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "a6label")))
        who_box.click()
        who_box.send_keys(self.gov_body)
        apearing_hint = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME, "yui-ac-highlight"))) 
        apearing_hint.click() 

        time.sleep(self.timeout)
        
        if self.doc_number: 
            doc_number_type = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "a8type")))
            select_type = Select(doc_number_type)
            select_type.select_by_visible_text('Точно')

            doc_number = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "a8")))
            doc_number.click()
            doc_number.send_keys(self.doc_number)


        time.sleep(self.timeout)
        if self.date_type == 'Период':
            select_date = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "a7type")))
            select_date = Select(select_date)
            select_date.select_by_visible_text('Период')

            driver.find_element(by=By.ID, value='img_a7_from').click() 

            # set from date
            from_year = driver.find_element(by=By.ID, value='a7dropdown_calendar1year_choice') 
            Select(from_year).select_by_value(self.date_from['year'])

            from_month = driver.find_element(by=By.ID, value='a7dropdown_calendar1month_choice') 
            Select(from_month).select_by_value(str(int(self.date_from['month'])-1))
            
            from_calendar = driver.find_element(by=By.ID, value='a7dropdown_calendar1calendar_days') 
            calendar_rows = from_calendar.find_elements(by=By.TAG_NAME, value='tr')[:2]
            
            calendar_days = sum([row.find_elements(by=By.TAG_NAME, value='span') for row in calendar_rows], [])
            first_day_button = [e for e in calendar_days if e.text == '1'][0] 
            first_day_button.click()
                

            # set to date
            driver.find_element(by=By.ID, value='img_a7_to').click() 
            # select_date = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "a7type")))


            # to_year = driver.find_element(by=By.ID, value='a7dropdown_calendar2year_choice') 
            select_to_year = WebDriverWait(driver, 3.5).until(EC.element_to_be_clickable((By.ID, "a7dropdown_calendar2year_choice")))
            Select(select_to_year).select_by_value(self.date_to['year'])

            to_month = driver.find_element(by=By.ID, value='a7dropdown_calendar2month_choice') 
            Select(to_month).select_by_value(str(int(self.date_to['month'])-1))

            to_calendar = driver.find_element(by=By.ID, value='a7dropdown_calendar2calendar_days') 
            calendar_rows = to_calendar.find_elements(by=By.TAG_NAME, value='tr')[-2:]
            
            calendar_days = sum([row.find_elements(by=By.TAG_NAME, value='span') for row in calendar_rows], [])

            month_last_day = str(calendar.monthrange(int(self.date_from['year']), int(self.date_from['month']))[-1]) 

            last_day_button = [e for e in calendar_days if e.text == month_last_day][0] 
            last_day_button.click()
            time.sleep(self.timeout)


        if self.key_word:
            key_word_field = driver.find_element_by_css_selector('textarea[name="a0"]')
            key_word_field.click()
            key_word_field.send_keys(self.key_word)
            time.sleep(self.timeout)


        go_butt_path = '//*[@id="searchfields"]/tbody/tr[16]/td[2]/input[1]'
        go_butt = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, go_butt_path)))
        go_butt.click()
    
    @staticmethod
    def _paginate_pages_of_docs(url:str, offset):
        """ листаем список документов """
        if not offset:
            url = re.sub(string=url, pattern='start=\d{1,3}', repl=f'start=0')
            url += '&lstsize=100'
        else:
            url = re.sub(string=url, pattern='start=\d{1,9}', repl=f'start={offset}')
        
        return url

    def get_pages_to_parse(self) ->list[str]:
        """составляем ссылки на страницы с документами (имитация пагинации)"""
        time.sleep(3)
        driver.switch_to.frame('topmenu') 

        # ссылка шаблон с заполненным query, куда можно подставлять offset
        pagination_el = driver.find_elements(by=By.CLASS_NAME, value='pager')[-1] 

        # рабочая ссылка на одну из страниц с пагинацией  
        pagination_link = pagination_el.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
        
        total_docs_path = '//*[@id="search_results_format"]/table/tbody/tr/td[1]/span/span'
        total_docs = driver.find_element(by=By.XPATH, value=total_docs_path).text
        total_docs = int(total_docs)

        def roundup(x): return int(math.ceil(x / 100.0)) 
        n_iterations = roundup(total_docs)  
        
        links_to_parse = []
        offset = 0 
        for _ in range(0, n_iterations):
            pagination_link = self._paginate_pages_of_docs(pagination_link, offset=offset)        
            links_to_parse.append(pagination_link)
            offset+=100 
            
        return links_to_parse

    def get_page_docs(self, page_path:str)->list[str]:        
        """вытащить все ссылки на документы со страницы"""

        driver.get(page_path)
        frame_selector = 'td.list'
        WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, frame_selector)))
        
        driver.switch_to.frame('list') 
        docs = driver.find_elements(by=By.CLASS_NAME, value='l_pics')

        docs_hrefs = [e.find_element_by_tag_name('a').get_attribute('href') for e in docs]
        docs_hrefs = ['&'.join(href.split('/')[-1].split("&")[1:-1]) for href in docs_hrefs]
        
        all_docs_links = []
        for href in docs_hrefs:
            all_docs_links.append(f'http://pravo.gov.ru/proxy/ips/?savertf=&{href}&page=all')
        
        return all_docs_links


    def get_docs(self)-> list[str]:
        self.paste_data()
        pages_to_parse = self.get_pages_to_parse()
        docs_links = []
        for page in pages_to_parse:
            docs_links.append(self.get_page_docs(page))
    
        if self.filename:
            docs_links = [item for sublist in docs_links for item in sublist]
            with open(self.filename, 'w') as f:
                f.write('\n'.join(docs_links))
                print(f'Сохранено {len(docs_links)} ссылок на документы')                
        return docs_links


