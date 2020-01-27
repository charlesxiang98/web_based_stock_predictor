import os
from random import sample, randint, uniform
import numpy as np
import tensorflow as tf
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.linear_model import BayesianRidge, LinearRegression


class Predictor:
    '''
    collection of predictors
    all predictor input x&y shape: (-1, 1), dtype = float
    '''

    @staticmethod
    def bayesian_linear(train_x: np.ndarray, train_y: np.ndarray, pred_x: np.ndarray):
        '''predicts with Bayesian Linear Regression (sklearn.linear_model.LinearRegression()'''

        train_y = np.ravel(train_y, order='C')  # fix input shape

        def calculate_score(feature_deg, train_x, train_y):
            '''constructs pipeline under Bayesian model and evaluates score.'''
            pipe = make_pipeline(
                StandardScaler(),
                PolynomialFeatures(feature_deg),  # feature_deg: 多项式的度
                LinearRegression()
            )
            pipe.fit(train_x, train_y)
            return pipe.score(train_x, train_y)

        record = -1  # best score
        best_deg = -1  # degree to gain best score
        deg_range = 4  # degree range for testing

        """ # Not needed, best_deg always= deg_range
        # find the best degree for PolynomialFeatures
        for deg in range(1, deg_range):
            score = calculate_score(deg, train_x, train_y)
            if score > record:
                record = score
                best_deg = deg
        """
        best_deg = deg_range - 1
        # build model, train with best deg, and predict
        pipe = make_pipeline(
            StandardScaler(),
            PolynomialFeatures(best_deg),
            LinearRegression()
        )
        pipe.fit(train_x, train_y)

        print(pipe.predict(pred_x))

        return pipe.predict(pred_x)

    @staticmethod
    def bayesian_ridge(train_x: np.ndarray, train_y: np.ndarray, pred_x: np.ndarray):
        '''predicts with Bayesian Regression (sklearn.linear_model.BayesianRidge()'''

        train_y = np.ravel(train_y, order='C')  # fix input shape

        def calculate_score(feature_deg, train_x, train_y):
            '''constructs pipeline under Bayesian model and evaluates score.'''
            pipe = make_pipeline(
                StandardScaler(),
                PolynomialFeatures(feature_deg),  # feature_deg: 多项式的度
                BayesianRidge()
            )
            pipe.fit(train_x, train_y)
            return pipe.score(train_x, train_y)

        record = -1  # best score
        best_deg = -1  # degree to gain best score
        deg_range = 4  # degree range for testing

        """ # Not needed, best_deg always= deg_range
        # find the best degree for PolynomialFeatures
        for deg in range(1, deg_range):
            score = calculate_score(deg, train_x, train_y)
            if score > record:
                record = score
                best_deg = deg
        """
        best_deg = deg_range - 1
        # build model, train with best deg, and predict
        pipe = make_pipeline(
            StandardScaler(),
            PolynomialFeatures(best_deg),
            BayesianRidge()
        )
        pipe.fit(train_x, train_y)
        return pipe.predict(pred_x)

    @staticmethod
    def SVR(train_x: np.ndarray, train_y: np.ndarray, pred_x: np.ndarray):
        '''predicts with SVM based Regression (sklearn.svm.SVR())'''
        '''DEV NOTE: 数据多时(>200)效率极低'''

        train_y = np.ravel(train_y, order='C')  # fix input shape

        # build model
        pipe = make_pipeline(
            StandardScaler(),
            SVR()
        )

        # train with auto-var grad search
        model = GridSearchCV(
            pipe,
            param_grid={
                'svr__gamma': np.logspace(-2, 2, 5),
                'svr__C': [1e0, 1e1, 1e2]#, 1e3]
            },
            n_jobs=os.cpu_count(),
            cv=(train_x.shape[0] // 10),
            verbose=0
        )

        # predict
        model.fit(train_x, train_y)
        return model.predict(pred_x)

    @staticmethod
    def DNN(train_x: np.ndarray, train_y: np.ndarray, pred_x: np.ndarray):
        '''predicts with TensorFlow based Neural Network (DNNRegressor.Estimator())'''
        '''DEV NOTE: 效率受数据量影响较小，准确性&数据量呈正相关'''

        train_y = np.ravel(train_y, order='C')  # fix input shape

        STEPS = 800  # training steps
        PRICE_NORM_FACTOR = 10  # for normalization
        SECONDS_OF_ONE_DAY = 86400
        SHUFFLE_TIMES = 100  # shuffle multiple times (likely > dataset size) to ensure adequate mixture
        DEBUG = 0  # debug mode flag

        if not DEBUG:  # mute various warnings
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # mute CPU AVX warning
            tf.logging.set_verbosity(tf.logging.ERROR)  # mute warnings from tf

        # preprocess
        pred_x = (train_x[0] - pred_x) / SECONDS_OF_ONE_DAY
        train_x = (train_x[0] - train_x) / SECONDS_OF_ONE_DAY

        trainset_ratio = 0.7
        l1 = sample(list(range(train_x.shape[0])), int(len(train_x) * trainset_ratio))
        x_trainset = train_x[l1]
        y_trainset = train_y[l1]
        l2 = list(set(list(range(train_x.shape[0]))) - set(l1))
        x_testset = train_x[l2]
        y_testset = train_y[l2]

        x_train_dist = {"time": x_trainset}
        x_test_dist = {"time": x_testset}
        x_dist = {"time": pred_x}

        train = tf.data.Dataset.from_tensor_slices((dict(x_train_dist), y_trainset))
        test = tf.data.Dataset.from_tensor_slices((dict(x_test_dist), y_testset))
        to_predict_x = tf.data.Dataset.from_tensor_slices(dict(x_dist))

        def normalize_price(features, labels):
            return features, labels / PRICE_NORM_FACTOR

        train = train.map(normalize_price)
        test = test.map(normalize_price)

        # build training and evaluation input_functions
        def input_train():
            return (train.shuffle(SHUFFLE_TIMES).batch(128)  # shuffle
                    .repeat().make_one_shot_iterator().get_next())  # Repeat forever

        def input_test():
            return (test.shuffle(SHUFFLE_TIMES).batch(128)
                    .make_one_shot_iterator().get_next())

        def pred_fn():
            return to_predict_x.make_one_shot_iterator().get_next()

        # build Neural Network model
        model = tf.estimator.DNNRegressor(
            hidden_units=[20, 20],
            feature_columns=[tf.feature_column.numeric_column(key="time")],
            optimizer=tf.train.ProximalAdagradOptimizer(
                learning_rate=0.3,
                l1_regularization_strength=0.001
            )
        )

        # train
        model.train(input_fn=input_train, steps=STEPS)
        prediction = model.predict(input_fn=pred_fn)
        pred_list = list(prediction)

        # evaluate
        eval_res = model.evaluate(input_fn=input_test)
        ave_loss = eval_res["average_loss"]

        # debug
        if DEBUG:
            print(pred_list[0]['predictions'][0] * PRICE_NORM_FACTOR)
            print("\nRMS err on testset: {:.0f}".format(PRICE_NORM_FACTOR * ave_loss ** 0.5),
                  end="\n")
            print(80 * "_")
            print(pred_list)

        return np.array([pred['predictions'][0] * PRICE_NORM_FACTOR for pred in pred_list])


if __name__ == "__main__":
    '''driver codes as sample & debugger'''
    # preparation
    # tf.logging.set_verbosity(tf.logging.INFO) # setup tf logs

    '''
    # mock data
    import random
    print('_' * 80)
    print('RUNNING MOCK DATA\n')
    # generate test data
    history_size = 300
    predict_size = 5
    train_x = np.array([float(i) for i in range(history_size)]).reshape(-1, 1)
    train_y = np.array([float(i) * 10 + uniform(0., 9.) for i in range(history_size)]).reshape(-1, 1)
    pred_x = np.array([float(i) for i in range(history_size, history_size + predict_size)]).reshape(-1, 1)
    if history_size < 100:
        print(train_x.reshape(1, -1))
        print(train_y.reshape(1, -1))
    print(pred_x.reshape(1, -1))
    # predict
    print("\nBAYES:")
    print(Predictor.bayesian(train_x, train_y, pred_x))
    print("\nSVR:")
    print(Predictor.SVR(train_x, train_y, pred_x))
    print("\nDNN:")
    print(Predictor.DNN(train_x, train_y, pred_x))
    '''

    # real data
    #from datetime import datetime
    #from get_stock_data import get_formated_daily_prices
#
    #print('_' * 80)
    #print('RUNNING REAL DATA\n')
#
    ## fetch data
    #whole_data = get_formated_daily_prices('GOOG')
    #print("dataset size = ", len(whole_data))
    #cur_timestamp = datetime.now().timestamp()
    #SECONDS_OF_ONE_DAY = 86400
    #predict_size = 20
    #train_x = []
    #train_y = []
    #pred_x = np.array(
    #    [cur_timestamp + i * SECONDS_OF_ONE_DAY for i in range(predict_size)]
    #).reshape(-1, 1)  # timestamps of the following 'predict_size' days
    #for row in whole_data:
    #    train_x.append(row[0])
    #    train_y.append(row[1])
    #train_x = np.array(train_x).reshape(-1, 1)
    #train_y = np.array(train_y).reshape(-1, 1)
#
    ## print(train_x)
    ## print(pred_x)
#
    ## predict
    #print("\nBAYESIAN LINEAR:")
    #bayes_l_ans = Predictor.bayesian_linear(train_x, train_y, pred_x)
    #print(bayes_l_ans)
#
    #print("\nBAYESIAN RIDGE:")
    #bayes_r_ans = Predictor.bayesian_ridge(train_x, train_y, pred_x)
    #print(bayes_r_ans)
#
    #print("\nSVR:")
    #SVR_ans = Predictor.SVR(train_x, train_y, pred_x)
    #print(SVR_ans)
#
    #print("\nDNN:")
    #DNN_ans = Predictor.DNN(train_x, train_y, pred_x)
    #print(DNN_ans)
#
    ## draw graph
    #import matplotlib.pyplot as plt
#
    #plt.figure()
    #plt.style.use("ggplot")
    #plt.xlabel("Time")
    #plt.ylabel("Price")
#
    #plt.plot(train_x, train_y, color="black", label="history")
    #plt.plot(pred_x, bayes_l_ans, color="blue", label="Bayesian Linear")
    #plt.plot(pred_x, bayes_r_ans, color="yellow", label="Bayesian Ridge")
    #plt.plot(pred_x, SVR_ans, color="red", label="SVR")
    #plt.plot(pred_x, DNN_ans, color="green", label="DNN")
#
    #plt.show()