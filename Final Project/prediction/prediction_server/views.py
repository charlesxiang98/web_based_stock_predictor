import arrow
import numpy as np
from flask import request, jsonify, render_template

from prediction.prediction_engine.bayes import Bayes
from prediction.prediction_engine.dnn import DNN
from prediction.prediction_engine.ema import EMA
from prediction.prediction_engine.macd import MACD
from prediction.prediction_engine.svr_zhu import SupportVectorRegression
from prediction.prediction_engine.vr import VolatilityRatio
from prediction.prediction_server import app, pool
from prediction.prediction_server.jsonp import jsonp
from prediction.prediction_server.models import checkParameters, getDailyData, \
    checkSymbol, getRealtimeData, checkDate, checkTimestamp
from prediction.prediction_engine.predictor import Predictor



# root_route_mark
@app.route('/')
def index_page():
    # print(url_for(''))
    #return render_template('index.html')
    return render_template('StockContent.html')


@app.route('/api/v0.0.1/test/daily')
def daily_data():
    check_result = checkParameters(
        args=request.args,
        parametersList=['symbol', ],
    )
    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    return jsonify(getDailyData(request.args['symbol'], request.args.get('timestamp', None)))


@app.route('/api/v0.0.1/test/realtime')
def realtime_data():
    check_result = checkParameters(
        args=request.args,
        parametersList=['symbol', ],
    )
    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    return jsonify(getRealtimeData(request.args['symbol']))


@app.route('/api/v0.1.0/vr')
@jsonp
def indicator_vr():
    check_result = checkParameters(
        args=request.args,
        parametersList=['timestamp', 'symbol'],
    )
    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    check_result = checkTimestamp(request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    check_result = checkDate(request.args['symbol'], request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    # timestamp = arrow.get(request.args.get('timestamp', 0))
    # data_list = []

    period = int(request.args.get('period', 24))

    r = getDailyData(request.args['symbol'], request.args['timestamp'], period + 1)

    res = {
        'type': 'result',
        'time': arrow.utcnow().isoformat(),
        'result': {
            'symbol': request.args.get('symbol', 'ERROR'),
            'indicator': 'VR',
            'timestamp': arrow.get(request.args['timestamp']).isoformat(),
            'data': VolatilityRatio.indicator(
                price=np.float_(r['close'][-1]),
                historical_price=np.array(r['close'][:-1]),
                historical_volume=np.array(r['volume'][:-1])
            )
        }
    }

    return jsonify(res)


@app.route('/api/v0.1.0/ema')
@jsonp
def indicator_ema():
    check_result = checkParameters(
        args=request.args,
        parametersList=['timestamp', 'symbol'],
    )
    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    check_result = checkTimestamp(request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    check_result = checkDate(request.args['symbol'], request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    # timestamp = arrow.get(request.args.get('timestamp', 0))
    # data_list = []

    period = int(request.args.get('period', 10))

    r = getDailyData(request.args['symbol'], request.args['timestamp'], period + 1)

    res = {
        'type': 'result',
        'time': arrow.utcnow().isoformat(),
        'result': {
            'symbol': request.args.get('symbol', 'ERROR'),
            'indicator': 'EMA',
            'timestamp': arrow.get(request.args['timestamp']).isoformat(),
            'data': EMA.value(
                vals=np.array(r['close'][:-1])
            )
        }
    }

    return jsonify(res)


@app.route('/api/v0.1.0/macd')
@jsonp
def indicator_macd():
    check_result = checkParameters(
        args=request.args,
        parametersList=['timestamp', 'symbol'],
    )
    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    check_result = checkTimestamp(request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    check_result = checkDate(request.args['symbol'], request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    # timestamp = arrow.get(request.args.get('timestamp', 0))
    # data_list = []

    period_first = 12
    period_second = 26

    r_first = getDailyData(request.args['symbol'], request.args['timestamp'], period_first)
    r_second = getDailyData(request.args['symbol'], request.args['timestamp'], period_second)

    res = {
        'type': 'result',
        'time': arrow.utcnow().isoformat(),
        'result': {
            'symbol': request.args.get('symbol', 'ERROR'),
            'indicator': 'MACD',
            'timestamp': arrow.get(request.args['timestamp']).isoformat(),
            'data': MACD.value(
                val12=np.array(r_first['close'][:-1]),
                val26=np.array(r_second['close'][:-1])
            )
        }
    }

    return jsonify(res)


@app.route('/api/v0.1.0/predict')
@jsonp
def predict():
    # check parameters
    check_result = checkParameters(
        args=request.args,
        parametersList=['symbol', 'term', 'timestamp'],
        parameterOptions={
            'term': ['short', 'long']
        })

    if check_result:
        return jsonify(check_result)

    check_result = checkSymbol(request.args['symbol'])
    if check_result:
        return jsonify(check_result)

    check_result = checkTimestamp(request.args['timestamp'])
    if check_result:
        return jsonify(check_result)

    # request.args.get('timestamp')

    # ------------------------------------
    if request.args['term'] == 'short':
        r = getDailyData(request.args['symbol'], request.args['timestamp'], 50)
        time = np.array(r['timestamp']).reshape(-1, 1)
        price = np.array(r['open'])
    else:
        r = getDailyData(request.args['symbol'], request.args['timestamp'], 252)
        time = np.array(r['timestamp']).reshape(-1, 1)
        price = np.array(r['open'])

    predict_time = arrow.get(request.args['timestamp']).timestamp

    bayes = pool.apply_async(Bayes.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #bayes = Bayes.predict(time, price, np.array(predict_time).reshape(-1, 1))
    svr = pool.apply_async(SupportVectorRegression.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    # svr = SupportVectorRegression.predict(time, price, np.array(predict_time).reshape(-1, 1))
    dnn = pool.apply_async(DNN.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    # dnn = DNN.predict(time, price, np.array(predict_time).reshape(-1, 1))

    #bayes = pool.apply_async(Predictor.bayesian_linear, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #svr = pool.apply_async(Predictor.SVR, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #dnn = pool.apply_async(Predictor.DNN, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    # dnn = svr[0]

    res = {
        'type': 'result',
        'time': arrow.utcnow().isoformat(),
        'result': {
            'symbol': request.args.get('symbol'),
            'predictPrice': (bayes[0] + svr[0] + dnn) / 3,
            'predictor': [
                {'name': 'bayes', 'price': bayes[0]},
                {'name': 'Support Vector Regression', 'price': svr[0]},
                {'name': 'Deep Neural Network', 'price': dnn}
            ],
            'note': 'ONLY FOR TESTING!',
            'timestamp': arrow.get(request.args['timestamp']).isoformat()
        }
    }
    return jsonify(res)
