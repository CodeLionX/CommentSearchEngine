import os
import re

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.indexing import (InvertedIndexReader, DocumentMap)
from cse.indexing.FileIndexer import FileIndexer
from cse.CommentReader import CommentReader
from cse.BooleanQueryParser import (BooleanQueryParser, Operator)
from cse.helper.MultiFileMap import MultiFileMap


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


    def __init__(self):
        self.__prep = (
            PreprocessorBuilder()
            .useNltkTokenizer()
            .useNltkStopwordList()
            .usePorterStemmer()
            .addCustomStepToEnd(CustomPpStep())
            .build()
        )
        self.__boolQueryPattern = re.compile('^([\w\d*]+[^\S\x0a\x0d]*(NOT|OR|AND)[^\S\x0a\x0d]*[\w\d*]+)$', re.M)
        self.__prefixQueryPattern = re.compile('^[^\S\x0a\x0d]*([\w\d]*\*)[^\S\x0a\x0d]*$', re.I | re.M)
        self.__phraseQueryPattern = re.compile('^[^\S\x0a\x0d]*(\'[\w\d]+([^\S\x0a\x0d]*[\w\d]*)*\')[^\S\x0a\x0d]*$', re.I | re.M)


    def loadIndex(self, directory):
        return InvertedIndexReader(directory)


    def index(self, directory):
        indexer = FileIndexer(directory, self.__prep)
        indexer.index()


    def __booleanSearch(self, query):
        # TODO: implement bool query parser
        # operator precedence: STAR > NOT > AND > OR
        p = BooleanQueryParser(query)
        print(p)

        if Operator.STAR in p.get():
            print("STAR operator found: prefixSearch needed")
        return []


    def __prefixSearch(self, query):
        # TODO: implement prefix query parser
        return []


    def __phraseSearch(self, query):
        ii = self.loadIndex("data")
        queryTermTuples = self.__prep.processText(query.replace("'", ""))

        # determine documents with ordered consecutive query terms
        first = True
        cidTuples = {}
        for term, _ in queryTermTuples:
            if first:
                cidTuples = dict(ii.retrieve(term))
                first = False
            else:
                newCidTuples = dict(ii.retrieve(term))
                cidTuples = self.__documentsWithConsecutiveTerms(cidTuples, newCidTuples)

        return self.__loadDocumentTextForCids(cidTuples)


    def __keywordSearch(self, query):
        ii = self.loadIndex("data")
        queryTermTuples = self.__prep.processText(query)

        # assume multiple tokens in query are combined with OR operator
        allCidTuples = []
        for term, _ in queryTermTuples:
            cidTupleList = ii.retrieve(term)
            if cidTupleList:
                allCidTuples = allCidTuples + cidTupleList

        return self.__loadDocumentTextForCids([cid for cid, _ in allCidTuples])


    def __loadDocumentTextForCids(self, cids):
        results = []
        commentPointers = set()

        # get document pointers
        with DocumentMap(os.path.join("data", "documentMap.index")).open() as documentMap:
            for cid in cids:
                try:
                    commentPointers.add(documentMap.get(cid))
                except KeyError:
                    print(self.__class__.__name__ + ":", "comment", cid, "not found!")

        # load document text
        with CommentReader(os.path.join("data", "comments.data")).open() as cr:
            for pointer, rowData in enumerate(cr):
                if pointer in commentPointers:
                    results.append(rowData["comment_text"])

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


    def search(self, query):
        results = []
        if self.__boolQueryPattern.fullmatch(query):
            print("\n\n##### Boolean Query Search")
            results = self.__booleanSearch(query)

        elif self.__prefixQueryPattern.fullmatch(query):
            print("\n\n##### Prefix Search")
            results = self.__prefixSearch(query)

        elif self.__phraseQueryPattern.fullmatch(query):
            print("\n\n##### Phrase Search")
            results = self.__phraseSearch(query)

        else:
            if re.search('NOT|AND|OR|[*]', query):
                print("*** ERROR ***")
                #raise ValueError("Query not supported. Please use only one of the following Operators: '*', 'NOT', 'AND', 'OR'")
                return ["*** ERROR ***", "Query not supported. Please use only one of the following Operators or none: '*', 'NOT', 'AND', 'OR'"]

            else:
                print("\n\n##### Keyword Search")
                results = self.__keywordSearch(query)


        print("##### Query for >>>", query, "<<< returned", len(results), "comments")
        return results


    def printAssignment2QueryResults(self):
        print(prettyPrint(self.search("October")[:5]))
        print(prettyPrint(self.search("jobs")[:5]))
        print(prettyPrint(self.search("Trump")[:5]))
        print(prettyPrint(self.search("hate")[:5]))
    

    def printAssignment3QueryResults(self):
        #print(prettyPrint(self.search("hate")[:5]))
        #print(prettyPrint(self.search("prefix*")[:5]))
        #print(prettyPrint(self.search("party AND chancellor NOT europe")))

        #print(prettyPrint(self.search("party AND chancellor")[:5]))
        #print(prettyPrint(self.search("party NOT politics")[:5]))
        #print(prettyPrint(self.search("war OR conflict")[:5]))
        #print(prettyPrint(self.search("euro* NOT europe")[:5]))
        #print(prettyPrint(self.search("publi* OR moderation")[:5]))
        #print(prettyPrint(self.search("'the european union'")[:5]))
        print(prettyPrint(self.search("'christmas market'")))
        print(prettyPrint(self.search("'Republican legislation'")))
        print(prettyPrint(self.search("'truck confederate flag'")))



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
    se = SearchEngine()
    #se.index("data")
    se.printAssignment3QueryResults()
