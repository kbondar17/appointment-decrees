import imp
import requests 
import os
import re
import time
from random import uniform
from pathlib import Path

class FilesDownloader:
    def __init__(self, result_folder) -> None:
        self.result_folder = Path(result_folder)
        self.results = []

    def get(self, links:list):
        for link in links:
            r = requests.get(link, timeout=(3, 60))
            if not r.ok:
                print('ошибка')
                print(link)
                print(r.status_code)
                self.results.append('ошибка запроса')
                continue

            content = r.content.decode('cp1251')
            if not 'назначить' in content and not 'Назначить' in content:
                self.results.append('нет назначить')
                continue
            
            filename = re.findall("filename=(.+)", r.headers['Content-Disposition'])[0]

            with open(self.result_folder / filename, 'wb') as f:
                self.results.append('сохранено')            
                f.write(r.content) 
                time.sleep(uniform(a=0.3,b=1.5))
