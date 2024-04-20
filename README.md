# Dvmn-seller-apis
**Обновление цен и информации по остаткам товаров на маркетплейсах Я.Маркет и Озон**

Приложение скачивает информацию по остаткам и ценам на товары с сайта [timeworld.ru](https://timeworld.ru/upload/files/ostatki.zip) и загружает её на маркетплейсы. 

Остатки преобразуются по алгоритму: 
* `>10 -> 100`
* `1 -> 0`
* `остальные количества -> как есть`.

# Данные для авторизации

В корневой директории проекта создайте файл .env и поместите в него переменные в виде `VAR={your_var_here}`.

Для `market.py`:
```
MARKET_TOKEN
FBS_ID
DBS_ID
WAREHOUSE_FBS_ID
WAREHOUSE_DBS_ID
```
Подробнее о требуемых ключах [здесь](https://yandex.ru/dev/market/partner-api/doc/ru/)

Для 'seller.py':
```
SELLER_TOKEN
CLIENT_ID
```
Подробнее о требуемых ключах [здесь](https://docs.ozon.ru/global/api/intro/?country=CN)
