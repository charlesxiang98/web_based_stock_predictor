# coding:utf-8

import json
from typing import List, Union

import arrow
import requests
from bson.decimal128 import Decimal128
from bson.errors import BSONError
from bson.int64 import Int64
from read_file import get_api_key


class GetData(object):
    URL = 'https://www.alphavantage.co/query'

    @staticmethod
    def get_daily_data(symbol: Union[str, List[str]]):
        if not symbol:
            raise ValueError

        if isinstance(symbol, str):
            symbol = [symbol, ]

        ret_list = []
        for s in symbol:
            res = requests.get(GetData.URL,
                               params={
                                   'function': 'TIME_SERIES_DAILY',
                                   'symbol': s,
                                   'outputsize': 'compact',  # full, compact
                                   'apikey': get_api_key()
                               })

            j = res.json()  # type: dict
            if 'Time Series (Daily)' in j:
                tz = j['Meta Data']['5. Time Zone']
                for d, info in j['Time Series (Daily)'].items():
                    tmp_dict = {'timestamp': arrow.get(d).datetime,
                                'symbol': s,
                                'open': Decimal128(info['1. open']),
                                'high': Decimal128(info['2. high']),
                                'low': Decimal128(info['3. low']),
                                'close': Decimal128(info['4. close'])}
                    try:
                        tmp_dict['volume'] = Int64(info['5. volume'])
                    except (BSONError, ValueError):
                        tmp_dict['volume'] = Int64(0)
                    ret_list.append(tmp_dict)
            else:
                print(arrow.utcnow().isoformat())
                print(json.dumps(j, indent=1))
        return ret_list

    @staticmethod
    def get_real_time_price(symbol: Union[str, List[str]] = None):
        if symbol is None:
            return []
        if isinstance(symbol, str):
            symbol = [symbol, ]

        res = requests.get(GetData.URL,
                           params={
                               'function': 'BATCH_STOCK_QUOTES',
                               'symbols': ','.join(symbol),
                               'apikey': get_api_key()
                           })
        j = res.json()  #type: dict
        ret_list = []
        if 'Stock Quotes' in j:
            tz = j['Meta Data']['3. Time Zone']

            for info in j['Stock Quotes']:
                tmp_dict = {'timestamp': arrow.get(info['4. timestamp']).replace(tzinfo=tz).datetime,
                            'symbol': info['1. symbol'],
                            'price': Decimal128(info['2. price'])}
                try:
                    tmp_dict['volume'] = Int64(info['3. volume'])
                except (BSONError, ValueError):
                    tmp_dict['volume'] = Int64(0)
                ret_list.append(tmp_dict)
        else:
            print(arrow.utcnow().isoformat())
            print(json.dumps(j, indent=1))
        return ret_list


if __name__ == '__main__':
    print(GetData.get_real_time_price(['GOOG', 'AABA', 'FB', 'MSFT', 'TWTR', 'AAPL', 'JPM', 'AMZN', 'JNJ', 'BAC']))
