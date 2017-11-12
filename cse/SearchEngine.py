import abc
import os

from cse.lang import PreprocessorBuilder
from cse.lang.PreprocessorStep import PreprocessorStep
from cse.Index import (InvertedIndex, Index)
from cse.CommentReader import CommentReader

class SearchEngine():

    def index(self, directory):
        # preprocessing
        # - to lower case
        # - tokenization (remove punctuation)
        # - remove stopwords (https://github.com/igorbrigadir/stopwords)
        # - stemming (porter(2), porter very fast python wrapper: https://github.com/shibukawa/snowball_py) or lemmatization (i dont think we need this)

        # see: http://whoosh.readthedocs.io/en/latest/stemming.html (stemming from whoosh in separate package: https://pypi.python.org/pypi/stemming/1.0)

        # with nltk:
        prep = (
            PreprocessorBuilder()
            .useNltkTokenizer()
            #.useNltkStopwordList()
            .usePorterStemmer()
            .addCustomStepToEnd(CustomPpStep())
            .build()
        )
        #tokens = prep.processText("WordNet® is a large lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept. Synsets are interlinked by means of conceptual-semantic and lexical relations. The resulting network of meaningfully related words and concepts can be navigated with the browser. WordNet is also freely and publicly available for download. WordNet’s structure makes it a useful tool for computational linguistics and natural language processing.")
        #print(tokens)

        # lookup for articles file ids
        index = Index()
        index.loadJson("data/index.json")

        # to be created inverted index
        ii = InvertedIndex("data/invertedIndex.json")

        # for just one article
        randomCid = index.listCids()[0:1][0]
        filename = index.get(randomCid)["fileId"]
        self.__createIndexForArticle(ii, prep, filename)
        ii.save()

        # for all article
        """
        for cid in index.listCids():
            filename = index.get(cid)["fileId"]
            print("Processing file", filename)
            self.__createIndexForArticle(ii, prep, filename)
        ii.save()
        """


    def __createIndexForArticle(self, index, prep, filename):
        cr = CommentReader(os.path.join("data", "raw", filename))
        cr.open()
        fileData = cr.readData()

        for cid in fileData["comments"]:
            tokens = prep.processText(fileData["comments"][cid]["comment_text"])

            for token in set(tokens):
                index.insert(token, cid)

        cr.close()



    def loadIndex(self, directory):
        pass


    def search(self, query):
        results = []
        return results


    def printAssignment2QueryResults(self):
        print(self.search("October"))
        print(self.search("jobs"))
        print(self.search("Trump"))
        print(self.search("hate"))



class CustomPpStep(PreprocessorStep):

    def __init__(self):
        pass

    def process(self, token):
        return token if not token.startswith("//") else None

    def processAll(self, tokens):
        return [token for token in tokens if not token.startswith("//")]

        



#searchEngine = SearchEngine()
#searchEngine.printAssignment2QueryResults()
se = SearchEngine()
se.index("")
