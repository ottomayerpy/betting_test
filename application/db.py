import base64
import json

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import PG_USER, PG_PASSWORD, PG_DB, PG_HOST, PG_PORT

# Url для подключения к postgres
url = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'

db = create_engine(url)
base = declarative_base()


class Query(base):
    """ Запросы """
    __tablename__ = 'query'

    id = Column(Integer, primary_key=True)
    key = Column(String)  # Ключ
    body = Column(String)  # Тело запроса


Session = sessionmaker(db)
session = Session()

# Создаем таблицу
base.metadata.create_all(db)


def query_add(body: bytes) -> str:
    """ Сохранить запрос """
    data = load_body_and_encode_key(body)
    if 'Error' in data:
        # Если ошибка, возвращаем ее описание
        return str(data)
    query = Query(
        key=data['key'],
        body=json.dumps(data['body']),
    )
    session.add(query)
    session.commit()
    return f"Ключ запроса: {data['key']}"


def get_query(key: str) -> dict:
    """ Вернуть/Получить запрос """
    query = get_queries(key)
    if query is None:
        return {
            'duplicates': None,
            'body': None,
        }
    statistic = get_count_duplicates(key)
    return {
        'duplicates': statistic,
        'body': json.loads(query.body),
    }


def query_remove(key: str) -> str:
    """ Удалить запрос """
    query = get_queries(key)
    if query is None:
        return f'Запрос {key} не найден!'
    session.delete(query)
    session.commit()
    return f'Запрос {key} удален!'


def query_update(key: str, body: bytes) -> str:
    """ Обновить запрос """
    query = get_queries(key)
    if query is None:
        return f'Запрос {key} не найден!'
    data = load_body_and_encode_key(body)
    if 'Error' in data:
        return str(data)
    query.key = data['key']
    query.body = json.dumps(data['body'])
    session.commit()
    return f"Новый ключ: {data['key']}"


def get_statistic() -> str:
    """ Вернуть/Получить процент повторяющихся
    запросов относительно всех запросов """
    queries = session.query(Query)
    # Составляем список из ключей запросов
    keys_queries = [i.key for i in queries]
    # Составляем словарь из ключей запросов и количества их повторений
    dict_repeat_queries = {i: keys_queries.count(i) for i in keys_queries}
    repeat_counter = 0  # Счетчик повторений
    # Считаем сколько всего было повторений
    for value in dict_repeat_queries.values():
        if value > 1:
            repeat_counter += value - 1
    # Считаем процент повторений запросов
    percent_repeats = 100*repeat_counter/queries.count()
    return f"Процент дубликатов: {round(percent_repeats)}%"


def get_count_duplicates(key: str) -> int:
    """ Получить количество дубликатов для одного запроса """
    queries = session.query(Query).filter(Query.key == key)
    query_count = queries.count()
    return query_count - 1


def get_queries(key: str):
    """ Получить запрос(ы) """
    queries = session.query(Query)
    for query in queries:
        if query.key == key:
            return query


def load_body_and_encode_key(body: bytes) -> dict:
    """ Десериализация тела запроса и кодирование ключа в base64 """
    try:
        data = json.loads(body)['body']
        key = base64.b64encode(
            bytes(
                data['key'] + data['value'],
                'utf-8'
            )
        ).decode('utf-8')
        return {
            'key': key,
            'body': data,
        }
    except json.decoder.JSONDecodeError as e:
        return {
            'Error': 'JSONDecodeError',
            'Description': e
        }
    except KeyError as e:
        return {
            'Error': 'KeyError',
            'Description': f'{e} not found'
        }
