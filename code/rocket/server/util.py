from typing import List, Dict, Union

import arrow
from pymongo import DESCENDING
from werkzeug.datastructures import ImmutableMultiDict

from rocket.server import daily, realtime
from rocket.server import error_code


def checkDate(symbol: str, timestamp: str):
    t = arrow.get(timestamp).replace(tzinfo='+0000').floor('day')

    if daily.find({'symbol': symbol, 'timestamp': t.datetime}).count() <= 0:
        return {
            'type': 'error',
            'time': arrow.utcnow().isoformat(),
            'error': {
                'errorCode': error_code.ERROR_CODE_NOT_ON_THE_TRADING_DAY,
                'errorInfo': 'Not on the trading day'
            }
        }
    else:
        return None


def checkTimestamp(timestamp: str):
    try:
        arrow.get(timestamp)
    except:
        return {
            'type': 'error',
            'time': arrow.utcnow().isoformat(),
            'error': {
                'errorCode': 103,
                'errorInfo': 'please use ISO8601 format'
            }
        }


def checkParameters(
        args: ImmutableMultiDict,
        parametersList: List[str],
        parameterOptions: Dict[str, List[str]] = None):
    if parameterOptions is None:
        parameterOptions = {}

    missing_parameter = []
    for parameter in parametersList:
        if parameter not in args:
            missing_parameter.append(parameter)
    if missing_parameter:
        return {
            'type': 'error',
            'time': arrow.utcnow().isoformat(),
            'error': {
                'errorCode': error_code.ERROR_CODE_MISSING_PARAMETERS,
                'errorInfo': 'Missing parameters',
                'missingParameters': missing_parameter
            }
        }

    invalid_parameter = []
    for k, v in parameterOptions.items():
        if args.get(k) not in v:
            invalid_parameter.append(k)
    if invalid_parameter:
        return {
            'type': 'error',
            'time': arrow.utcnow().isoformat(),
            'error': {
                'errorCode': error_code.ERROR_CODE_INVALID_PARAMETERS,
                'errorInfo': 'Invalid parameter value',
                'invalidParameters': invalid_parameter
            }
        }

    return None


def checkSymbol(symbol: str):
    if symbol not in [ele['_id'] for ele in daily.aggregate([{"$group": {"_id": "$symbol"}}])]:
        return {
            'type': 'error',
            'time': arrow.utcnow().isoformat(),
            'error': {
                'errorCode': error_code.ERROR_CODE_INVALID_SYMBOL,
                'errorInfo': 'Invalid symbol'
            }
        }
    return None


def getDailyData(symbol: str, timestamp: str = None, n: int = 50) -> Dict[str, List[Union[float, int]]]:
    query = {
        'symbol': symbol
    }
    if timestamp:
        query['timestamp'] = {'$lte': arrow.get(timestamp).datetime}

    timestamp_ = []
    open_ = []
    close = []
    high = []
    low = []
    volume = []

    for row in daily.find(query, {'_id': 0.0}).sort(
            [('timestamp', DESCENDING), ]).limit(n):
        timestamp_.append(row['timestamp'].timestamp())
        open_.append(float(row['open'].to_decimal()))
        close.append(float(row['close'].to_decimal()))
        high.append(float(row['high'].to_decimal()))
        low.append(float(row['low'].to_decimal()))
        volume.append(row['volume'])

    return {
        'timestamp': timestamp_[::-1],
        'open': open_[::-1],
        'close': close[::-1],
        'high': high[::-1],
        'low': low[::-1],
        'volume': volume[::-1]
    }


def getRealtimeData(symbol: str, timestamp: str = None, n: int = 50) -> Dict[str, List[Union[float, int]]]:
    query = {
        'symbol': symbol
    }
    if timestamp:
        query['timestamp'] = {'$lte': arrow.get(timestamp).datetime}

    timestamp_ = []
    price = []
    volume = []

    for row in realtime.find(query, {'_id': 0.0}).sort(
            [('timestamp', DESCENDING), ]).limit(n):
        timestamp_.append(row['timestamp'].timestamp())
        price.append(float(row['price'].to_decimal()))
        volume.append(row['volume'])

    return {
        'timestamp': timestamp_[::-1],
        'price': price[::-1],
        'volume': volume[::-1]
    }
