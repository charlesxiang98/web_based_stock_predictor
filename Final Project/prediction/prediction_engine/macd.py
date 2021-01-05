
import numpy as np
from prediction_engine.ema import EMA

class MACD(object):

    @staticmethod
    def value(val12: np.ndarray, val26: np.ndarray) -> np.float_:
        return EMA.value(val12) - EMA.value(val26)