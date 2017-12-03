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
    dj = np.array(docWeights)
    q = np.array(queryWeights)
    #print(q, dj)
    score = np.dot(dj, q) / (np.linalg.norm(dj) * np.linalg.norm(q))
    #print(score)
    return float(score)


def euclDistance(docWeights, queryWeights):
    dj = np.array(docWeights)
    q = np.array(queryWeights)
    #print(q, dj)
    score = np.linalg.norm(dj - q)
    #print(score)
    return float(score)


if __name__ == "__main__":
    w1 = [1,4,0,1.4,23.0]
    w2 = [76,5.7,1,13.5,3.5]

    print(cosineSimilarity(w1, w2))
