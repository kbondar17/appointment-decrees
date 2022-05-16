import requests
import os
import time
import re
from random import uniform
import urllib
from torch import gather
import tqdm

# links = open('downloads/links/duma_2010_2022__links.txt', 'r').read().split('\n')
links = open('downloads/links/pres_links_2000_2022.txt', 'r').read().split('\n')
links = open('downloads/links/mos_oblast.txt', 'r').read().split('\n')
links = open('downloads/links/алтайский_край.txt', 'r').read().split('\n')




def download_doc_set(filname):
    pass

from collections import Counter

results = []

# for link in tqdm.tqdm(links):
#     # print(link)
#     try:
#         r = requests.get(link, timeout=(3,60))
#         if not r.ok:
#             print('ошибка')
#             print(link)
#             print(r.status_code)
#             results.append('ошибка запроса')
#             continue

#         content = r.content.decode('cp1251')
#         if not 'назначить' in content and not 'Назначить' in content:
#             results.append('нет назначить')
#             continue
        
#         filename = re.findall("filename=(.+)", r.headers['Content-Disposition'])[0]
#         # print(filename)
#         # print(filename.encode('utf-8').decode())
#         # print(filename.encode('cp1251').decode('utf-8'))

#         with open(f'downloads/files/алтайский_край/{filename}', 'wb') as f:
#             results.append('сохранено')            
#             f.write(r.content) 
#             f.write(r.content) 
#             time.sleep(uniform(a=0.3,b=1.5))

#     except Exception as ex:
#         results.append('другая ошибка')            
#         print('ERROR')
#         print(ex)
#         # TODO: какая то херь с названием доковк


import aiohttp
import asyncio
i=0
total = len(links)
async def download(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            global i
            i+=1
            print(f'{i}/{total}')
            # try:
            #     r = requests.get(link, timeout=(3,60))
            #     if not r.ok:
            #         print('ошибка')
            #         print(link)
            #         print(r.status_code)
            #         results.append('ошибка запроса')
            #         continue

            #     content = r.content.decode('cp1251')
            #     if not 'назначить' in content and not 'Назначить' in content:
            #         results.append('нет назначить')
            #         continue
                
            #     filename = re.findall("filename=(.+)", r.headers['Content-Disposition'])[0]
            #     # print(filename)
            #     # print(filename.encode('utf-8').decode())
            #     # print(filename.encode('cp1251').decode('utf-8'))

            #     with open(f'downloads/files/алтайский_край/{filename}', 'wb') as f:
            #         results.append('сохранено')            
            #         f.write(r.content) 
            #         f.write(r.content) 
            #         time.sleep(uniform(a=0.3,b=1.5))

            # except Exception as ex:
            #     results.append('другая ошибка')            
            #     print('ERROR')
            #     print(ex)


async def main(links):
    await asyncio.gather(*[download(link) for link in links])

links = open('downloads/links/алтайский_край.txt', 'r').read().split('\n')

loop = asyncio.get_event_loop()
loop.run_until_complete(main(links[:15]))


