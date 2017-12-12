import os
import sys
import math
import operator
import pickle
import numpy as np
from tqdm import tqdm

from preprocessing import tokenize

def cosine(v1, v2):
    return float(np.dot(v1, v2)) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def make_vector(tf):
    return np.array(tf.values())

def get_tf_for_doc(tf, doc_id):
    doc_id = str(doc_id)
    v = {}
    for term in tf:
        if doc_id not in tf[term]:
            v[term] = 0
        else:
            v[term] = tf[term][doc_id]
    return v

def get_tf_for_query(tf, query):
    my_tf = {}
    words = tokenize(query)
    for word in words:
        if (word not in my_tf):
            my_tf[word] = 0
        my_tf[word] += 1

    v = {}
    for term in tf:
        if term not in my_tf:
            v[term] = 0
        else:
            v[term] = my_tf[term]

    return v

class VSM:
    def __init__(self, corpus, tf, idf):
        self.corpus = corpus
        self.tf = tf
        self.idf = idf
        self.songs = { doc['index']: doc for doc in corpus }

        print('caching tf_idf vectors...')
        self.doc_tf_idf_vectors = {}
        for doc_id in tqdm(self.get_doc_ids()):
            doc_vector = make_vector(self.get_tf_idf(get_tf_for_doc(self.tf, doc_id)))
            self.doc_tf_idf_vectors[doc_id] = doc_vector

    def get_doc_ids(self):
        return [ doc['index'] for doc in self.corpus]

    def get_tf_idf(self, v_tf):
        return { term : float(v_tf[term]) / self.idf[term] for term in v_tf }

    def display(self, results):
        n = 10
        for i in range(n):
            print('Position #' + str(i+1) + ', score: ' + str(results[i][1]))
            print('-' * 32)
            song = self.songs[results[i][0]]
            print song
            print

    def get_scores_tf(self, query):
        query_vector = make_vector(get_tf_for_query(self.tf, query))
        scores = {}
        for doc_id in tqdm(self.get_doc_ids()):
            doc_vector = make_vector(get_tf_for_doc(self.tf, doc_id))
            scores[doc_id] = cosine(query_vector, doc_vector)

        ranking = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        return ranking

    def get_scores_tf_idf(self, query):
        query_vector = make_vector(self.get_tf_idf(get_tf_for_query(self.tf, query)))
        scores = {}
        for doc_id in tqdm(self.get_doc_ids()):
            doc_vector = self.doc_tf_idf_vectors[doc_id]
            scores[doc_id] = cosine(query_vector, doc_vector)

        ranking = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        return ranking
        
    def search(self, query):
        results = self.get_scores_tf_idf(query)
        self.display(results)


if __name__ == '__main__':
    pathname = os.path.dirname(sys.argv[0])
    ROOT_DIR = os.path.abspath(pathname)
    DATA_DIR = 'data'

    corpus = pickle.load(open(os.path.join(ROOT_DIR, DATA_DIR, 'corpus.pickle'), 'rb'))
    tf = pickle.load(open(os.path.join(ROOT_DIR, DATA_DIR, 'tf.pickle'), 'rb'))
    idf = pickle.load(open(os.path.join(ROOT_DIR, DATA_DIR, 'idf.pickle'), 'rb'))

    vsm = VSM(corpus, tf, idf)
    vsm.search('I love you')

