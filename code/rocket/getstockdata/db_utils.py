# coding:utf-8

from typing import List
from pymongo import MongoClient, DESCENDING


class DBUtils(object):
    client = MongoClient(host='localhost', port=27017)
    db = client['stockapp']

    @classmethod
    def save_daily_history(cls, insert_list: List):
        col = cls.db['daily']
        for doc in insert_list:
            col.update_many(
                {'timestamp': doc['timestamp'],
                 'symbol': doc['symbol']},
                {'$set': doc},
                upsert=True
            )

    @classmethod
    def save_realtime(cls, insert_list: List):
        col = cls.db['realtime']
        for doc in insert_list:
            col.update_many(
                {'timestamp': doc['timestamp'],
                 'symbol': doc['symbol']},
                {'$set': doc},
                upsert=True
            )

    @classmethod
    def get_daily_history_symbols(cls):
        return [ele['_id'] for ele in cls.db['daily'].aggregate([{'$group': {'_id': '$symbol'}}, ])]

    @classmethod
    def get_daily_history_by_symbol(cls, symbol: str):
        return list(
            cls.db['daily'].find(filter={'symbol': symbol}, projection={'_id': 0}, sort=[('timestamp', DESCENDING)]))

    @classmethod
    def get_realtime_symbols(cls):
        return [ele['_id'] for ele in cls.db['realtime'].aggregate([{'$group': {'_id': '$symbol'}}, ])]

    @classmethod
    def get_realtime_by_symbol(cls, symbol: str):
        return list(
            cls.db['realtime'].find(filter={'symbol': symbol}, projection={'_id': 0}, sort=[('timestamp', DESCENDING)]))

if __name__ == '__main__':
    from get_data import GetData

    DBUtils.save_daily_history(GetData.get_daily_data('GOOG'))
