# coding:utf-8
from typing import Union, List

import arrow
import requests
from bson.decimal128 import Decimal128
from bson.int64 import Int64
from pymongo import MongoClient, DESCENDING
import time
from read_file import get_api_key


def get_daily_data(symbol: Union[str, List[str]]):
    if not symbol:
        raise ValueError

    if isinstance(symbol, str):
        symbol = [symbol, ]

    url = 'https://www.alphavantage.co/query'
    if not symbol:
        raise ValueError

    if isinstance(symbol, str):
        symbol = [symbol, ]

    ret_list = []
    for s in symbol:
        res = requests.get(url,
                           params={
                               'function': 'TIME_SERIES_DAILY',
                               'symbol': s,
                               'outputsize': 'full',  # full, compact
                               'apikey': get_api_key()
                           })
        time.sleep(13)

        j = res.json()
        print(j)
        for d, info in j['Time Series (Daily)'].items():
            tmp_dict = {'timestamp': arrow.get(d).datetime,
                        'symbol': s,
                        'open': Decimal128(info['1. open']),
                        'high': Decimal128(info['2. high']),
                        'low': Decimal128(info['3. low']),
                        'close': Decimal128(info['4. close']),
                        'volume': Int64(info['5. volume'])}
            ret_list.append(tmp_dict)
    return ret_list



def DB_init(symbols: Union[str, List[str]]):
    client = MongoClient(host='localhost', port=27017)
    db = client['stockapp']

    if db['flag'].find({'init': True}).count() != 0:
        return

    db['daily'].drop()
    db['realtime'].drop()
    db['flag'].drop()

    db.create_collection('daily', validator={'$jsonSchema': {
        'bsonType': 'object',
        'required': ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume'],
        'properties': {
            'timestamp': {
                'bsonType': 'date',
                'description': 'all time points are in UTC, please convert to local timezone before use'
            },
            'symbol': {
                'bsonType': 'string'
            },
            'open': {
                'bsonType': 'decimal'
            },
            'high': {
                'bsonType': 'decimal'
            },
            'low': {
                'bsonType': 'decimal'
            },
            'close': {
                'bsonType': 'decimal'
            },
            'volume': {
                'bsonType': 'long'
            }
        }
    }})
    db.create_collection('realtime', validator={'$jsonSchema': {
        'bsonType': 'object',
        'required': ['timestamp', 'symbol', 'price', 'volume'],
        'properties': {
            'timestamp': {
                'bsonType': 'date',
                'description': 'all time points are in UTC, please convert to local timezone before use'
            },
            'symbol': {
                'bsonType': 'string'
            },
            'price': {
                'bsonType': 'decimal'
            },
            'volume': {
                'bsonType': 'long'
            }
        }
    }})

    db['daily'].create_index([('timestamp', DESCENDING), ('symbol', DESCENDING)], unique=True, background=True)
    db['daily'].create_index([('symbol', DESCENDING), ('timestamp', DESCENDING)], unique=True, background=True)
    db['realtime'].create_index([('timestamp', DESCENDING), ('symbol', DESCENDING)], unique=True, background=True)
    db['realtime'].create_index([('symbol', DESCENDING), ('timestamp', DESCENDING)], unique=True, background=True)

    for stock in symbols:
        print(stock)
        db['daily'].insert_many(get_daily_data(stock))
    db['flag'].insert_one({'init': True})


if __name__ == '__main__':
    DB_init(['GOOG', 'AABA', 'FB', 'MSFT', 'TWTR', 'AAPL', 'JPM', 'AMZN', 'JNJ', 'BAC'])
