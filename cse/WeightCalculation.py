import math


def tf(nAllTermsInDoc, nTermInDoc):
    return math.log10(
        float(nTermInDoc) /
        float(nAllTermsInDoc)
    )


def idf(nAllDocuments, nDocumentsContainingTerm):
    return math.log10(
        float(nAllDocuments) /
        float(nDocumentsContainingTerm)
    )
