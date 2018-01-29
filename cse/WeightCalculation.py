import math
import numpy as np


def calcTf(nAllTermsInDoc, nTermInDoc):
    """
    # to unstable (most values are near to each other for all docs)
    return math.log10(
        (float(nTermInDoc) / float(nAllTermsInDoc))
        + 1
    )
    """
    return float(nTermInDoc) / float(nAllTermsInDoc)


def calcIdf(nAllDocuments, nDocumentsContainingTerm):
    """
    return math.log10(
        (float(nAllDocuments) / float(nDocumentsContainingTerm))
        + 1
    )
    """
    return float(nAllDocuments) / float(nDocumentsContainingTerm)


def calcWeight(tf, idf):
    return tf * idf


def missingTermWeight():
    return 0


def cosineSimilarity(docWeights, queryWeights):
    cache = NormCache()
    dj = np.array(docWeights)
    q = np.array(queryWeights)

    # use cache to store norms
    dj_norm = np.linalg.norm(dj)
    try:
        q_norm = cache[tuple(queryWeights)]
    except KeyError:
        q_norm = np.linalg.norm(q)
        cache[tuple(queryWeights)] = q_norm
    #print(q, dj)
    score = np.dot(dj, q) / (dj_norm * q_norm)
    #print(score)
    return float(score)


def euclDistance(docWeights, queryWeights):
    dj = np.array(docWeights)
    q = np.array(queryWeights)
    #print(q, dj)
    score = np.linalg.norm(dj - q)
    #print(score)
    return float(score)


class NormCache(object):
    """
    Singleton Cache from http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html.
    Instance Holder
    """
    class __NormCache:
        """
        Singleton Cache from http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html.
        """
        def __init__(self):
            self.cache = {}
        def __str__(self):
            return str(self.cache)
        def __getitem__(self, key):
            return self.cache[key]
        def __setitem__(self, key, value):
            self.cache[key] = value
        def clear(self):
            self.cache = {}
    
    instance = None
    def __new__(cls): # __new__ is always a classmethod
        if not NormCache.instance:
            NormCache.instance = NormCache.__NormCache()
        return NormCache.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
