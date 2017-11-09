import abc

from cse.lang import PreprocessorBuilder

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
            .useNltkStopwordList()
            .usePorterStemmer()
            .build()
        )
        tokens = prep.processText("WordNet® is a large lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept. Synsets are interlinked by means of conceptual-semantic and lexical relations. The resulting network of meaningfully related words and concepts can be navigated with the browser. WordNet is also freely and publicly available for download. WordNet’s structure makes it a useful tool for computational linguistics and natural language processing.")
        print(tokens)


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



#searchEngine = SearchEngine()
#searchEngine.printAssignment2QueryResults()
