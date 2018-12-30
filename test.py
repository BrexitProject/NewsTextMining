import numpy as np
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
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
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


def read(folder):
    file_list = []
    for root, dirs, files in os.walk(folder):
        file_list = files

    res = []
    for file in file_list:
        f = open(os.path.join(folder, file), 'r', encoding='utf-8')
        text = f.read()
        res.append(text_preprocess(text))
        f.close()

    return res


if __name__ == '__main__':
    tfidf = joblib.load('./models/tfidf_train')
    corpus_test = tfidf.transform(read('./spider_news/thesun'))
    clf = joblib.load('./models/svm_train')

    result = clf.predict(corpus_test)
    leave_count = np.sum(result == 'leave')
    remain_count = np.sum(result == 'remain')

    print('Leave: %d (%.2f%%)' % (leave_count, leave_count / result.size * 100))
    print('Remain: %d (%.2f%%)' % (remain_count, remain_count / result.size * 100))
    print('Total: %d' % (result.size))
