import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id, client_id, seller_token):
    """Получить список товаров магазина озон

    Аргументы:
        last_id (str): ID последнего загруженного товара
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        result (dict): перечень товаров маркетплейса

    Выбрасывает исключения:
        HTTPError

    Примеры:
    Корректное исполнение функции:

        >>> get_product_list(last_id, client_id, seller_token)
        {
            "items": [
              {
                "product_id": 223681945,
                "offer_id": "136748"
              }
            ],
            "total": 1,
            "last_id": "bnVсbA=="
        }

    Некорректное исполнение функции:

        >>> get_product_list(last_id, client_id, seller_token)
        HTTPError: 400 (если указан неверный параметр).
        HTTPError: 403 (если доступ запрещен).
    """

    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def get_offer_ids(client_id, seller_token):
    """Получить артикулы товаров магазина озон

    Аргументы:
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        offer_ids (list): список товаров маркетплейса

    Выбрасывает исключения:
        HTTPError

    Примеры:
    Корректное исполнение функции:

        >>> get_offer_ids(client_id, seller_token)
            ["136748", "123123"]

    Некорректное исполнение функции:

        >>> get_offer_ids(client_id, seller_token)
        HTTPError: 400 (если указан неверный параметр).
        HTTPError: 403 (если доступ запрещен).
    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids


def update_price(prices: list, client_id, seller_token):
    """Обновить цены товаров

    Аргументы:
        prices (list): список цен
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        response.json() (dict): словарь с ответом сервера

    Выбрасывает исключения:
        HTTPError

    Примеры:
    Корректное исполнение функции:

        >>> update_price(prices, client_id, seller_token)
        {
          "result": [
            {
              "product_id": 1386,
              "offer_id": "PH8865",
              "updated": true,
              "errors": []
            }
          ]
        }

    Некорректное исполнение функции:

        >>> update_price(prices, client_id, seller_token)
        HTTPError: 400 (если указан неверный параметр).
        HTTPError: 403 (если доступ запрещен).
    """
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_stocks(stocks: list, client_id, seller_token):
    """Обновить остатки

    Аргументы:
        stocks (list): список остатков
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        response.json() (dict): словарь с ответом сервера

    Выбрасывает исключения:
        HTTPError

    Примеры:
    Корректное исполнение функции:

        >>> update_stocks(stocks, client_id, seller_token)
        {
          "result": [
            {
              "warehouse_id": 22142605386000,
              "product_id": 118597312,
              "offer_id": "PH11042",
              "updated": true,
              "errors": []
            }
          ]
        }

    Некорректное исполнение функции:

        >>> update_stocks(stocks, client_id, seller_token)
        HTTPError: 400 (если указан неверный параметр).
        HTTPError: 403 (если доступ запрещен).
    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def download_stock():
    """Скачать файл ostatki с сайта casio

    Аргументы:
        нет

    Возвращает:
        watch_remnants (list): остатки

    Выбрасывает исключения:
        HTTPError

    Примеры:
    Корректное исполнение функции:

        >>> download_stock()
        [{'Код': '',
          'Наименование товара': 'CASIO Baby-G',
          'Изображение': '',
          'Цена': '',
          'Количество': '',
          'Заказ': ''},
         {'Код': 71301,
          'Наименование товара': 'BA-110BE-4A',
          'Изображение': 'Показать',
          'Цена': "19'990.00 руб.",
          'Количество': 6,
          'Заказ': ''}]

    Некорректное исполнение функции:

        >>> download_stock()
        HTTPError: 400 (если указан неверный параметр).
        HTTPError: 403 (если доступ запрещен).
    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants


def create_stocks(watch_remnants, offer_ids):
    """Создать объект для загрузки остатков на маркетплейс

    Аргументы:
        watch_remnants (list): остатки
        offer_ids (list): перечень товаров

    Возвращает:
        stocks (list): остатки
    """
    # Уберем то, что не загружено в seller
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks


def create_prices(watch_remnants, offer_ids):
    """Создать объект для загрузки цен на маркетплейс

    Аргументы:
        watch_remnants (list): остатки
        offer_ids (list): перечень товаров

    Возвращает:
        prices (list): остатки
    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices


def price_conversion(price: str) -> str:
    """Преобразовать цену. Пример: 5'990.00 руб. -> 5990

    Аргументы:
        price (str): Цена в строковом формате с разделителями разрядов и с указанием валюты

    Возвращает:
        str: Цена в строковом формате без разделителей разрядов и указания валюты

    Примеры:
    Корректное исполнение функции:

        >>> price = "5'990.00 руб."
        >>> price_conversion(price)
        5990

    Некорректное исполнение функции:

        >>> price = 5990
        >>> price_conversion(price)
        ---------------------------------------------------------------------------
        AttributeError                            Traceback (most recent call last)
        Cell In[57], line 1
        ----> 1 price_conversion(price)

        Cell In[52], line 2, in price_conversion(price)
              1 def price_conversion(price):
        ----> 2     return re.sub("[^0-9]", "", price.split(".")[0])

        AttributeError: 'int' object has no attribute 'split'
    """
    return re.sub("[^0-9]", "", price.split(".")[0])


def divide(lst: list, n: int):
    """Разделить список lst на части по n элементов
    Аргументы:
        lst (list): Список, который нужно разделить
        n (int): Количество элементов в каждой части разделённого списка

    Генерирует:
        list: Часть списка

    Примеры:
    Корректное исполнение функции:

        >>> for part in divide([1, 2, 3, 4, 5], 2):
        >>> ... print(part)
        [1, 2]
        [3, 4]
        [5]

    Некорректное исполнение функции:

        >>> for part in divide([1, 2, 3, 4, 5], 0):
        >>> ... print(part)
    ---------------------------------------------------------------------------
    ValueError                                Traceback (most recent call last)
    Cell In[16], line 1
    ----> 1 for part in divide([1,], 0):
          2     print(part)

    Cell In[12], line 17, in divide(lst, n)
          1 def divide(lst: list, n: int):
    ---> 17     for i in range(0, len(lst), n):
         18         yield lst[i : i + n]

    ValueError: range() arg 3 must not be zero
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    """Загрузить цены на маркетплейс

    Аргументы:
        watch_remnants (list): список остатков
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        prices (list): перечень загруженных цен"""
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    """Загрузить остатки на маркетплейс

    Аргументы:
        watch_remnants (list): список остатков
        client_id (str): ID продавца маркетплейса
        seller_token (str): Токен продавца маркетплейса

    Возвращает:
        not_empty (list): перечень товаров с ненулевым остатком
        stocks (list): перечень загруженных остатков"""
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
