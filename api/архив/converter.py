import typing
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import typing
import tqdm
from genericpath import isfile
import os
import re
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

from pathlib import Path
from bs4 import BeautifulSoup

from api.utils.my_logger import Log
segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)


class MyParser:
    """берет файл, находит строчку с назначением и должностью, сохраняет в папку results"""

    def __init__(self,  location, unwanted_words:str='api/unwanted_words.txt'):
        self.unwanted_words = open(unwanted_words, 'r', encoding='utf-8').read().split('\n')
        self.location = location
        # self.file_to_parse = file_to_parse 
        # self.path_to_save = path_to_save

    @Log(__name__)
    def _locate_names_in_string(self, text, *args, **kwargs)->list[int]:
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
                # print('as_dict---',span.fact.as_dict)
                # names_index.append({"start":span.start,'stop':span.stop})
    
        return names 

    @Log(__name__)
    def extract_text_from_file(self, filepath:str)->dict[str, typing.Any] | bool:
        with open(filepath) as f:
            raw_text = f.read()

        if 'Назначить' not in raw_text and 'назначить' not in raw_text:
            print('Не найдено "назначить" --- ',filepath)
            return False
        
        soup = BeautifulSoup(raw_text, 'html.parser')        
        tags = soup.find_all(['p','h1','h2','h3','span'])
        raw_text = [e.text for e in tags if e.text != '\xa0']
        raw_text = set(raw_text)
        text = [e.replace('\xa0',' ') for e in raw_text]
        # идем по строчкам, как нашли Назначить - ищем точку
        appoitment_lines = [e for e in text if 'Назначить' in e or 'назначить' in e]
        # print('appoitment_lines---',appoitment_lines)
        
        return({
            'file': Path(filepath).stem, 
            'app_lines' : appoitment_lines,
            'raw': text
        })

    @staticmethod
    def normaliaze_position(string:str)->str:
        pass

    @Log(__name__)
    def find_names_in_line(self, file)->dict[str,list]:
        file['names'] = [] 
        for line in file['app_lines']:
            names = self._locate_names_in_string(text=line)
            if names:
                file['names'].append(names)
        if not file['names']:
            raise ValueError('no_name')
        return file

    @Log(__name__)
    def clean_up(self, line:str):
        line = line.lower()
        line = ' '.join(line.split())
        line = line.replace('.', '')
        line = line.replace(',', '')    

        # unwanted_words = '|'.join(self.unwanted_words) 
        for w in self.unwanted_words: 
            p = f'(?<!\S)({w})(?!\S)' 
            line = re.sub(pattern=p, repl=' ', string=line)
        
        line = re.sub(string=line, pattern='\d', repl='')
        line = ' '.join(line.split())        
        line = re.sub(string=line, pattern=f'^{self.location}', repl='')
        return line

    @Log(__name__)
    def check_for_stop_words(self, line:str)->bool:
        stop = ['при рассмотрении в государственной думе', 'государственной думе','официальным представителем', 'стипендия', 'стипендий','стипендию']
        stop: str = '|'.join(stop)
        stop_words_in_line = re.findall(pattern=stop, string=line)
        return bool(stop_words_in_line)

    @Log(__name__)
    def find_position(self, file) -> list[dict[str, str]]:
        lines = file['app_lines']
        names = file['names']
        # надо убрать имя
        results = []
        for line, list_of_names in zip(lines, names):
            line = line.lower()
            line = ' '.join(line.split())

            # убираем лишние слова
            stop_words_detected = self.check_for_stop_words(line)
            if stop_words_detected:
                raise ValueError('stop_words')

            full_name = []
            for name_part in list_of_names:
                line = line.replace(name_part.text,'')
                full_name.append(name_part)

            name_to_delete = ' '.join([e.text.lower() for e in full_name])
            name_to_delete = ' '.join(name_to_delete.split())
            line = line.replace(name_to_delete, '')
            name_normalized = [e.normal for e in full_name]

            line = self.clean_up(line)
            #TODO: зачем это?? 
            position = ' '.join(line.split('\n'))

            results.append({
                'name': name_normalized,
                'position':position,
                'file':file,
            })

        return results

    @Log(__name__)
    def add_file_info(self, data:dict, filepath:str, date:str, link='')->dict:
        data['filepath'] = filepath
        data['date'] = date
        return data

    @Log(__name__)
    def get_names_n_positions(self, filepath='', date=''):
        #1 получили файл, взяли из него текст
        file_data = {
                'filename':e,
                'filepath': filepath,
                'raw_text': '???',
                'names':[] 
            }

        raw_text_n_app_lines = self.extract_text_from_file(filepath)
        # 2 нашли имя 
        text_with_names = self.find_names_in_line(raw_text_n_app_lines)
        # 3 нашли должность
        text_with_names_n_position = self.find_position(text_with_names)
        # 4 добавили имя файла
        text_with_names_n_position = [self.add_file_info(line, filepath, date) for line in text_with_names_n_position]
        return text_with_names_n_position

    @Log(__name__)
    def parse_folder(self, folder_path)->list[dict[str,str]]:
        

        results_info :dict[str, list] = {'no_name':[], 'нет назначить':[],'stop_words':[] , 'ok':[], 'err':[]}
        results = []
        for e in tqdm.tqdm(os.listdir(folder_path)):
            try:
                filepath = os.path.join(folder_path, e)

                file_data = {
                    'filename':e,
                    'filepath': filepath,
                    'raw_text': '???' 
                }

                print('='*10,'start converting', '='*10,)
                date = e.split('-')[-1].split('.')[0].replace('_','-')
                if not isfile(filepath):
                    results_info['нет назначить'].append(e)
                    continue    

                parsed_data = self.get_names_n_positions(filepath, date)
                results.append(parsed_data)
                results_info['ok'].append(e)
                
            except ValueError as ex: 
                results_info['err'].append({'file':e, 'err':ex.args})
                
            except Exception as  ex:
                import traceback
                print(ex)
                traceback.print_exception(ex)
                results_info['err'].append({'file':e, 'err':ex})


        # print('results --- ', results_info)
        # results = [{e:len(results[e])} for e in results_info.keys()]
        # print('total -- ', results_info)
        

        return results


# PATH = 'downloads/files/алтайский_край'
# parser = MyParser('алтайского края')
# parse_folder(PATH)


#TODO: 
# стоп слова которые дропают всю линию (назначить именную стипендию)
# Multiple appointments
# нормализацию должности  
# ! добавить ссылку на скачивание !

# 1. Возможно можно удалить все после 
# "освободив от занимаемой должности..."
# освободив...
# возможно удалить и добавить флажок куда нибудь область 
# выташить дату !!! 
# кто подписал? просто нижний <p> или <h> и if на имя


