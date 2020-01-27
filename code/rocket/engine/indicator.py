'''
@author: Ruiyu Zhang
@create: 2019.04.29
@intro.: Stocks indicators
'''

import numpy as np
from alpha_vantage.techindicators import TechIndicators
import json
#from env import Env
from rocket.engine.env import Env
from time import sleep

class Indicator: # deprecated

    @staticmethod
    def EMA(val: np.ndarray) -> np.float_:
        '''
        Exponential Moving Average (指数移动平均)
        https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
        '''

        if val.size < 10: return np.float_(-1)
        ret = sum(val[:10]) / 10
        multiplier = 2 / (10 + 1)
        for v in val[10:]:
            ret = (v - ret) * multiplier + ret
        return ret

    @staticmethod
    def VR(price: np.float_, historical_price: np.ndarray, historical_volume: np.ndarray) -> np.float_:
        '''
        Volatility Ratio (成交量变异率)
        https://www.investopedia.com/terms/v/volatility-ratio.asp
        https://baike.baidu.com/item/VR%E6%8C%87%E6%A0%87
        '''

        A = np.sum(historical_volume[np.where(price > historical_price)])
        D = np.sum(historical_volume[np.where(price < historical_price)])
        U = np.sum(historical_volume[np.where(price == historical_price)])
        return np.float_((A + U / 2) / (A + D + U))

    @staticmethod
    def MACD(val12: np.ndarray, val26: np.ndarray) -> np.float_:
        '''
        Moving Average Convergence / Divergence (指数平滑异同移动平均线)
        https://zh.wikipedia.org/wiki/MACD
        '''

        return Indicator.EMA(val12) - Indicator.EMA(val26)

class AlphaVantageIndicators:
    '''
    enables alpha_vantage for indicator calculation
    important: frequent requests may result in temp-ban of api
    input eg.: "GOOG"
    output type: json str
    基本用不上
    '''


    @staticmethod
    def ROC(stock_name):
        '''
        Price Rate of Change (变动率指标)
        https://baike.baidu.com/item/ROC%E6%8C%87%E6%A0%87
        https://en.wikipedia.org/wiki/Momentum_(technical_analysis)
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_roc(symbol=stock_name, interval='daily', time_period=60, series_type='close')
        #data.to_csv(stock_name + '_ROC indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def EMA(stock_name):
        '''
        Exponential Moving Average (指数移动平均)
        https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_ema(symbol=stock_name, interval='daily', series_type='close')
        # data.to_csv(stock_name + '_EMA indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def OBV(stock_name):
        '''
        On-balance Volume (能量潮)
        https://en.wikipedia.org/wiki/On-balance_volume
        https://baike.baidu.com/item/%E8%83%BD%E9%87%8F%E6%BD%AE/10168521
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_obv(symbol=stock_name, interval='daily')
        # data.to_csv(stock_name + '_OBV indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')


    @staticmethod
    def MACD(stock_name):
        '''
        Moving Average Convergence / Divergence (指数平滑异同移动平均线)
        https://zh.wikipedia.org/wiki/MACD
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_macd(symbol=stock_name, interval='daily', series_type='close')
        #data.to_csv(stock_name + '_MACD indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def stoch(stock_name):
        '''
        Stochastic Oscillator (随机指标)
        https://en.wikipedia.org/wiki/Stochastic_oscillator
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_stoch(symbol=stock_name, interval='daily')
        # data.to_csv(stock_name + '_stoch indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def RSI(stock_name):
        '''
        Relative Strength Index (相对强弱指数)
        https://en.wikipedia.org/wiki/Relative_strength_index
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_rsi(symbol=stock_name, interval='daily', series_type='close', time_period='60')
        # data.to_csv(stock_name + '_RSI indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def CCI(stock_name):
        '''
        Commodity Channel Index (顺势指标)
        https://en.wikipedia.org/wiki/Commodity_channel_index
        https://baike.baidu.com/item/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87/976711
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')
        data, meta_data = ti.get_cci(symbol=stock_name, interval='daily', time_period=60)
        # data.to_csv(stock_name + '_CCI indicator.csv', index=True, sep=',')
        return data.to_json(orient='split')

    @staticmethod
    def save_all_indicators(stock_name):
        '''
        Saves everything to local .csv files with corresponding name
        @DEV NOTE: can only process any 5 of them, the other 2 will encounter unexpected error
        :param stock_name:
        :return: None
        '''

        ti = TechIndicators(key=Env.alpha_vantage_api_key, output_format='pandas')

        d, _ = ti.get_cci(symbol=stock_name, interval='daily', time_period=60)
        d.to_csv(stock_name + '_CCI.csv', index=True, sep=',')

        d, _ = ti.get_rsi(symbol=stock_name, interval='daily', series_type='close', time_period='60')
        d.to_csv(stock_name + '_RSI.csv', index=True, sep=',')

        d, _ = ti.get_stoch(symbol=stock_name, interval='daily')
        d.to_csv(stock_name + '_stoch.csv', index=True, sep=',')

        d, _ = ti.get_macd(symbol=stock_name, interval='daily', series_type='close')
        d.to_csv(stock_name + '_MACD.csv', index=True, sep=',')

        d, _ = ti.get_obv(symbol=stock_name, interval='daily')
        d.to_csv(stock_name + '_OBV.csv', index=True, sep=',')

        d, _ = ti.get_ema(symbol=stock_name, interval='daily', series_type='close')
        d.to_csv(stock_name + '_EMA.csv', index=True, sep=',')

        d, _ = ti.get_roc(symbol=stock_name, interval='daily', time_period=60, series_type='close')
        d.to_csv(stock_name + '_ROC.csv', index=True, sep=',')



if __name__ == "__main__":
    #print(AlphaVantageIndicators.ROC("GOOG"))
    #print(AlphaVantageIndicators.EMA("GOOG"))
    #print(AlphaVantageIndicators.OBV("GOOG"))
    print(AlphaVantageIndicators.MACD("GOOG"))
    #print(AlphaVantageIndicators.stoch("GOOG"))
    #print(AlphaVantageIndicators.RSI("GOOG"))
    #print(AlphaVantageIndicators.MACD("GOOG"))
    #AlphaVantageIndicators.save_all_indicators("GOOG")

    pass