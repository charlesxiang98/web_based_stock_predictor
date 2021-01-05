
import numpy as np

class EMA(object):
    '''
    receive a sequence of prices (num >= 10) as an ndarray, in time order
    return the EMA of it
    '''

    @staticmethod
    def MA(vals: np.ndarray) -> np.float_:
        ret = 0
        for x in vals:
            ret = ret + x
        return ret / len(vals)

    @staticmethod
    def value(vals: np.ndarray) -> np.float_:
        if vals.size < 10:
            return np.float_(-1)
        ret = EMA.MA(vals[0:10])
        vals = vals[10:]
        multiplier = 2 / (10+1)
        for x in vals:
            ret = (x - ret) * multiplier + ret
        return ret

if __name__ == "__main__":
    print(EMA.value(np.asarray([22.27,22.19, 22.08, 22.17, 22.18, 22.13, 22.23, 22.43, 22.24,22.29])))
