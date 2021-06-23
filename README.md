# simple-full-text-search-service
A simple service for full-text searching in text-documents stored in PostgreSQL using Elasticsearch. Written for learning purposes.

##  Инструкции по поднятию.

### 1. Начальные приготовления.
  1. Клонировать репозиторий:
`git clone https://github.com/ImHereByChance/simple-full-text-search-service.git`.

  2. Создать окружение (на линуксе: `python3.8 -m venv env`) и активировать его.

  3. Установить зависимости из `requirenments.py`: `pip install -r requirements.txt`.

### 2. Конфигурирование.<br />
В приложении два `.yaml` файла с конфигами:
  - дефолтный `source/default_config.yaml` содержит настройки по умолчанию (на данный момент там мои dev настройки);
  - локальный `local_config.yaml`, служит для "перетирания" настроек по умолчанию: если, к примеру, указать в `local_config.yaml` `PORT: 6666`, то приложение стартует на порте 6666, вместо дефолтного 5000 - остальные настройки будут взяты из `default_config.yaml`, если их также не переопределить.<br />
Также необходимо создать и активировать файл с переменными окружения (напр. `touch .vars.sh`), в него положить пароли и др. переменные, которые нужно скрыть. В дефолтном конфиге пароль от базы данных PostgreSQL берется из переменной окружения $DATABASE_PASSWORD, поэтому пароль от него лежит в `.vars.sh`
```
# .vars.sh
export DATABASE_PASSWORD="y0Ur_dAtaBa$e_Pa$$w0rd"
```
```
# local_config.yaml
DATABASE_CONFIG:
    ...
    password: ${DATABASE_PASSWORD}  # модуль pyaml_env позволяет использовать переменные окружения в .yaml
    ...
```

### 3. PostreSQL и Elasticsearch. <br />
В `local_config.yaml` указать данные для подключения к PostreSQL и Elasticsearch:
```
# local_config.yaml
DATABASE_CONFIG:
    user: ...
    password: ...
    host: ...
    port: ...
    database: ...
    
ELASTICSEARCH_CONFIG:
    host: ...
    port: ...
    # и другие данные
```
Создать в PostreSQL пустую базу с указанным в `/local_config.yaml` названием. <br />
Далее можно загрузить данные из тестового `.csv` файла c помощью скрипта `misc/load_data_from_csv.py` <br />
Если Вы не планируете этого делать, то нужно:
  - создать в пустой PostreSQL базе таблицу и индекс, выполнив в ней запросы, описанные в файле `misc/db_schema_setup.sql`;
  - cоздать в Elastisearch индекс с именем `posts`, например с помощью curl: `curl -X PUT "localhost:9200/posts"`. <br />

### Готово.
Запускается через `entry.py`. Можно указать консольные аргументы: 
  - `--host` 
  - `--port`
  - `--reload` (пререзапускать после сохранения изменений в файлах проекта) 
  - `-c` или `--config` (путь до `.yaml` файла с конфигурациями, заменит собой `local_config.yaml`)
