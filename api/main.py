'''
Инкапсуляция. 
'''
from typing import Any
import pickle

from api.temp_api import TempApi
from api.files_downloader import FilesDownloader
from api.converter import MyParser

class DataHandler:

    def __init__(self, result_data_folder, links_n_filenames_path:str) -> None:
        # self.meta_path = meta_path
        self.result_data_folder = result_data_folder
        self.links_n_filenames_path = links_n_filenames_path

    def create_folder_if_not_exists(foldername):
        pass

    
    def save_pkl(self, data:Any, path='')->None:
        if not path:
            path = self.result_data_folder
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    @staticmethod
    def save_csv():
        pass

    def save_links_n_filenames(self, data):
        with open(self.links_n_filenames_path, 'wb') as f:
            pickle.dump(obj=data, file=f)
            

    def meta_data(self, data:dict):
        existing_data = pickle.load(open(self.meta_path,'r+w'))
        if type(existing_data) == list:
            existing_data.append(data)


class DecreeWorker:

    def __init__(self, search_link, entity_name, unwanted_words, result_folder, meta_data_path):
        self.files_folder = f'downloads/{entity_name}'
        self.links_getter = TempApi()
        self.files_downloader = FilesDownloader(entity_name)
        self.parser = MyParser(location=entity_name, unwanted_words=unwanted_words) 
        self.data_handler = DataHandler(result_folder, meta_data_path)
    
        self.go(search_link)


    def get_links_from_site(self, link)->list[str]:
        links = self.links_getter.get(link)
        return links

    def download_files(self, links:list[str]):
        self.files_downloader.get(links, self.data_handler)


    def parse_files(self, files_folder):
        self.parser.parse_folder(files_folder)

    def go(self, search_link):
        # получили ссылки
        links = self.get_links_from_site(search_link)
        # скачали ссылки. папка прописана в ините
        self.download_files(links)
        # парсим файлы
        parsed_data = self.parse_files(self.files_folder)
        # сохраняем
        self.data_handler.save_pkl(parsed_data)


# main_link -> links -> files -> parsed_files 

link = r'http://pravo.gov.ru/proxy/ips/?searchres=&bpas=r013200&a3=&a3type=1&a3value=&a6=&a6type=1&a6value=&a15=&a15type=1&a15value=&a7type=3&a7from=&a7to=&a7date=01.01.2000&a8=&a8type=1&a1=&a0=%ED%E0%E7%ED%E0%F7%E8%F2%FC&a16=&a16type=1&a16value=&a17=&a17type=1&a17value=&a4=&a4type=1&a4value=&a23=&a23type=1&a23value=&textpres=&sort=7&x=64&y=11'
entity_name = 'брянская область'
unwanted_words = 'api/unwanted_words.txt'

worker = DecreeWorker(search_link=link, entity_name=entity_name, unwanted_words=unwanted_words)


#TODO: обработка ошибок
