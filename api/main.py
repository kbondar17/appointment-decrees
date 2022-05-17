'''
Инкапсуляция. 
'''

import os 
from collections import Counter 
 
from transliterate import translit
from api.temp_api import TempApi    
# from api.converter import MyParser
from api.new_converter import MyParser
from api.utils.my_logger import Log, get_file_logger
from api.utils.json_validation import FileData

from api.data_handler import DataHandler
from api.aio_files_downloader import FilesDownloader

filelogger = get_file_logger(__name__)

class DecreeWorker:

    def __init__(self, entity_name, search_link, unwanted_words, links_file_exists:bool=False, parse_only:bool=False):
        self.data_handler = DataHandler(entity_name=entity_name)
        self.search_link = search_link
        self.links_getter = TempApi()
        self.parser = MyParser(location=entity_name, unwanted_words=unwanted_words, data_hanlder=self.data_handler) 
        self.links_file_exists = links_file_exists
        self.parse_only = parse_only

    def get_links_from_site(self, link)->list[str]:
        links = self.links_getter.get(link)
        filelogger.warning('получили всего ссылок - {}'.format(len(links)))
        return links
        
    def download_files(self, links:list[str])->None:
        downloader = FilesDownloader(result_folder=self.data_handler.raw_files_folder,
                                    files_n_links_file=self.data_handler.files_n_links_file,
                                    links=links, data_hanlder=self.data_handler)
        downloader.go()

    def parse_folder(self, files_folder)->list[FileData]:
        parsing_results = []
        results = []
        for file in os.listdir(files_folder):
            file_path = os.path.join(files_folder, file)
            try:
                parsed_file = self.parser.parse_file(file_path=file_path)
                parsing_results.append(parsed_file)
                results.append('ok')
            except Exception as ex:
                results.append(str(ex))
                # import traceback
                # traceback.print_exc()
                # print('===ОШИБКА===') # TODO: вынести это в декоратор
                # # print(files_folder)
                # print(ex)
                # print('====')
        
        filelogger.warning('Результаты парсинга {}'.format(str(Counter(results))))
        # print('PARSIN RESULTS in MAIN:::',Counter(results))
        return parsing_results        
        
    def go(self):
        if not self.parse_only: 
            # получили и сохранили ссылки       
            if not self.links_file_exists:
                links = self.get_links_from_site(self.search_link)
                self.data_handler.save_links(links)
            else:
                links = self.data_handler.get_pre_downloaded_links()
            # скачали ссылки. папка прописана в ините
            self.download_files(links)

        # парсим файлы
        parsed_data = self.parse_folder(files_folder=self.data_handler.raw_files_folder)
        # сохраняем
        self.data_handler.save_results_pkl(parsed_data)
        self.data_handler.save_results_json(parsed_data)

        # self.data_handler.save_pkl(parsed_data)
        # self.parse_folder(self.data_handler.raw_files_folder)


if __name__ == '__main__':
    # link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=r015700&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.01.2018&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=59&y=5'
    # entity_name = 'орловская область'
    unwanted_words = 'api/unwanted_words.txt'
    # worker = DecreeWorker(entity_name, link, links_file_exists=False, parse_only=False)
    # worker.go()
    import ast
    already_proccessed_regions = os.listdir(r'C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions')
    regs_n_links = open('regions_n_links.txt', 'r').read()
    regs_n_links = ast.literal_eval(regs_n_links)
    i=0
    for region, link in regs_n_links.items():
        if region in already_proccessed_regions:
            continue
        filelogger.warning('PARSING REGION:: {} VIA LINK {}'.format(translit(region, 'ru', reversed=True), link))
        worker = DecreeWorker(entity_name=region, search_link=link, unwanted_words=unwanted_words, 
                              links_file_exists=False, parse_only=False)
        worker.go()
        i+=1
        if i > 5:
            break 


    #TODO: мб files downloader может наследоваться от data handler. было бы логично 
    #TODO: обработка ошибок
    # TODO: склеить имена?
    #TODO добавить: 
    # 1. склонение начальник/директор
    # если в имени два слова - пометить, что неправильное имя и поправить руками.
    # мб через падежи? pymorphy?



