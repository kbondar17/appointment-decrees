import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from random import uniform
import aiohttp
import asyncio
from pathlib import Path
import time


from api.utils.my_logger import get_file_logger

filelogger = get_file_logger(__name__)

class FilesDownloader:
    """скачивает и сохраняет файлы по ссылке"""
    
    def __init__(self, result_folder:str|Path, files_n_links_file:str|Path, links:list[str], data_hanlder) -> None:
        """принимает ссылки на доки"""
        self.result_folder = Path(result_folder)
        self.files_n_links_file = files_n_links_file
        self.links = links
        self.timeout = aiohttp.ClientTimeout(400)
        # для проверки результатов
        self.results: list[str] = []
        self.files_n_links: list[dict[str, str]] = []
        self.count = 0
        self.data_hanlder = data_hanlder
        self.processed_links = []        

    async def fetch(self, session, url):
        async with session.get(url) as response:
            try:
                headers = response.headers
                content = await response.content.read()
                decoded = content.decode('cp1251') 

                if not 'назначить' in decoded and not 'Назначить' in decoded:
                    # time.sleep(uniform(0.3, 1.5))
                    # await asyncio.sleep(uniform(0.3, 1.5))
                    self.results.append('нет назначить')
                    raise ValueError('нет назначить')

                filename = headers['Content-Disposition'].split('filename=')[-1].encode('utf-8', errors='ignore').decode('utf-8') 

                self.data_hanlder.add_files_n_links({filename:url})

                # сохраняем файл
                with open(self.result_folder / filename, 'wb') as f:
                    f.write(content)
                    self.results.append('ok')
                
                #сохраняем {имя_файла:ссылка}
                with open(self.files_n_links_file, 'a') as f:
                    line = str({"filename":filename, "link":url})
                    f.write(f'{line}\n')

                # time.sleep(uniform(0.3, 1.5))
                # await asyncio.sleep(uniform(0.3, 1.5))
                self.processed_links.append(url)
                self.count += 1
                print(f'{self.count}/{self.total}')
                return True

            except Exception as ex:            
                self.processed_links.append(url)                 
                time.sleep(uniform(0.3, 0.9))
                # await asyncio.sleep(uniform(0.3, 1.5))
                self.count += 1
                print(f'{self.count}/{self.total}')
                # import traceback
                # print('=== ERROR ===')
                # print(url)
                # print(traceback.print_exc())
                # print('================')
                self.results.append(ex)

    async def fetch_all(self, urls, loop):
        self.total = len(urls)
        async with aiohttp.ClientSession(loop=loop) as session:
            res = await asyncio.gather(*[self.fetch(session, url) for url in urls], return_exceptions=True)
            return res

    def go(self) -> list[dict[str,str]]:

        from collections import Counter

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_all(urls=self.links, loop=loop))

        not_processed = set(self.links).difference(set(self.processed_links))

        filelogger.warning('было ссылок на файлы {}. Из них скачали {}'.format(len(self.links), len(self.files_n_links) ))
        filelogger.warning('НЕ ОБРАБОТАЛИ ЭТИ ФАЙЛЫ {}'.format(not_processed))
        filelogger.warning(str(Counter(self.results)))
        
        print('===== РЕЗУЛЬТАТЫ скачивания ==== ', )
        print(Counter(self.results))
        print('======'*2)
        return self.files_n_links

# def download_files(links:list[str], result_folder:str|Path, files_n_links_file:str|Path):

#     # d = FilesDownloader(result_folder=result_folder, files_n_links_file=files_n_links_file)
#     loop = asyncio.get_event_loop()
#     html = loop.run_until_complete(d.fetch_all(test_links,loop))
#     print(html)


if __name__ == '__main__':
    test_links = ['http://pravo.gov.ru/proxy/ips/?savertf=&link_id=14&nd=104140949&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC%0D%0A&page=all',
    'http://pravo.gov.ru/proxy/ips/?savertf=&link_id=15&nd=104140698&intelsearch=%ED%E0%E7%ED%E0%F7%E8%F2%FC%0D%0A&page=all']

    # test_links = ['https://stackoverflow.com/questions/48840378/python-attempt-to-decode-json-with-unexpected-mimetype']
    result_folder = 'api/tests/test_data/test_download_results'

    d = FilesDownloader(result_folder=result_folder, files_n_links_file='')
    loop = asyncio.get_event_loop()
    html = loop.run_until_complete(d.fetch_all(test_links,loop))
    print(html)


