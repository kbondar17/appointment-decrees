from api.aio_files_downloader import FilesDownloader
import unittest
import os
from bs4 import BeautifulSoup 
import asyncio
import shutil

test_links = ['http://pravo.gov.ru/proxy/ips/?savertf=&link_id=0&nd=104148984&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC&firstDoc=1&page=all',
'http://pravo.gov.ru/proxy/ips/?savertf=&link_id=0&nd=104148984&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC&firstDoc=1&page=all']
result_folder = 'api/tests/test_data/test_download_results'

class MyTest(unittest.TestCase): 

    def __init__(self, methodName) -> None:
        super().__init__(methodName)
        self.result_folder = 'api/tests/test_data/test_download_results'
        shutil.rmtree(self.result_folder)
        os.makedirs(self.result_folder)

    def get_files(self):
        
        test_links = ['http://pravo.gov.ru/proxy/ips/?savertf=&link_id=14&nd=104140949&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC%0D%0A&page=all',
        'http://pravo.gov.ru/proxy/ips/?savertf=&link_id=15&nd=104140698&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC%0D%0A&page=all']

        d = FilesDownloader(result_folder=self.result_folder, files_n_links_file='f_n_l.txt')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(d.fetch_all(test_links,loop))
        print('downloaded')

    def test_files(self):
        self.get_files()
        self.assertEqual(set(os.listdir(self.result_folder)), 
       set(['-451--11_06_2021.rtf', '-62-02_06_2021.rtf']))
                         

        