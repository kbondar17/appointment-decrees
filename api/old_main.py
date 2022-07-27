'''
Инкапсуляция. 
'''

import json
import os 
from collections import Counter 
import structlog
log = structlog.get_logger()


from transliterate import translit
from api.temp_api import TempApi    
# from api.converter import MyParser
# from api.converter import MyParser
from api.decree_parser.decree_parser import MyParser

from api.utils.my_logger import Log, get_file_logger
from api.utils.models import FileData

from api.data_handler import DataHandler
from api.downloader.aio_files_downloader import FilesDownloader

filelogger = get_file_logger(__name__)

class DecreeWorker:

    def __init__(self, entity_name, search_link, unwanted_words, links_file_exists:bool=False, parse_only:bool=False, word_to_search:str='назначить'):
        self.data_handler = DataHandler(entity_name=entity_name)
        self.search_link = search_link
        self.links_getter = TempApi()
        self.parser = MyParser(location=entity_name, unwanted_words=unwanted_words, data_hanlder=self.data_handler) 
        self.links_file_exists = links_file_exists
        self.parse_only = parse_only
        self.word_to_search = word_to_search

    def get_links_from_site(self, link)->list[str]:
        links = self.links_getter.get(link)
        self.data_handler.save_just_file_links(links)
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
        rogue_files = []
        for file in os.listdir(files_folder):
            file_path = os.path.join(files_folder, file)
            try:
                parsed_file = self.parser.parse_file(file_path=file_path)
                parsing_results.append(parsed_file)
                results.append('ok')
            except Exception as ex:
                results.append(str(ex))
                rogue_files.append({
                    'err':str(ex),
                    'file':file,
                })

        with open('rogue_files.json', 'w') as f:
            json.dump(rogue_files, f)

        filelogger.warning('Parsing results {}'.format(Counter(results)))
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

        # загрузили файл с ссылками и filenames
        if self.links_file_exists:
            self.data_handler.load_files_n_links()
        
        # парсим файлы
        parsed_data = self.parse_folder(files_folder=self.data_handler.raw_files_folder)
        # сохраняем
        self.data_handler.save_results_pkl(parsed_data)
        self.data_handler.save_results_json(parsed_data)

        # self.data_handler.save_pkl(parsed_data)
        # self.parse_folder(self.data_handler.raw_files_folder)


if __name__ == '__main__':
    unwanted_words = 'api/unwanted_words.txt'
    # already_proccessed_regions = os.listdir(r'C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions')

    # regs_n_links = open('regions_n_links.json', 'r')
    # regs_n_links = json.load(regs_n_links)
    
    # i=0
    # for region, link in regs_n_links.items():
    #     if region in already_proccessed_regions:
    #         continue
    #     filelogger.warning('PARSING REGION:: {} VIA LINK {}'.format(translit(region, 'ru', reversed=True), link))
    #     worker = DecreeWorker(entity_name=region, search_link=link, unwanted_words=unwanted_words, 
    #                           links_file_exists=False, parse_only=False)
    #     worker.go()
    #     i+=1

    link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=cd00000&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.12.2021&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=65&y=8'
    link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=cd00000&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.01.2022&a8=&a8type=1&a1=&a0=%EE%F1%E2%EE%E1%EE%E4%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=31&y=14'
    link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=cd00000&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.04.2022&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=47&y=10'
    link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=r015000&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.01.2020&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=50&y=9'
    link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=cd00000%2Fr015000&v3=&v3type=1&v3value=&v6=&v6type=1&v6value=&a7type=3&a7from=&a7to=&a7date=01.01.2020&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&v4=&v4type=1&v4value=&textpres=&sort=7&virtual=1&x=41&y=14'
    
    # region = 'московская область'
    region = 'федеральный уровень'

    WORD_TO_SEARCH = 'назначить'

    worker = DecreeWorker(entity_name=region, search_link=link, unwanted_words=unwanted_words, 
                            links_file_exists=False, parse_only=False, word_to_search=WORD_TO_SEARCH)

    worker.go()
 

    #TODO: мб files downloader может наследоваться от data handler. было бы логично 
    #TODO: обработка ошибок
    #TODO добавить: 
    # имя региона в файл?
    # 1. склонение начальник/директор 
    
    #TODO:
    # если два имени и в одном три слова, то второе имя дропнуть
    #TODO: если имена не имена а города - дропнуть строку
    # мб через падежи? pymorphy?
    # скрипт, который парсит логи и проверяет все ли скачалось
    # фронт можно сделать на джанге
    # !!! IMPORTANT !!! сделать освободить от должности 



    # V интерфейс для поиска по словам?
    
