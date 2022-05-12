import aiohttp
import asyncio
from api.main import DataHandler

class FilesDownloader:

    def __init__(self, destination_folder:str, meta_data_handler:DataHandler) -> None:
        """принимает ссылки на доки"""
        self.destination_folder = destination_folder
        self.downloaded = 0
        self.results = []
        self.meta_data_handler = meta_data_handler
        self.files_n_links = []

    async def download(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                try:
                    response
                    # TODO: wait for responce
                    # response.
                    print('SAVE FILES')
                    filename = ''
                    
                    print('downloaded ---', f'{self.downloaded}/{self.links}' )
                    self.results.append('ok')
                    self.files_n_links.append({'filename':filename, 'link':url})
                    # self.meta_data_handler({'filename':filename,'link':url})  


                except Exception as ex:
                    print(ex.with_traceback)
                    self.results.append(ex.args[0])

    async def gather(self, links):
        await asyncio.gather(*[self.download(link) for link in links])


    def get(self, links:list[str]):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.gather(links))
        self.meta_data_handler.save_links_n_filenames(self.files_n_links)


