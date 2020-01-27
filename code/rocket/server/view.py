import arrow
import numpy as np
from flask import request, jsonify, render_template

from rocket.server import app, pool
from rocket.server.jsonp import jsonp
from rocket.server.util import checkParameters, getDailyData, \
    checkSymbol, getRealtimeData, checkDate, checkTimestamp
from rocket.engine.predictor import Predictor
import rocket.engine.indicator_util as idut
from rocket.engine.indicator import Indicator



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
            'data': Indicator.VR(
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
            'data': idut.get_ema(request.args['symbol'], request.args['timestamp'])
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
            'data': idut.get_macd(request.args['symbol'], request.args['timestamp'])
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

    if request.args['term'] == 'short':
        r = getDailyData(request.args['symbol'], request.args['timestamp'], 50)
        time = np.array(r['timestamp']).reshape(-1, 1)
        price = np.array(r['open'])
    else:
        r = getDailyData(request.args['symbol'], request.args['timestamp'], 252)
        time = np.array(r['timestamp']).reshape(-1, 1)
        price = np.array(r['open'])

    predict_time = arrow.get(request.args['timestamp']).timestamp

    #bayes = pool.apply_async(Bayes.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #bayes = Bayes.predict(time, price, np.array(predict_time).reshape(-1, 1))
    #svr = pool.apply_async(SupportVectorRegression.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #svr = SupportVectorRegression.predict(time, price, np.array(predict_time).reshape(-1, 1))
    #dnn = pool.apply_async(DNN.predict, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    #dnn = DNN.predict(time, price, np.array(predict_time).reshape(-1, 1))

    bayes = pool.apply_async(Predictor.bayesian_ridge, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    svr = pool.apply_async(Predictor.SVR, [time, price, np.array(predict_time).reshape(-1, 1)]).get()
    dnn = pool.apply_async(Predictor.DNN, [time, price, np.array(predict_time).reshape(-1, 1)]).get()

    #ans = (bayes[0] + svr[0]) / 2 if bayes[0] < 0 else (bayes[0] + svr[0] + dnn[0]) / 3

    bayes[0] = (svr[0] + dnn[0]) if bayes[0] < 0 else bayes[0]
    if request.args['term'] == 'short':
        ans = 0.1 * bayes[0] + 0.7 * svr[0] + 0.2 * dnn[0]
    elif request.args['term'] == 'long':
        ans = 0.1 * bayes[0] + 0.2 * svr[0] + 0.7 * dnn[0]
    else:
        ans = 0

    res = {
        'type': 'result',
        'time': arrow.utcnow().isoformat(),
        'result': {
            'symbol': request.args.get('symbol'),
            'predictPrice': ans,
            'predictor': [
                {'name': 'bayes', 'price': bayes[0]},
                {'name': 'Support Vector Regression', 'price': svr[0]},
                {'name': 'Deep Neural Network', 'price': dnn[0]}
            ],
            'note': 'ONLY FOR TESTING!',
            'timestamp': arrow.get(request.args['timestamp']).isoformat()
        }
    }
    return jsonify(res)
