import os

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.indexing import (InvertedIndexWriter, InvertedIndexReader)
from cse.indexing import DocumentMap
from cse.CommentReader import CommentReader


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
                positionList = tokenDict.get(token, default=[])
                positionList.append(position)
                positionList.sort()
                tokenDict[token] = positionList
            
            for token in tokenDict:
                index.insert(token, cid) # and also positionList = tokenDict[token]

        cr.close()


    def loadIndex(self, directory):
        return InvertedIndexReader(directory)


    def search(self, query):
        ii = self.loadIndex("data")
        queryTermTuples = self.__prep.processText(query)

        # assume multiple tokens in query are combined with OR operator
        allCids = []
        for term, position in queryTermTuples:
            cids = ii.retrieve(term)
            if cids and len(cids) > 0:
                allCids = allCids + cids

        #print("found", len(allCids), "documents")

        # read info from files
        documentMap = DocumentMap().loadJson(os.path.join("data", "index.json"))
        fileIdCids = {}
        for cid in allCids:
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


    def printAssignment2QueryResults(self):
        print(prettyPrint(self.search("October")[:5]))
        print(prettyPrint(self.search("jobs")[:5]))
        print(prettyPrint(self.search("Trump")[:5]))
        print(prettyPrint(self.search("hate")[:5]))



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
    se.printAssignment2QueryResults()
