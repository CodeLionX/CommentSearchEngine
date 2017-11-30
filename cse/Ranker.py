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
        print(self.__terms, self.__wq)


    def documentTerm(self, cid, tf, idf):
        wd = self.__wdi.get(cid, [])
        wd.append(wc.calcWeight(tf, idf))
        self.__wdi[cid] = wd


    def rank(self):
        self.__fillDocumentWeights()
        rankedDocs = []
        for cid in self.__wdi:
            rankedDocs.append((wc.cosineSimilarity(self.__wdi[cid], self.__wq), cid))
        rankedDocs.sort(key=lambda x: -x[0])

        return [(i+1, rankedDoc[1]) for i, rankedDoc in enumerate(rankedDocs[:self.__limit])]
        #return [(i+1, rankedDoc[1]) for i, rankedDoc in enumerate(rankedDocs)]


    def __fillDocumentWeights(self):
        nTerms = len(self.__terms)
        filler = wc.missingTermWeight()
        for cid in self.__wdi:
            for _ in range(nTerms - len(self.__wdi[cid])):
                self.__wdi[cid].append(filler)
            #assert len(self.__terms) == len(self.__wdi[cid])

        #assert len(self.__terms) == len(self.__wq)
