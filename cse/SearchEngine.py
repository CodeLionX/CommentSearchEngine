class SearchEngine(object):

    def index(self, directory):
        # preprocessing
        # - to lower case
        # - tokenization (remove punctuation)
        # - remove stopwords (https://github.com/igorbrigadir/stopwords)
        # - stemming (porter(2), porter very fast python wrapper: https://github.com/shibukawa/snowball_py) or lemmatization (i dont think we need this)

        # see: http://whoosh.readthedocs.io/en/latest/stemming.html (stemming from whoosh in separate package: https://pypi.python.org/pypi/stemming/1.0)

        # with nltk:
        """
        from nltk.stem import PorterStemmer
        from nltk.tokenize import sent_tokenize, word_tokenize
        ps = PorterStemmer()

        words = word_tokenize("very long text about interesting things")

        for w in words:
            print(ps.stem(w))
        """
        pass

    def loadIndex(self, directory):
        pass

    def search(self, query):
        results = []
        return results

    def printAssignment2QueryResults(self):
        print self.search("October")
        print self.search("jobs")
        print self.search("Trump")
        print self.search("hate")

searchEngine = SearchEngine()
searchEngine.printAssignment2QueryResults()
