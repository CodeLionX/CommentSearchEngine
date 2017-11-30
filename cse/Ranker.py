import cse.WeightCalculation as wc

class Ranker(object):


    def __init__(self, limit):
        self.__limit = limit
        self.__wq = []
        self.__terms = []
        self.__wdi = {}


    def queryTerms(self, terms, idfs):
        termCounts = {}
        for term in terms:
            count = termCounts.get(term, 0)
            count += 1
            termCounts[term] = count

        for term in termCounts:
            self.__terms.append(term)
            try:
                idf = idfs[term]
            except KeyError:
                idf = 0

            self.__wq.append(wc.calcWeight(
                wc.calcTf(len(terms), termCounts[term]),
                idf
            ))


    def documentTerm(self, cid, tf, idf):
        self.__wdi[cid] = wc.calcWeight(tf, idf)


    def rank(self):
        rankedDocs = []
        for cid in self.__wdi:
            rankedDocs.append((wc.cosineSimilarity(self.__wq, self.__wdi[cid]), cid))
        rankedDocs.sort(key=lambda x: -x[0])

        #return [(i+1, rankedDoc[1]) for i, rankedDoc in enumerate(rankedDocs[:self.__limit])]
        return [(i+1, rankedDoc[1]) for i, rankedDoc in enumerate(rankedDocs)]
