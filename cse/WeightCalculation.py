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
    try:
        dj_norm = cache[tuple(docWeights)]
    except KeyError:
        dj_norm = np.linalg.norm(dj)
        cache[tuple(docWeights)] = dj_norm
    try:
        q_norm = cache[tuple(queryWeights)]
    except KeyError:
        q_norm = np.linalg.norm(q)
        cache[tuple(queryWeights)] = q_norm
    #print(q, dj)
    score = np.dot(dj, q) / (dj_norm * q_norm)
    #print(score)
    return float(score)


def oldCosineSimilarity(docWeights, queryWeights):
    dj = np.array(docWeights)
    q = np.array(queryWeights)

    score = np.dot(dj, q) / (np.linalg.norm(dj) * np.linalg.norm(q))
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



def profileTime(func, docs, query, warm=False):
    import cProfile
    import pstats
    if not warm:
        NormCache().clear()

    pr = cProfile.Profile()
    results = []
    for doc in docs:
        pr.enable()
        r = func(doc, query)
        pr.disable()
        results.append(r)
    
    print("\nTime statistics for {}".format(func.__name__))
    ps = pstats.Stats(pr)
    ps.sort_stats('time')
    ps.print_stats(10)


def profileMemory(func, docs, query, warm=False):
    import tracemalloc
    snapshots = {}
    if not warm:
        NormCache().clear()

    tracemalloc.start()
    results = []
    for doc in docs:
        r = func(doc, query)
        results.append(r)

    snapshots[func.__name__] = tracemalloc.take_snapshot()
    used, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("Memory Snapshot for {}".format(func.__name__))
    print("Used memory={}, Peak memory={}".format(used, peak))
    for stat in snapshots[func.__name__].statistics('lineno'):
        print(stat)


if __name__ == "__main__":
    import random

    # data
    DOC_SIZE = 5
    SAMPLE_SIZE = 200000
    docs = []
    for i in range(0, SAMPLE_SIZE):
        docs.append([random.random() for i in range(DOC_SIZE)])
    query = [random.random() for i in range(0, DOC_SIZE)]

    print("Testrun for {} documents each containing {} values".format(SAMPLE_SIZE, DOC_SIZE))
    print("\nUncached cosine similarity")
    profileTime(oldCosineSimilarity, docs, query)
    profileMemory(oldCosineSimilarity, docs, query)

    print("\nCached cosine similarity")
    profileTime(cosineSimilarity, docs, query)
    profileMemory(cosineSimilarity, docs, query)

    print("\nWarm cached cosine similarity")
    profileTime(cosineSimilarity, docs, query, warm=True)
    profileMemory(cosineSimilarity, docs, query, warm=True)
