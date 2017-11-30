import math
import numpy as np

def calcTf(nAllTermsInDoc, nTermInDoc):
    return math.log10(
        float(nTermInDoc) /
        float(nAllTermsInDoc)
    ) + 1


def calcIdf(nAllDocuments, nDocumentsContainingTerm):
    return math.log10(
        float(nAllDocuments) /
        float(nDocumentsContainingTerm)
    ) + 1


def calcWeight(tf, idf):
    return tf * idf


def cosineSimilarity(docWeights, queryWeights):
    dj = np.array(docWeights)
    q = np.array(queryWeights)
    return float(np.dot(dj, q) / (np.linalg.norm(dj) * np.linalg.norm(q)))


if __name__ == "__main__":
    w1 = [1,4,0,1.4,23.0]
    w2 = [76,5.7,1,13.5,3.5]

    print(cosineSimilarity(w1, w2))
