import os
import re

# import chardet
# import gensim
# import multiprocessing
# import numpy as np
# import tensorflow as tf
# from gensim.models.doc2vec import LabeledSentence, Doc2Vec, TaggedDocument
# from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn import svm
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer, CountVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, train_test_split

stop_words = stopwords.words('english')


def text_preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r"#(\w+)", '', text)
    text = re.sub(r"@(\w+)", '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.strip().lower()
    # text = word_tokenize(text)
    # print(text)
    # text = text.split()
    # text = [word for word in text if word not in stop_words]
    return text


def get_corpus(folder):
    article_dict = {}
    for each in os.listdir(folder):
        for root, dirs, files in os.walk(os.path.join(folder, each)):
            article_dict[each] = files
    # print(article_dict)

    corpus = []
    target = []
    for tag in article_dict:
        files = article_dict[tag]
        for file in files:
            # some file may encode by iso-8859-1
            f = open(os.path.join(folder, tag, file), 'r', encoding='utf-8')
            text = f.read()
            corpus.append(text_preprocess(text))
            target.append(tag)
            f.close()
    # print(corpus)
    # print(target)
    return corpus, target


def vectorize(save_path):
    tfidf_vectorizer = TfidfVectorizer(analyzer='word', stop_words='english', norm='l2')
    corpus_train = tfidf_vectorizer.fit_transform(x_train)
    joblib.dump(tfidf_vectorizer, save_path)
    # print(corpus_train)
    return corpus_train


def svm_build(save_path):
    # find suitable hyper parameter
    # it should be commented when running
    tuned_parameters = {
        'kernel': ['linear', 'rbf'],
        'C': [0.25, 0.5, 1, 2, 4, 8],
        'gamma': [0.125, 0.25, 0.5, 1, 2, 4]
    }
    clf = GridSearchCV(svm.SVC(), tuned_parameters, cv=3)
    vectorizer = TfidfVectorizer(analyzer='word', stop_words='english', norm='l2')
    clf.fit(vectorizer.fit_transform(corpus), target)
    print(clf.best_estimator_)

    # build & train svm model (should adjust parameter C and gamma)
    svc = svm.SVC(C=8, kernel='linear', gamma='auto').fit(x_corpus_vector, y_train)

    # save model
    joblib.dump(svc, save_path)
    return


def predict(vectorizer_model, svm_model):
    tfidf = joblib.load(vectorizer_model)
    corpus_test = tfidf.transform(x_test)

    clf = joblib.load(svm_model)
    report = classification_report(clf.predict(corpus_test), y_test)
    print(report)
    print(clf.score(corpus_test, y_test))
    return


if __name__ == '__main__':
    corpus, target = get_corpus('./LabelledNews')
    (x_train, x_test, y_train, y_test) = train_test_split(corpus, target, test_size=0.01)
    x_corpus_vector = vectorize('./models/tfidf_train')
    svm_build('./models/svm_train')
    predict('./models/tfidf_train', './models/svm_train')
