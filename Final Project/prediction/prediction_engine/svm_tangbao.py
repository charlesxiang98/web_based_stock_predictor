from sklearn import svm
from get_data import get_long_term_data
import matplotlib.pyplot as plt


class SVM(object):

    @staticmethod
    def predict(X, y, symbol):
        print(y)
        clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1)
        clf.fit(X, y)
        return clf.predict(X)


if __name__ == '__main__':
    X, y = get_long_term_data('GOOG')
    p = SVM.predict(X, y, 'GOOG')
    plt.scatter(X, y, color = 'darkorange')
    plt.plot(X, p, color = 'navy')
    plt.show()
