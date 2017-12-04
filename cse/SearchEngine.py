import os
import re
import functools

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.indexing import (InvertedIndexReader, DocumentMap)
from cse.indexing.FileIndexer import FileIndexer
from cse.CommentReader import CommentReader
from cse.BooleanQueryParser import (BooleanQueryParser, Operator)
from cse.helper.MultiFileMap import MultiFileMap
from cse.Ranker import Ranker


class SearchEngine():

    """
    preprocessing
    - to lower case
    - tokenization (remove punctuation)
    - remove stopwords (https://github.com/igorbrigadir/stopwords)
    - stemming (porter(2), porter very fast python wrapper: https://github.com/shibukawa/snowball_py)
      or lemmatization (i dont think we need this)

    see: http://whoosh.readthedocs.io/en/latest/stemming.html (stemming from whoosh in separate package: https://pypi.python.org/pypi/stemming/1.0)
    """
    __prep = None
    __boolQueryPattern = None
    __prefixQueryPattern = None
    __phraseQueryPattern = None

    __directory = ""


    def __init__(self, directory):
        self.__directory = directory
        self.__prep = (
            PreprocessorBuilder()
            .useNltkTokenizer()
            .useNltkStopwordList()
            .usePorterStemmer()
            .addCustomStepToEnd(CustomPpStep())
            .build()
        )
        self.__boolQueryPattern = re.compile('^([\w\d*]+[^\S\x0a\x0d]*(NOT|OR|AND)[^\S\x0a\x0d]*[\w\d*]+)+$', re.M)
        self.__prefixQueryPattern = re.compile('^[^\S\x0a\x0d]*([\w\d]*\*)[^\S\x0a\x0d]*$', re.I | re.M)
        self.__phraseQueryPattern = re.compile('^[^\S\x0a\x0d]*(\'[\w\d]+([^\S\x0a\x0d]*[\w\d]*)*\')[^\S\x0a\x0d]*$', re.I | re.M)


    def loadIndex(self):
        return InvertedIndexReader(self.__directory)


    def index(self):
        indexer = FileIndexer(self.__directory, self.__prep)
        indexer.index()


    def search(self, query, topK=10):
        results = []
        if self.__boolQueryPattern.fullmatch(query):
            print("\n\n##### Boolean Query Search")
            results = self.__booleanSearch(query)

        elif self.__phraseQueryPattern.fullmatch(query):
            print("\n\n##### Phrase Search")
            results = self.__phraseSearch(query, topK)

        elif re.search('NOT|AND|OR|[*]', query):
                print("*** ERROR ***")
                #raise ValueError("Query not supported. Please use only one of the following Operators: '*', 'NOT', 'AND', 'OR'")
                return ["*** ERROR ***", "Query not supported. Please use only one of the following binary Operators or none: '*', 'NOT', 'AND', 'OR'"]

        else:
            print("\n\n##### Keyword Search")
            results = self.__keywordSearch(query, topK)


        print("##### Query for >>>", query, "<<< returned", len(results), "comments")
        return results


    def __booleanSearch(self, query):
        with self.loadIndex() as ii:
            # operator precedence: STAR > NOT > AND > OR
            p = BooleanQueryParser(query).get()
            cidSets = []

            # filter out operators
            # note: we only support one opperator kind per query at the moment!
            op = None
            if Operator.NOT in p:   op = Operator.NOT
            elif Operator.OR in p:  op = Operator.OR
            elif Operator.AND in p: op = Operator.AND
            else:
                print("No or wrong operator in query!!")
                return []
            terms = [term for term in p if term not in Operator]

            # load document set per term
            for term in terms:
                cidTuples = []
                if term.endswith("*"):
                    cidTuples = self.__prefixSearchTerm(ii, term.replace("*", ""))

                else:
                    pTerm = self.__prep.processText(term)
                    if not pTerm or len(pTerm) > 1:
                        print(
                            self.__class__.__name__ + ":", "term", term,
                            "is invalid! Please use only one word for boolean queries."
                        )
                        return []
                    cidTuples = ii.retrievePostingList(pTerm[0][0])

                if cidTuples:
                    cidSets.append(set( (cid for cid, _ in cidTuples) ))

        if not cidSets:
            return []

        firstCids = cidSets[0]
        cidSets.remove(firstCids)
        cids = functools.reduce(self.__cidSetCombiner(op), cidSets, firstCids)

        return self.__loadDocumentTextForCids(cids)


    def __phraseSearch(self, query, topK):
        queryTermTuples = self.__prep.processText(query.replace("'", ""))
        queryTerms = [term for term, _ in queryTermTuples]
        # use ranking:
        idfs = {}
        ranker = Ranker(topK)

        with self.loadIndex() as ii:
            # determine documents with ordered consecutive query terms
            first = True
            cidPosTuples = {}
            for term in queryTerms:
                idf, pl = ii.retrieveAll(term)

                if idf:
                    idfs[term] = idf

                if not pl:
                    cidPosTuples = {}
                    return []
                elif first:
                    for cid, tf, posList in pl:
                        cidPosTuples[cid] = posList
                        ranker.documentTerm(cid, term, tf, idf)
                    first = False
                else:
                    newCidPosTuples = {}
                    for cid, tf, posList in pl:
                        newCidPosTuples[cid] = posList
                        ranker.documentTerm(cid, term, tf, idf)
                    cidPosTuples = self.__documentsWithConsecutiveTerms(cidPosTuples, newCidPosTuples)
                    
        
        ranker.queryTerms(queryTerms, idfs)
        ranker.filterDocumentTermWeightsBy(lambda cid: cid in cidPosTuples)
        rankedCids = ranker.rank()

        return self.__loadDocumentTextForCids(set([cid for _, _, cid in rankedCids]))


    def __keywordSearch(self, query, topK):
        idfs = {}
        queryTerms = []
        # use ranking:
        ranker = Ranker(topK)

        with self.loadIndex() as ii:
            queryTermTuples = self.__prep.processText(query)
            queryTerms = [term for term, _ in queryTermTuples]

            allCidTuples = []
            for term in queryTerms:
                idf, cidTuples = ii.retrieveAll(term)
                
                if idf:
                    idfs[term] = idf

                if cidTuples:
                    for cid, tf, _ in cidTuples:
                        ranker.documentTerm(cid, term, tf, idf)
                    allCidTuples = allCidTuples + cidTuples

        # calculate query term weights
        ranker.queryTerms(queryTerms, idfs)
        rankedCids = ranker.rank()

        #for r, s, c in rankedCids:
        #    print(r, s, c)
        return self.__loadDocumentTextForCids(set([cid for _, _, cid in rankedCids]))


    def __prefixSearchTerm(self, index, term):
        # get prefix matching terms
        matchedTerms = [token for token in index.terms() if token.startswith(term)]

        # load posting list
        cidTuples = {}
        for term in matchedTerms:
            for cid, posList in index.retrievePostingList(term):
                # there should be NO possibility that we have two terms in one document at the same position
                # so this operation can be done on simple lists without checking duplicates
                positions = cidTuples.get(cid, [])
                positions = positions + posList
                positions.sort()
                cidTuples[cid] = positions

        # reconstruct tuple list: [(cid, positionList), (cid2, positionList2)]
        return [(cid, cidTuples[cid]) for cid in cidTuples]


    def __loadDocumentTextForCids(self, cids):
        results = {}
        commentPointers = set()

        if not cids:
            return results

        # get document pointers
        with DocumentMap(os.path.join("data", "documentMap.index")).open() as documentMap:
            for cid in cids:
                try:
                    commentPointers.add(documentMap.getPointer(cid))
                except KeyError:
                    print(self.__class__.__name__ + ":", "comment", cid, "not found!")

        # load document text
        with CommentReader(os.path.join("data", "comments.data")).open() as cr:
            for pointer, rowData in enumerate(cr):
                if pointer in commentPointers:
                    results[pointer] = rowData["comment_text"]

        return list(map(results.get, commentPointers))


    def __documentsWithConsecutiveTerms(self, firstTermTuples, secondTermTuples):
        # documents containing both terms:
        cids = [cid for cid in firstTermTuples if cid in secondTermTuples]

        # check for consecutive term positions
        resultCidTuples = {}
        for cid in cids:
            for pos in firstTermTuples[cid]:
                if pos+1 in secondTermTuples[cid]:
                    resultCidTuples[cid] = secondTermTuples[cid]
        return resultCidTuples


    def __cidSetCombiner(self, op):
        def notFunc(x, y):
            return x - y
        def andFunc(x, y):
            return x & y
        def orFunc(x, y):
            return x | y

        switcher = {
            Operator.NOT: notFunc,
            Operator.AND: andFunc,
            Operator.OR:  orFunc
        }
        return switcher.get(op)


    def printAssignment2QueryResults(self):
        print(prettyPrint(self.search("October")[:5]))
        print(prettyPrint(self.search("jobs")[:5]))
        print(prettyPrint(self.search("Trump")[:5]))
        print(prettyPrint(self.search("hate")[:5]))
    

    def printAssignment3QueryResults(self):
        print(prettyPrint(self.search("party AND chancellor")[:1]))
        print(prettyPrint(self.search("party NOT politics")[:1]))
        print(prettyPrint(self.search("war OR conflict")[:1]))
        print(prettyPrint(self.search("euro* NOT europe")[:1]))
        print(prettyPrint(self.search("publi* OR moderation")[:1]))
        print(prettyPrint(self.search("'the european union'")[:1]))
        print(prettyPrint(self.search("'christmas market'")[:1]))


    def printTestQueryResults(self):
        print(prettyPrint(self.search("christmas")[:5]))
        print(prettyPrint(self.search("christmas market")[:5]))
        #print(prettyPrint(self.search("hate")[:5]))
        #print(prettyPrint(self.search("prefix* help")[:5]))
        #print(prettyPrint(self.search("atta*")[:5]))
        #print(prettyPrint(self.search("party AND chancellor NOT europe")))
        #print(prettyPrint(self.search("NOT hate")[:5]))
        #print(prettyPrint(self.search("Trump AND hate")[:5]))
        #print(prettyPrint(self.search("'Republican legislation'")))
        #print(prettyPrint(self.search("Trump President Russia Russia Russia", 5)))
        #print(prettyPrint(self.search("'truck confederate flag'")))
        pass


    def printAssignment4QueryResults(self):
        #print(prettyPrint(self.search("christmas market", 5)))
        #print(prettyPrint(self.search("catalonia independence", 5)))
        print(prettyPrint(self.search("'european union'")[:5]))
        #print(prettyPrint(self.search("negotiate", 5)))




def prettyPrint(l):
    return "\t" + "\n\t".join([t.replace("\n", "\\n") for t in l])



class CustomPpStep(PreprocessorStep):

    def __init__(self):
        pass

    def process(self, tokenTuple):
        return tokenTuple if not tokenTuple[0].startswith("//") else None

    def processAll(self, tokenTuples):
        return [(token, position) for token, position in tokenTuples if not token.startswith("//")]



if __name__ == '__main__':
    se = SearchEngine("data")
    #se.index()
    #se.printAssignment2QueryResults()
    #se.printAssignment3QueryResults()
    #se.printTestQueryResults()
    se.printAssignment4QueryResults()
