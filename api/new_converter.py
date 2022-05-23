import json
import typing
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) 

import typing
import tqdm
import os
import re
from pathlib import Path

from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    NamesExtractor,
    PER,
    Doc
) 

from bs4 import BeautifulSoup

from api.utils.json_validation import FileData

from api.utils.my_logger import Log, get_file_logger

filelogger = get_file_logger(__name__)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)


class MyParser:
    """берет файл, находит строчку с назначением и должностью"""

    def __init__(self, data_hanlder='', unwanted_words:str='api/unwanted_words.txt', location='', word_to_search:str='назначить'):
        self.unwanted_words = open(unwanted_words, 'r', encoding='utf-8').read().split('\n')
        self.file_data_class = FileData
        self.file_data:FileData 
        self.data_hanlder = data_hanlder
        self.location = location
        self.word_to_search = word_to_search

    def get_file_info(self, file_path:str)->dict[str,str]:
        file_name = Path(file_path).name
        self.file_name = file_name
        
        date = file_name.split('-')[-1].split('.')[0].replace('_','-')
        return {'file_name':file_name, 'date': date, 'file_path':file_path}

    def get_raw_text(self)->None:
        with open(self.file_data.file_path) as f:
            raw_text = f.read()

        if not self.word_to_search.lower() in raw_text and not self.word_to_search.capitalize() in raw_text:
            raise ValueError('search word not found')

        if 'освободи' in raw_text or 'Освободи' in raw_text:
            print('освободи --- ', self.file_name)

        soup = BeautifulSoup(raw_text, 'html.parser')        

        tags = soup.find_all(['p','h1','h2','h3','span'])
        raw_text = [e.text for e in tags if e.text != '\xa0']
        raw_text = set(raw_text)
        raw_text = [e.replace('\xa0',' ') for e in raw_text]
        self.file_data.text_raw = raw_text #'\n'.join(raw_text)
        
        # если надо вытащить все тэги 
        # raw_text = [tag.text for tag in soup.findAll(recursive=False)] 

        
    def get_appointment_lines(self)->None:
        # фльтруем по поисковому слову
        appointment_lines = [e for e in self.file_data.text_raw if self.word_to_search.lower() in e 
                            or self.word_to_search.capitalize() in e]
        
        for line in appointment_lines:
            self.file_data.appointment_lines.append({
                'raw_line':line
            })

    def _locate_names_in_string(self, text, *args, **kwargs)->list[dict[str,str]]:
        """находит в строке имена, возвращает их индексы"""
        doc = Doc(text)
        doc.segment(segmenter) 
        doc.tag_morph(morph_tagger)
        for token in doc.tokens:
            token.lemmatize(morph_vocab)

        doc.parse_syntax(syntax_parser)
        doc.tag_ner(ner_tagger)
        for span in doc.spans:
            span.normalize(morph_vocab)

        names = []
        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)
                names.append(span)

        # конкатинируем, если фамилия и имя отдельно
        if len(names) == 2 and (len(names[1].fact.as_dict) + len(names[0].fact.as_dict) == 3):
            concated_name_norm = names[0].normal + ' ' + names[1].normal 
            concated_name_norm = ' '.join(concated_name_norm.split())
            concated_name_raw = names[0].text + ' ' + names[1].text 
            concated_name_raw = ' '.join(concated_name_raw.split())
            names = [{'name_raw':concated_name_raw, 'name_norm':concated_name_raw}]
        else:
            names = [{'name_raw':' '.join(span.text.split()),'name_norm':' '.join(span.normal.split())} for span in names]
        return names


    def find_names_in_line(self)->None:
        """при нахождении имен добавляет в {'name'} """    
        names_located = False            
        # breakpoint()
        for line in self.file_data.appointment_lines:
            name = self._locate_names_in_string(line['raw_line'])
            if name:
                line['names'] = name
                names_located = True
        if not names_located:  
            raise ValueError('no names found')

    def remove_unwanted_words(self, line:str)->str:
        line = line.lower()
        line = ' '.join(line.split())
        line = line.replace('.', '')
        line = line.replace(',', '')    

        # TODO: unwanted_words = '|'.join(self.unwanted_words) 
        for w in self.unwanted_words: 
            p = f'(?<!\S)({w})(?!\S)' 
            line = re.sub(pattern=p, repl=' ', string=line)
        
        line = re.sub(string=line, pattern='\d', repl='')
        line = ' '.join(line.split())        
        line = re.sub(string=line, pattern=f'^{self.location}', repl='')
        return line

    def check_for_stop_words(self, line:str)->bool:
        stop = ['при рассмотрении в государственной думе', 'при  рассмотрении  законопроекта председателя', 'государственной думе','официальным представителем', 'стипендия', 'стипендий','стипендию', 'ответственным за']
        stop: str = '|'.join(stop)
        stop_words_in_line = re.findall(pattern=stop, string=line)
        return bool(stop_words_in_line)

    def find_position(self)->None:
        position_exists_in_file = False

        for line in self.file_data.appointment_lines:
            position = line['raw_line']
            position = ' '.join(position.split())
            # breakpoint()
            for name in line['names']:
                position = position.replace(name['name_raw'],'')

            position = position.lower()
            if self.check_for_stop_words(position):
                continue

            position = position.split('освободив')[0]
            position = position.split('в порядке перевода')[0]
            position = self.remove_unwanted_words(position)    
            line['position'] = position
            position_exists_in_file = True
        
        if not position_exists_in_file:
            raise ValueError('No position, or position is in stop words')
    
    def add_url_info(self):
        file_name = self.file_data.file_name
        try:
            link = self.data_hanlder.files_n_links[file_name]
            self.file_data.link = link
        except Exception as ex:
            print(ex)
            print(f'не нашли ссылку для {file_name}')

    def parse_file(self, file_path:str)->FileData:
        file_info = self.get_file_info(file_path=file_path)
        # собрали инфу про файл
        self.file_data = self.file_data_class(**file_info)
        # # вытащили сырой текст
        self.get_raw_text()
        # нашли строки с "назначить"
        self.get_appointment_lines()
        # нашли в этих строках имена
        self.find_names_in_line()
        # удалили из сырого текста все лишнее (имена, даты, служебные слова)
        self.find_position()
        # сделали изначальный текст строкой
        self.file_data.text_raw = '\n'.join(self.file_data.text_raw)
        # добавили ссылку на скачивание файл
        self.add_url_info()
        return self.file_data


if __name__ == '__main__':

    # f = r"C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions\ивановская область\raw_files\-1--21_01_2002.rtf"
    # f = r"C:\Users\ironb\Downloads\П-103-26_04_2016.rtf"
    # f = r"C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions\Ивановской области\raw_files\-10--13_01_2006.rtf"
    fed_folder = Path(r'C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions\федеральное законодательство\raw_files')
    rogue_files = json.load(open('rogue_files.json', 'r'))
    rogue_files = [e['file'] for e in rogue_files if e['err'] == "'names'"]
    # print(rogue_files)
    # когда много мб сплитить по ; ?
    # освободив -569--10_03_2021.rtf
    # -489-03_08_2020.rtf - тут и много и освободив
    #      #     #f = rogue_files[0]
    f = '-1192--05_05_2021.rtf'
    f = fed_folder / f

     

    parser = MyParser()
    from pprint import pprint
    pprint(parser.parse_file(f))