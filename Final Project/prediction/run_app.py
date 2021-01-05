from prediction.prediction_server import app

if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=5001, threaded=True)
