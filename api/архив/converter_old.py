import os
from pydoc import doc
import stanza
import tqdm

class Parser:
    pass

raw_folder = 'downloads/files/duma_2000_2022'
raw_folder = 'downloads/files/pres_2000_2022'
raw_folder = 'downloads/files/test'

import pickle

"""скаченный rtf to txt """


from bs4 import BeautifulSoup


def stanza_nlp_ru(text):
    nlp = stanza.Pipeline(lang='ru', processors='tokenize,ner')
    doc = nlp(text)
    # result = [{'entity':ent.text, 'ent_type':ent.type} for sent in doc.sentences for ent in sent.ents]
    result = [{ent.type:ent.text} for sent in doc.sentences for ent in sent.ents]

    # print(*[f'entity: {ent.text}\ttype: {ent.type}' for sent in doc.sentences for ent in sent.ents], sep='\n')
    
    return result 
    
results = []

stop_words = 'назначить наказание' 

for file in tqdm.tqdm(os.listdir(raw_folder)):
    # file = r"C:\Users\ironb\Downloads\Р-38-Р-18_04_2018.rtf"
    # file = r"C:\Users\ironb\Downloads\Р-119-РГ-13_04_2018.rtf"
    try:   
        raw_text = open(os.path.join(raw_folder, file)).read()        
        if 'Назначить' not in raw_text and 'назначить' not in raw_text:
            continue

        soup = BeautifulSoup(raw_text, 'html.parser')        
        tags = soup.find_all(['p','h1','h2','h3','span'])
        raw_text = [e.text for e in tags if e.text != '\xa0']
        raw_text = set(raw_text)
        text = [e.replace('\xa0',' ') for e in raw_text]
        # идем по строчкам, как нашли Назначить - ищем точку
        appoitment_lines = [e for e in text if 'Назначить' in e or 'назначить' in e]
        # print('appoitment_lines---',appoitment_lines)
        
        results.append({
            'file':file, 
            'app_lines' : appoitment_lines,
            'raw': text
        })

        # text_entites = []
        # for line in text:
        #     parsing_res = stanza_nlp_ru(line)
        #     parsing_res.append({'raw_line':line})
        #     text_entites.append(parsing_res)
        # results.append({'file':file, 'res':text_entites})
 
    except Exception as ex:
        results.append({'file':file, 'res':'', 'err':ex})

with open('test.pkl', 'wb') as f:
    pickle.dump(results, f)


'''
все скаченное лежит в wsl /root/.deeppavlov/downloads
'''

# 2. продолжать искать правила для поиска имен



