import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import unittest
from api.converter import MyParser


stop_words = 'api/unwanted_words.txt'
my_parser = MyParser(location='алтайского края', unwanted_words=stop_words)
test_folder = 'api/tests/test_data'
 

class TestApi(unittest.TestCase): 
    
    def test_parser(self):
        correct_data = [{
            'NAME':'Гарибян Артур Петросович',
            'POSITION':  'московской области министра правительства московской области по государственному надзору строительстве',
            'RAW LINE': 'Назначить 10.06.2021 Гарибяна Артура\nПетросовича на государственную должность Московской области министра\nПравительства Московской области по государственному надзору в строительстве с\nдолжностным окладом в размере, кратном должностному окладу специалиста II\nкатегории согласно штатному расписанию.',
            'FILE': 'Ï-171-ÏÃ-10_06_2021'
                        }]

        files = my_parser.parse_folder(folder_path=test_folder)
        for file in files:            
            # # print('file---', file)
            position = file[0]['position']
            name = file[0]['name']
            raw_line = file[0]['file']['app_lines']
            self.assertEqual(position, correct_data[0]['POSITION'])
            break
            # self.assertEqual(2,2)
            
            # print('NAME: ',file[0]['name'])
            # print('POSITION: ', f'|{position}')
            # print('RAW LINE: ',file[0]['file']['app_lines'])
            # print('FILE :: ', file[0]['file']['file'])
            # print('='*10)

if __name__ == '__main__':
    unittest.main()

#     NAME:  Гарибян Артур Петросович
# POSITION:  | министра правительства московской области по государственному надзору в строительстве согласно
# RAW LINE:  ['Назначить 10.06.2021 Гарибяна Артура\nПетросовича на государственную должность Московской области министра\nПравительства Московской области по государственному надзору в строительстве с\nдолжностным окладом в размере, кратном должностному окладу специалиста II\nкатегории согласно штатному расписанию.']
# FILE ::  Ï-171-ÏÃ-10_06_2021

# NAME:  Мишонову Оксана Владимировну
# POSITION:  |уполномоченного по правам ребенка в московской области с
# RAW LINE:  ['Назначить Мишонову Оксану Владимировну на должность\nУполномоченного по правам ребенка в Московской области с 23 декабря 2021 года.']
# FILE ::  Ï-2_11-Ï-16_12_2021


# NAME:  Саитгареев Руслан Ринатович
# POSITION:  | первого заместителя министра здравоохранения московской области
# RAW LINE:  ['Принять Саитгареева Руслана Ринатовича на\nгосударственную гражданскую службу Московской области и назначить на должность\nпервого заместителя министра здравоохранения Московской области, установив срок\nиспытания продолжительностью 3 месяца.']
# FILE ::  Ð-138-ÐÃ-29_04_2021