# """парсит ссылки с вручную выбранных страниц"""
# import math
# import re
# import time

# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import Select, WebDriverWait

# from api.driver_setup import driver


# class TempApi:


#     @staticmethod
#     def _paginate_pages_of_docs(url:str, offset):
#         """ листаем список документов """
#         if not offset:
#             url = re.sub(string=url, pattern='start=\d{1,3}', repl=f'start=0')
#             url += '&lstsize=100'
#         else:
#             url = re.sub(string=url, pattern='start=\d{1,9}', repl=f'start={offset}')
        
#         return url

#     def get_pages_to_parse(self) ->list[str]:
#         """составляем ссылки на страницы с документами (имитация пагинации)"""
#         time.sleep(3)
#         driver.switch_to.frame('topmenu') 

#         # ссылка шаблон с заполненным query, куда можно подставлять offset
#         pagination_el = driver.find_elements(by=By.CLASS_NAME, value='pager')[-1] 

#         # рабочая ссылка на одну из страниц с пагинацией  
#         pagination_link = pagination_el.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
        
#         total_docs_path = '//*[@id="search_results_format"]/table/tbody/tr/td[1]/span/span'
#         total_docs = driver.find_element(by=By.XPATH, value=total_docs_path).text
#         total_docs = int(total_docs)

#         def roundup(x): return int(math.ceil(x / 100.0)) 
#         n_iterations = roundup(total_docs)  
        
#         links_to_parse = []
#         offset = 0 
#         for _ in range(0, n_iterations):
#             pagination_link = self._paginate_pages_of_docs(pagination_link, offset=offset)        
#             links_to_parse.append(pagination_link)
#             offset+=100 
            
#         return links_to_parse

#     def get_page_docs(self, page_path:str)->list[str]:        
#         """вытащить все ссылки на документы со страницы"""

#         driver.get(page_path)
#         frame_selector = 'td.list'
#         WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CSS_SELECTOR, frame_selector)))
        
#         driver.switch_to.frame('list') 
#         docs = driver.find_elements(by=By.CLASS_NAME, value='l_pics')

#         docs_hrefs = [e.find_element_by_tag_name('a').get_attribute('href') for e in docs]
#         docs_hrefs = ['&'.join(href.split('/')[-1].split("&")[1:-1]) for href in docs_hrefs]
        
#         all_docs_links = []
#         for href in docs_hrefs:
#             all_docs_links.append(f'http://pravo.gov.ru/proxy/ips/?savertf=&{href}&page=all')
        
#         return all_docs_links

#     def get(self, url, filename)->list[str]:
#         driver.get(url)

#         pages_to_parse = self.get_pages_to_parse()
#         docs_links = []
#         for page in pages_to_parse:
#             docs_links.append(self.get_page_docs(page))
            

#         if filename:
#             docs_links = [item for sublist in docs_links for item in sublist]
#             with open(filename, 'w') as f:
#                 f.write('\n'.join(docs_links))
#                 print(f'Сохранено {len(docs_links)} ссылок на документы')                

# url = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=r015000%2Fv7701%2Fv7702%2Fv9101%2Fv9400&v3=&v3type=1&v3value=&v6=&v6type=1&v6value=&a7type=3&a7from=&a7to=&a7date=01.05.2010&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&v4=&v4type=1&v4value=&textpres=&sort=7&virtual=1&x=59&y=14'
# file = 'downloads/links/mos_oblast.txt'

# parser = TempApi()
# parser.get(url, file)