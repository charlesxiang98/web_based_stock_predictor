import arrow
from pymongo import DESCENDING

from rocket.server import realtime, daily, comment


def get_recent_price(symbol: str, n: int = 30):
    ret = []
    for row in daily.find({'symbol': symbol}, {'_id': 0, 'symbol': 0}).sort([('timestamp', DESCENDING)]).limit(n):
        ret.append(row)
    return ret


def get_realtime_price(symbol: str, n: int = 30):
    ret = []
    for row in realtime.find({'symbol': symbol}, {'_id': 0, 'symbol': 0}).sort([('timestamp', DESCENDING)]).limit(n):
        ret.append(row)
    return ret


def get_least_price(symbol: str):
    return realtime.find({'symbol': symbol}, {'price': 1, '_id': 0}).sort([('timestamp', DESCENDING)]).limit(1)[0][
        'price']


def get_all_symbol():
    ret = []

    for row in daily.aggregate([{'$group': {'_id': '$symbol'}}, {'$sort': {'_id': 1}}]):
        ret.append(row['_id'])

    return ret


def get_max(symbol: str):
    ret = []

    for row in daily.aggregate([
        {'$match': {'symbol': symbol}},
        {'$sort': {'timestamp': -1}},
        {'$limit': 10},
        {'$group': {'_id': 0, 'max': {'$max': '$high'}}}
    ]):
        ret.append(row['max'].to_decimal())

    return ret[0]


def get_min(symbol: str):
    ret = []

    for row in daily.aggregate([
        {'$match': {'symbol': symbol}},
        {'$sort': {'timestamp': -1}},
        {'$limit': 252},
        {'$group': {'_id': 0, 'min': {'$min': '$low'}}}
    ]):
        ret.append(row['min'].to_decimal())

    return ret[0]


def get_avg(symbol: str):
    ret = []

    for row in daily.aggregate([
        {'$match': {'symbol': symbol}},
        {'$sort': {'timestamp': -1}},
        {'$limit': 252},
        {'$group': {'_id': 0, 'avg': {'$avg': '$close'}}}
    ]):
        ret.append(row['avg'].to_decimal())

    return ret[0]


def get_lower_avg(symbol: str):
    symbols = get_all_symbol()
    min = get_min(symbol)

    ret = []
    for s in symbols:
        if get_avg(s) < min:
            ret.append(s)

    return ret


def get_comment(symbol: str):
    ret = []
    for row in comment.find({'symbol': symbol}, {'_id': 0}).sort([('timestamp', DESCENDING)]).limit(5):
        ret.append(row)

    return {'comment': ret}


def add_comment(symbol: str, comment_: str, timestamp: str, username: str):
    comment.insert({
        'symbol': symbol,
        'comment': comment_,
        'timestamp': arrow.utcnow().isoformat(),
        'username': username
    })
    # print(symbol, ', ', comment, ', ', timestamp, ', ', username)
