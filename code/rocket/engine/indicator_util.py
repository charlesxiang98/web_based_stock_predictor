from alpha_vantage.techindicators import TechIndicators
from rocket.engine.env import Env

# all_symbols = ["AABA", "AMZN", "BAC", "C", "GOOG", "JPM", "MSFT", "NFLX", "TWTR"]


def indicator_db_init():
    global indicator_data
    global ti
    indicator_data = {}
    ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')


def get_ema(symbol, timestamp):
    if not symbol or not timestamp:
        return 0
    if not indicator_data:
        indicator_db_init()
    if symbol not in indicator_data:
        ema_data, _ = ti.get_ema(symbol=symbol, interval='daily', series_type='close')
        macd_data, _ = ti.get_macd(symbol=symbol, interval='daily', series_type='close')

        indicator_data[symbol] = {
            'EMA': ema_data,
            'MACD': macd_data
        }
    return indicator_data[symbol]['EMA']['EMA'].loc[timestamp[:10]]


def get_macd(symbol, timestamp):
    if not symbol or not timestamp:
        return 0
    if not indicator_data:
        indicator_db_init()
    if symbol not in indicator_data:
        ema_data, = ti.get_ema(symbol=symbol, interval='daily', series_type='close')
        macd_data, _ = ti.get_macd(symbol=symbol, interval='daily', series_type='close')

        indicator_data[symbol] = {
            'EMA': ema_data,
            'MACD': macd_data
        }
    return indicator_data[symbol]['MACD']['MACD'].loc[timestamp[:10]]

