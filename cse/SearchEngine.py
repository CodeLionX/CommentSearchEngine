import os
import re
import functools

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.indexing import (FileIndexer, IndexReader, DocumentMap)
from cse.reader import CommentReader
from cse.BooleanQueryParser import (BooleanQueryParser, Operator)
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

    def __init__(self, directory):
        self.__directory = directory
        self.__prep = (
            PreprocessorBuilder()
            .useNltkTokenizer()
            #.useNltkStopwordList()
            .usePorterStemmer()
            .addCustomStepToEnd(CustomPpStep())
            .build()
        )
        self.__pattern_whitespace = '[^\S\x0a\x0d]*'
        self.__pattern_keyword = '[\w\d]+'
        self.__pattern_prefix = self.__pattern_keyword + '\*'
        self.__pattern_phrase = '\'' + self.__pattern_keyword + '(' + self.__pattern_whitespace + self.__pattern_keyword + ')*\''
        self.__boolQueryPattern = re.compile(
            '^(([\w\d*:]+|(' + self.__pattern_phrase + '))' 
                + self.__pattern_whitespace 
                + '(NOT|OR|AND)' 
                + self.__pattern_whitespace 
                + '([\w\d*:]+|(' + self.__pattern_phrase + ')))+$',
            re.M
        )
        self.__prefixQueryPattern = re.compile(
            '^' + self.__pattern_whitespace + self.__pattern_prefix + self.__pattern_whitespace + '$',
            re.I | re.M
        )
        self.__phraseQueryPattern = re.compile(
            '^' + self.__pattern_whitespace + self.__pattern_phrase + self.__pattern_whitespace + '$',
            re.I | re.M
        )
        self.__indexLoaded = False
        self.__index = None
        self.__documentMap = None
        self.__commentReader = None


    def loadIndex(self):
        if self.__indexLoaded:
            print(self.__class__.__name__ + ":", "index already loaded")
            return

        print(self.__class__.__name__ + ":", "loading index files and comment reader")
        self.__index = IndexReader(
            self.__directory
        )

        self.__documentMap = DocumentMap(
            os.path.join("data", "documentMap.index")
        ).open()

        self.__commentReader = CommentReader(
            os.path.join("data", "comments.data"),
            os.path.join("data", "articleMapping.data"),
            os.path.join("data", "authorMapping.data")
        ).open()

        self.__indexLoaded = True


    def releaseIndex(self):
        if not self.__indexLoaded:
            print(self.__class__.__name__ + ":", "no index loaded, nothing to release")
            return

        print(self.__class__.__name__ + ":", "releasing index files and comment reader")
        self.__index.close()
        self.__documentMap.close()
        self.__commentReader.close()

        self.__indexLoaded = False


    def index(self):
        if self.__indexLoaded:
            self.releaseIndex()

        FileIndexer(self.__directory, self.__prep).index()


    def close(self):
        self.releaseIndex()


    def search(self, query, topK=10):
        if not self.__indexLoaded:
            print("Index was not loaded!")
            return []

        results = []
        if self.__boolQueryPattern.fullmatch(query):
            print("\n\n##### Boolean Query Search")
            results = self.__booleanSearch(query)

        elif self.__phraseQueryPattern.fullmatch(query):
            print("\n\n##### Phrase Search")
            results = self.__phraseSearch(query, topK)

        elif query.startswith('ReplyTo:'):
            print("\n\n##### ReplyTo Search")
            results = self.__replyToSearch(query)

        elif self.__prefixQueryPattern.fullmatch(query):
            print("\n\n##### Prefix Search")
            results = self.__prefixSearch(query, topK)

        elif re.search('NOT|AND|OR|[*]', query):
                print("*** ERROR ***")
                print("Query not supported. Please use the following search options:\n" +
                    "  - Keyword Search: Use one or more words to search for: e.g. `donald trump news`\n" +
                    "  - Phrase Search:  Exact word order match: e.g. `christams market`\n" +
                    "  - ReplyTo Search: Search for replies to a parent comment: e.g. `ReplyTo:12345` (no whitespace allowed between keyword and comment ID, also use exact keyword `ReplyTo` [case sensitive])\n" +
                    "  - Prefix Search:  Search for comments containing words with a specifc prefix: e.g. `euro`\n" +
                    "  - Boolean Search: Please use only one of the following binary Operators or none: 'NOT', 'AND', 'OR'. You are allowed to use single-keyword-queries, prefix-queries, replyTo-queries and phrase-queries between binary operators"
                )
                return []

        else:
            print("\n\n##### Keyword Search")
            results = self.__keywordSearch(query, topK)


        print("##### Query for >>>", query, "<<< returned", len(results), "of k=" + str(topK) + " requested comments")
        # print("      CIDs:", results)
        return self.__loadDocumentTextForCids(results)


    def __booleanSearch(self, query):
        # operator precedence: NOT > AND > OR
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

        # check if query contains any other operator (we do not support this!)
        for operator in set(Operator)-set([op]):
            if operator in p:
                print("Only a single Operator-Type is supported in boolean search queries! Found:", op, operator)
                return []

        terms = [term for term in p if term not in Operator]

        # load document set per term
        for term in terms:
            cids = []
            if term.strip().endswith("*"):
                cids = self.__prefixSearchTerm(term)

            elif term.strip().startswith("ReplyTo:"):
                cids = self.__replyToSearch(term)

            elif self.__phraseQueryPattern.fullmatch(term):
                cids = self.__phraseSearch(term, None)

            else:
                pTerm = self.__prep.processText(term)
                if not pTerm or len(pTerm) > 1:
                    print(
                        self.__class__.__name__ + ":", "term", term,
                        "is invalid! Please use only one word for boolean queries."
                    )
                    return []
                cids = [cid for cid, _, _ in self.__index.postingList(pTerm[0][0])]

            if cids:
                cidSets.append(set(cids))

        if not cidSets:
            return []

        # we are able to sort the cid sets based on their length, because we only have one kind of operators
        # this should speed up the combination a little bit
        cidSets.sort(key=lambda cidSet: len(cidSet))
        firstCids = cidSets[0]
        cidSets.remove(firstCids)
        cids = functools.reduce(self.__cidSetCombiner(op), cidSets, firstCids)

        return cids


    def __phraseSearch(self, query, topK):
        queryTermTuples = self.__prep.processText(query.replace("'", ""))
        queryTerms = [term for term, _ in queryTermTuples]
        # use ranking:
        idfs = {}
        ranker = Ranker(topK)

        # determine documents with ordered consecutive query terms
        first = True
        cidPosTuples = {}
        for term in queryTerms:
            postingListEntry = self.__index.retrieve(term)

            if postingListEntry.idf():
                idfs[term] = postingListEntry.idf()

            if not postingListEntry.postingList():
                cidPosTuples = {}
                return []
            elif first:
                for cid, tf, posList in postingListEntry.postingList():
                    cidPosTuples[cid] = posList
                    ranker.documentTerm(cid, term, tf, postingListEntry.idf())
                first = False
            else:
                newCidPosTuples = {}
                for cid, tf, posList in postingListEntry.postingList():
                    newCidPosTuples[cid] = posList
                    ranker.documentTerm(cid, term, tf, postingListEntry.idf())
                cidPosTuples = self.__documentsWithConsecutiveTerms(cidPosTuples, newCidPosTuples)
                    
        
        ranker.queryTerms(queryTerms, idfs)
        ranker.filterDocumentTermWeightsBy(lambda cid: cid in cidPosTuples)
        rankedCids = ranker.rank()

        return set([cid for _, _, cid in rankedCids])


    def __replyToSearch(self, query):
        queryParts = query.strip().split(':')
        if len(queryParts) > 2:
            print(
                self.__class__.__name__ + ":", query,
                "is invalid! Please use only reply to queries with the following schema:",
                "`ReplyTo:<numeric comment id>`, eg. `ReplyTo:12345`"
            )
            return []

        try:
            parentCid = int(queryParts[1])
        except ArithmeticError:
            print(
                self.__class__.__name__ + ":", query,
                "is invalid! Please use only reply to queries with the following schema:",
                "`ReplyTo:<numeric comment id>`, eg. `ReplyTo:12345`"
            )
        
        # load child cids and return them
        return self.__index.repliedTo(parentCid)


    def __keywordSearch(self, query, topK):
        idfs = {}
        queryTerms = []
        # use ranking:
        ranker = Ranker(topK)

        queryTermTuples = self.__prep.processText(query)
        queryTerms = [term for term, _ in queryTermTuples]

        for term in queryTerms:
            postingListEntry = self.__index.retrieve(term)

            if postingListEntry.idf():
                idfs[term] = postingListEntry.idf()

            if postingListEntry.postingList():
                for cid, tf, _ in postingListEntry.postingList():
                    ranker.documentTerm(cid, term, tf, postingListEntry.idf())

        # calculate query term weights
        ranker.queryTerms(queryTerms, idfs)
        rankedCids = ranker.rank()

        #for rank, score, cid in rankedCids:
        #    print(rank, score, cid)
        return set([cid for _, _, cid in rankedCids])


    def __prefixSearch(self, term, topK):
        term = term.replace("*", "")
        # get prefix matching terms
        matchedTerms = [token for token in self.__index.terms() if token.startswith(term)]
        ranker = Ranker(topK)

        # load posting list
        idfs = {}
        for t in matchedTerms:
            postingListEntry = self.__index.retrieve(t)

            if postingListEntry.idf():
                idfs[t] = postingListEntry.idf()

            if postingListEntry.postingList():
                for cid, tf, _ in postingListEntry.postingList():
                    ranker.documentTerm(cid, t, tf, postingListEntry.idf())

        ranker.queryTerms(matchedTerms, idfs)
        rankedCids = ranker.rank()
        return set([cid for _, _, cid in rankedCids])


    def __prefixSearchTerm(self, term):
        """
        This should only used internally. No ranking is performed. All additional information
        of the index is lost (like tf, idf, positions, ...).
        Only returns all document IDs containing at least one matched term.
        """
        term = term.replace("*", "")
        # get prefix matching terms
        matchedTerms = [token for token in self.__index.terms() if token.startswith(term)]

        cids = set()
        for t in matchedTerms:
            cids.update((cid for cid, _, _ in self.__index.postingList(t)))

        return cids


    def __loadDocumentTextForCids(self, cids):
        results = []

        if cids is None or cids is []:
            return results

        # get document pointers and load comment texts
        for cid in cids:
            try:
                pointer = self.__documentMap.get(cid)
                rowData = self.__commentReader.readline(pointer)
                results.append(rowData["comment_text"])
            except KeyError:
                print(self.__class__.__name__ + ":", "comment", cid, "not found!")

        return results


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
        #print(prettyPrint(self.search("party AND chancellor")[:1]))
        #print(prettyPrint(self.search("party NOT politics")[:1]))
        #print(prettyPrint(self.search("war OR conflict")[:1]))
        print(prettyPrint(self.search("euro* NOT europe")[:1]))
        print(prettyPrint(self.search("publi* OR moderation")[:1]))
        print(prettyPrint(self.search("'the european union'")[:1]))
        print(prettyPrint(self.search("'christmas market'")[:1]))


    def printTestQueryResults(self):
        #print(prettyPrint(self.search("christmas")))
        #print(prettyPrint(self.search("christmas market")[:5]))
        #print(prettyPrint(self.search("hate")[:5]))
        #print(prettyPrint(self.search("prefix* help")[:5]))
        #print(prettyPrint(self.search("europe*")[:5]))
        #print(prettyPrint(self.search("party AND chancellor NOT europe")))
        #print(prettyPrint(self.search("NOT hate")[:5]))
        #print(prettyPrint(self.search("Trump AND hate")[:5]))
        #print(prettyPrint(self.search("'Republican legislation'")))
        #print(prettyPrint(self.search("Trump President Russia Russia Russia", 5)))
        #print(prettyPrint(self.search("'they also give'")))
        pass


    def printAssignment4QueryResults(self):
        print(prettyPrint(self.search("christmas market", 5)))
        print(prettyPrint(self.search("catalonia independence", 5)))
        print(prettyPrint(self.search("'european union'")[:5]))
        print(prettyPrint(self.search("negotiate", 5)))


    def printAssignment7QueryResults(self):
        print("\n\n#### Parent CID:7850")
        print(prettyPrint(self.__loadDocumentTextForCids([7850])))
        print(prettyPrint(self.search("ReplyTo:7850")))

        print("\n\n#### Parent CID:9590")
        print(prettyPrint(self.__loadDocumentTextForCids([9590])))
        print(prettyPrint(self.search("ReplyTo:9590")))

        print("\n\n#### Parent CID:9591")
        print(prettyPrint(self.__loadDocumentTextForCids([9591])))
        print(prettyPrint(self.search("ReplyTo:9591")))

        print("\n\n#### Parent CID:9591")
        print(prettyPrint(self.__loadDocumentTextForCids([9591])))
        print(prettyPrint(self.search("ReplyTo:9591 AND 'hate God'")))


    def printFinalQueryResults(self):
        print(prettyPrint(self.search("election")))
        print(prettyPrint(self.search("military conflict")))
        print(prettyPrint(self.search("'German chancellor'")))
        #print(prettyPrint(self.search("'guardians of the galaxy'"))) # Error: killed (over 4GB memory)
        print(prettyPrint(self.search("brexit AND economy")))
        print(prettyPrint(self.search("jared NOT kushner")))
        print(prettyPrint(self.search("isra*")))
        print(prettyPrint(self.search("ReplyTo:107701851")))
        print(prettyPrint(self.search("288 days")))
        print(prettyPrint(self.search("merkel NOT chancel*")))
        #print(prettyPrint(self.search("eu OR 'european union'"))) # needs way tooo long to print to console for simple testing!
        print(prettyPrint(self.search("trump AND putin AND merkel AND xi")))
        print(prettyPrint(self.search("'new ye'*")))
        print(prettyPrint(self.search("ReplyTo:107701851 AND 'silicon valley'")))



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
    se.loadIndex()
    #se.printAssignment2QueryResults()
    #se.printAssignment3QueryResults()
    #se.printTestQueryResults()
    #se.printAssignment4QueryResults()
    #se.printAssignment7QueryResults()
    se.printFinalQueryResults()
    se.close()
