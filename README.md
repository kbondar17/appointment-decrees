#  База законодательных актов РФ

Это апи для http://pravo.gov.ru/proxy/ips/?start_search&fattrib=1

### Настройка
1. Для работы Selenium необходим вебдрайвер. Например Chrome https://chromedriver.chromium.org/downloads
2. В корне проекта нужно создать .env файл и указать в нем путь до вебдрайвера (как в .env_defualt).

### Использование
Запросы можно фильтровать по органу, дате и ключевым словам. Орган следует указывать точно так, как на сайте. 
Даты указываются в формате дд.мм.гггг. 
Date-type может быть либо "Период" (тогда указываем date-from и date-to), либо "Точно" (тогда указываем date)

Пример c периодом:
```
python -m api get-docs --gov-body "Государственная Дума Федерального Собрания" --date-type Период --date-from 01.10.2021 --date-to 01.12.2021 --key-word назначить --filename='duma_links.txt'
```

Пример c точной датой:
```
python -m api get-docs --gov-body "Государственная Дума Федерального Собрания" --date-type Точно --date 01.10.2021 --key-word назначить --filename='duma_links.txt'
```
