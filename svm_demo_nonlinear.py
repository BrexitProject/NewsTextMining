import numpy as np
import tensorflow as tf
from sklearn import svm, datasets
from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV, train_test_split

if __name__ == '__main__':
    # load data
    # iris = datasets.load_iris()
    # x = iris.data
    # y = iris.target
    (x, y) = datasets.make_circles(n_samples=300, factor=0.5, noise=0.1)
    y = ['first' if e == 1 else 'second' for e in y]
    print(y)
    # print(x)
    # print(y)

    # divide data into train set / test set
    (x_train, x_test, y_train, y_test) = train_test_split(x, y, test_size=0.8)

    # find suitable hyper parameter
    # it should be commented when running
    tuned_parameters = {
        'kernel': ['linear', 'rbf'],
        'C': [0.25, 0.5, 1, 2, 4, 8],
        'gamma': [0.125, 0.25, 0.5, 1, 2, 4]
    }
    clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=3)
    clf.fit(x_train, y_train)
    print(clf.best_estimator_)

    # build & train svm model (should adjust parameter C and gamma)
    svc = svm.SVC(C=0.5, kernel='rbf', gamma=2).fit(x_train, y_train)

    # save model
    joblib.dump(svc, './models/svm_train')

    # load model from file
    clf = joblib.load('./models/svm_train')

    # predict another point's tag
    test_point = [[5.22, -2.13], [0.12, -0.51]]
    prediction = clf.predict(test_point)
    print(prediction)

    # calculate accuracy on test set
    acc = clf.score(x_test, y_test)
    print('accuracy on test set: %f' % (acc))
