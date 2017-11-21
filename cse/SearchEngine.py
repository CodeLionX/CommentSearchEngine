import os
import re

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.indexing import (InvertedIndexWriter, InvertedIndexReader)
from cse.indexing import DocumentMap
from cse.CommentReader import CommentReader
from cse.BooleanQueryParser import (BooleanQueryParser, Operator)


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


    def index(self, directory):
        # lookup for article file ids
        documentMap = DocumentMap()
        documentMap.loadJson(os.path.join(directory, "index.json"))

        # to be created inverted index
        ii = InvertedIndexWriter(directory)


        # for just one article
        """
        randomCid = documentMap.listCids()[0:1][0]
        filename = documentMap.get(randomCid)["fileId"]
        self.__createIndexForArticle(ii, prep, filename)
        ii.close()
        """

        # for all articles
        filenames = []
        for cid in documentMap.listCids():
            filenames.append(documentMap.get(cid)["fileId"])

        for filename in set(filenames):
            print("Processing file", filename)
            self.__createIndexForArticle(ii, filename)

        ii.close()


    def __createIndexForArticle(self, index, filename):
        cr = CommentReader(os.path.join("data", "raw", filename))
        cr.open()
        fileData = cr.readData()

        for cid in fileData["comments"]:
            tokenTuples = self.__prep.processText(fileData["comments"][cid]["comment_text"])

            tokenDict = {}
            for token, position in tokenTuples:
                positionList = tokenDict.get(token, [])
                positionList.append(position)
                positionList.sort()
                tokenDict[token] = positionList

            for token in tokenDict:
                index.insert(token, cid, tokenDict[token]) # and also positionList = tokenDict[token]

        cr.close()


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
        # TODO: implement phrase search
        return []


    def __keywordSearch(self, query):
        ii = self.loadIndex("data")
        queryTermTuples = self.__prep.processText(query)

        # assume multiple tokens in query are combined with OR operator
        allCids = []
        for term, position in queryTermTuples:
            cidTupleList = ii.retrieve(term)
            if cidTupleList:
                allCids = allCids + cidTupleList

        #print("found", len(allCids), "documents")

        # read info from files
        documentMap = DocumentMap().loadJson(os.path.join("data", "index.json"))
        fileIdCids = {}
        for cid, _ in allCids:
            meta = documentMap.get(cid)
            if meta["fileId"] not in fileIdCids:
                fileIdCids[meta["fileId"]] = []
            fileIdCids[meta["fileId"]].append(cid)

        #print("distributed in", len(fileIdCids), "files")

        # get comments
        results = []
        for fileId in fileIdCids:
            #print("  processing file", fileId)
            cr = CommentReader(os.path.join("data", "raw", fileId))
            cr.open()
            fileData = cr.readData()

            for cid in fileData["comments"]:
                if(cid in set(fileIdCids[fileId])):
                    results.append(fileData["comments"][cid]["comment_text"])

            cr.close()
        
        print("\n\n##### query for", query, ", comments found:", len(results))
        return results


    def loadIndex(self, directory):
        return InvertedIndexReader(directory)


    def search(self, query):
        if self.__boolQueryPattern.fullmatch(query):
            print("Boolean Query Search")
            return self.__booleanSearch(query)
        elif self.__prefixQueryPattern.fullmatch(query):
            print("Prefix Search")
            return self.__prefixSearch(query)
        elif self.__phraseQueryPattern.fullmatch(query):
            print("Phrase Search")
            return self.__phraseSearch(query)
        else:
            if re.search('NOT|AND|OR|[*]', query):
                print("*** ERROR ***")
                #raise ValueError("Query not supported. Please use only one of the following Operators: '*', 'NOT', 'AND', 'OR'")
                return ["*** ERROR ***", "Query not supported. Please use only one of the following Operators or none: '*', 'NOT', 'AND', 'OR'"]
            else:
                print("Keyword Search")
                return self.__keywordSearch(query)


    def printAssignment2QueryResults(self):
        print(prettyPrint(self.search("October")[:5]))
        print(prettyPrint(self.search("jobs")[:5]))
        print(prettyPrint(self.search("Trump")[:5]))
        print(prettyPrint(self.search("hate")[:5]))
    

    def printAssignment3QueryResults(self):
        print(prettyPrint(self.search("prefix*")[:5]))
        print(prettyPrint(self.search("party AND chancellor NOT europe")))

        print(prettyPrint(self.search("party AND chancellor")[:5]))
        print(prettyPrint(self.search("party NOT politics")[:5]))
        print(prettyPrint(self.search("war OR conflict")[:5]))
        print(prettyPrint(self.search("euro* NOT europe")[:5]))
        print(prettyPrint(self.search("publi* OR moderation")[:5]))
        print(prettyPrint(self.search("'the european union'")[:5]))
        print(prettyPrint(self.search("'christmas market'")))








class OrTerm(object):

    def __init__(self):
        self.__terms = terms

    def parse(self, term):
        terms = term.replace("OR")
        self.__terms = terms


def prettyPrint(l):
    return "\t" + "\n\t".join([t.replace("\n", "\\n") for t in l])



class CustomPpStep(PreprocessorStep):

    def __init__(self):
        pass

    def process(self, tokenTuple):
        return tokenTuple if not tokenTuple[0].startswith("//") else None

    def processAll(self, tokenTuples):
        return [(token, position) for token, position in tokenTuples if not token.startswith("//")]



#searchEngine = SearchEngine()
#searchEngine.printAssignment2QueryResults()

if __name__ == '__main__':
    se = SearchEngine()
    #se.index("data")
    se.printAssignment3QueryResults()
