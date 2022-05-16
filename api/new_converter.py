from turtle import pos
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
    
    PER,
    NamesExtractor,

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
    """берет файл, находит строчку с назначением и должностью, сохраняет в папку results"""

    def __init__(self, data_hanlder, unwanted_words:str='api/unwanted_words.txt', location=''):
        self.unwanted_words = open(unwanted_words, 'r', encoding='utf-8').read().split('\n')
        self.file_data_class = FileData
        self.file_data = ''
        self.data_hanlder = data_hanlder
        self.location = location

    def get_file_info(self, file_path:str)->dict[str,str]:
        file_name = Path(file_path).name
        date = file_name.split('-')[-1].split('.')[0].replace('_','-')
        return {'file_name':file_name, 'date': date, 'file_path':file_path}

    def get_raw_text(self)->None:
        with open(self.file_data.file_path) as f:
            raw_text = f.read()

        if 'Назначить' not in raw_text and 'назначить' not in raw_text:
            raise ValueError('нет назначить')

        soup = BeautifulSoup(raw_text, 'html.parser')        
        tags = soup.find_all(['p','h1','h2','h3','span'])
        raw_text = [e.text for e in tags if e.text != '\xa0']
        raw_text = set(raw_text)
        raw_text = [e.replace('\xa0',' ') for e in raw_text]
        self.file_data.text_raw = raw_text #'\n'.join(raw_text)
        
    def get_appointment_lines(self)->None:
        appointment_lines = [e for e in self.file_data.text_raw if 'Назначить' in e or 'назначить' in e]
        for line in appointment_lines:
            self.file_data.appointment_lines.append({
                'raw_line':line
            })

    def _locate_names_in_string(self, text, *args, **kwargs)->list[Doc]:
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
        #TODO: тут можно подумать, что делать, если несколько имены
        for span in doc.spans:
            if span.type == PER:
                span.extract_fact(names_extractor)
                names.append({'name_raw':span.text,'name_norm':span.normal})
        return names

    def find_names_in_line(self)->None:
        """при нахождении имен добавляет в {'name'} """    
        names_located = False
        for line in self.file_data.appointment_lines:
            name = self._locate_names_in_string(line['raw_line'])
            if name:
                line['names'] = name
                names_located = True
        if not names_located:  
            raise ValueError('нет имен')

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
            for name in line['names']:
                position = position.replace(name['name_raw'],'')

            position = position.lower()
            if self.check_for_stop_words(position):
                continue
            position = ' '.join(position.split())
            position = position.split('освободив')[0]
            position = position.split('в порядке перевода')[0]
            position = self.remove_unwanted_words(position)    
            line['position'] = position
            position_exists_in_file = True
        
        if not position_exists_in_file:
            raise ValueError('неподходящая должность')
    
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
    f = r"C:\Users\ironb\прогр\Declarator\appointment-decrees\downloads\regions\ивановская область\raw_files\-1--21_01_2002.rtf"
    parser = MyParser()

    # parser.parse_file(f)
    print(parser.parse_file(f))