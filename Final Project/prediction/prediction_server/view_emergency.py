from flask import jsonify, render_template, request

from prediction.prediction_server import app
from prediction.prediction_server import model_emergency

api_prefix = '/api/v0.1.0/'


@app.route('/StockContent')
def stock_content():
    return render_template('StockContent.html')


@app.route(api_prefix + 'getAllSymbols')
def get_all_symbol():
    return jsonify(model_emergency.get_all_symbol())


@app.route(api_prefix + 'getLeastPrice/<string:symbol>')
def get_least_price(symbol: str):
    return jsonify(float(model_emergency.get_least_price(symbol).to_decimal()))


@app.route(api_prefix + 'getRecentPrice/<string:symbol>/<int:n>')
def get_recent_price(symbol, n):
    res = model_emergency.get_recent_price(symbol, n)

    ret = []
    for row in res:
        ret.append([row['timestamp'].isoformat(), float(row['open'].to_decimal()), float(row['high'].to_decimal()),
                    float(row['low'].to_decimal()), float(row['close'].to_decimal()), row['volume']])

    return jsonify(ret)


@app.route(api_prefix + 'getRealtimePrice/<string:symbol>/<int:n>')
def get_realtime_price(symbol, n):
    res = model_emergency.get_realtime_price(symbol, n)
    ret = []
    for row in res:
        ret.append([row['timestamp'].isoformat(), float(row['price'].to_decimal()), row['volume']])

    return jsonify(ret)


@app.route(api_prefix + 'getMax/<string:symbol>')
def get_max(symbol: str):
    return jsonify(float(model_emergency.get_max(symbol)))


@app.route(api_prefix + 'getMin/<string:symbol>')
def get_min(symbol: str):
    return jsonify(float(model_emergency.get_min(symbol)))


@app.route(api_prefix + 'getAvg/<string:symbol>')
def get_avg(symbol: str):
    return jsonify(float(model_emergency.get_avg(symbol)))


@app.route(api_prefix + 'getLowerAvg/<string:symbol>')
def get_lower_avg(symbol: str):
    return jsonify(model_emergency.get_lower_avg(symbol))


@app.route(api_prefix + 'stockresource/comment/<string:symbol>', methods=['GET', ])
def get_commit(symbol: str):
    return jsonify(model_emergency.get_comment(symbol))


@app.route(api_prefix + 'stockresource/comment', methods=['POST', ])
def add_commit():
    model_emergency.add_comment(request.form['symbol'], request.form['comment'], request.form['timestamp'],
                                request.form['username'])
    return ''
