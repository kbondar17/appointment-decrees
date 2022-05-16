import json
import pickle
from typing import Any
from pathlib import Path
from dataclasses import dataclass, field        
from pathlib import Path

from api.utils.json_validation import FileData
from api.utils.my_logger import Log


class DataHandler:

    def __init__(self, entity_name) -> None:
        self.create_folders(entity_name)
        self.files_n_links = {}
    
    def add_files_n_links(self, file_n_link:dict):
        self.files_n_links.update(file_n_link)

    def save_results_json(self, data:list[FileData]):
        filepath = str(self.results_folder) + self.region_name +  '_parsed.json'
        data = {'parsed_data':[e.dict() for e in data]}
        with open(filepath, 'w') as f:
            json.dump(data, f)
            print(f'Сохранили в {filepath} в json')

    def save_results_pkl(self, data:list[FileData])->None:
        # TODO: сохраняет целиком
        filepath = str(self.results_folder) + self.region_name +  '_parsed.pkl'
        data = {'parsed_data':[e for e in data]}
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
            print(f'Сохранили в {filepath} в pickle!')

    def save_links_n_filenames(self, data):
        with open(self.links_n_filenames_path, 'wb') as f:
            pickle.dump(obj=data, file=f)
            
    @Log(__name__)
    def save_links(self, links:list[str])->list[str]:
        filename = self.links_folder / 'links.txt'
        with open(filename, 'w') as f:
            f.write('\n'.join(links))
            print(f'Сохранено {len(links)} ссылок на документы')                
        return links
    
    def get_pre_downloaded_links(self):
        file_path = self.links_folder / 'links.txt'
        with open(file_path, 'r') as f:
            return f.read().split('\n')

    def create_folders(self, region_name):
        self.region_name = region_name
        current_region_folder = Path('downloads') / 'regions' / region_name
        
        self.links_folder = Path(current_region_folder) / 'links'
        self.links_folder.mkdir(parents=True, exist_ok=True)
        
        self.raw_files_folder = Path(current_region_folder) / 'raw_files' 
        self.raw_files_folder.mkdir(parents=True, exist_ok=True)
        
        self.results_folder = Path(current_region_folder) / 'results'
        self.results_folder.mkdir(parents=True, exist_ok=True)

        self.files_n_links_file = current_region_folder / 'files_n_links_file.txt'

        print('создали папки --- ', self.links_folder, self.raw_files_folder, self.results_folder)        
        



# @dataclass(kw_only=True)
# class FileData:
#     file_name : str = None
#     file_path : str|Path = None
#     date : str = None
#     text_raw : str|None = None
#     link : str = None 

#     appointment_lines : list[str] = field(default_factory=list)
#     # names : list[str] = field(default_factory=list)


