import abc

class SearchEngine():

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
        print(self.search("October"))
        print(self.search("jobs"))
        print(self.search("Trump"))
        print(self.search("hate"))



class PreprocessorBuilder(object):

    __useStopwords = False
    __useStemming = False
    __useLemmatizing = False

    __stopwords = []
    __tokenizer = None
    __stemmer = None
    __lemmatizer = None

    def __init__(self):
        self.__tokenizer = NltkTokenizer()

    def useNltkStopwordList(self):
        self.__useStopwords = True
        self.__stopwords = NltkStopwordFilter.english()
        return self

    def useCustomStopwordList(self, stopwords):
        self.__useStopwords = True
        self.__stopwords = stopwords
        return self

    def appendToStopwordList(self, stopwords):
        self.__useStopwords = True
        self.__stopwords.append(stopwords)
        return self

    def usePorterStemmer(self):
        self.__useStemming = True
        self.__stemmer = NltkStemmer(NltkStemmer.porter())
        return self

    def build(self):
        if self.__useStemming and self.__useLemmatizing:
            raise Exception("You can't use both Stemmer and Lemmatizer at the same time!")

        steps = []
        if self.__useStopwords:
            steps.append(NltkStopwordFilter(self.__stopwords))

        if self.__useStemming and not self.__useLemmatizing:
            steps.append(self.__stemmer)

        if self.__useLemmatizing and not self.__useStemming:
            steps.append(self.__lemmatizer)

        return Preprocessor(self.__tokenizer, steps)


class PreprocessorStep(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def processAll(self, tokens):
        return tokens

    @abc.abstractmethod
    def process(self, token):
        return token


class NltkTokenizer(object):

    def __init__(self):
        pass

    def tokenize(self, text):
        from nltk import word_tokenize, sent_tokenize
        import string
        
        # tokenize into sentences and sentences into lower case words
        tokens = [word.lower() for sent in sent_tokenize(text) for word in word_tokenize(sent)]
        # filter out punctuation
        tokens = filter(lambda word: word not in string.punctuation, tokens)
        # replace "n't" with "not"
        tokens = map(lambda word: word if word != "n't" else "not", tokens)
        return list(tokens)


class NltkStopwordFilter(PreprocessorStep):

    __stopwordlist = set()

    def __init__(self, stopwordList):
        # lookup is faster in a set than a list
        self.__stopwordlist = set(stopwordList)

    @staticmethod
    def english():
        from nltk.corpus import stopwords
        return stopwords.words("english")

    def processAll(self, tokens):
        return [token for token in tokens if token not in self.__stopwordlist]

    def process(self, token):
        return token if token not in self.__stopwordlist else None


class NltkStemmer(PreprocessorStep):

    def __init__(self, stemmerType):
        self.__stemmerType = stemmerType

    @staticmethod
    def porter():
        from nltk.stem.porter import PorterStemmer
        return PorterStemmer()

    def processAll(self, tokens):
        return [self.__stemmerType.stem(token) for token in tokens]

    def process(self, token):
        return self.__stemmerType.stem(token)


class Preprocessor(object):

    __tokenizer = None
    __steps = []

    def __init__(self, tokenizer, steps):
        self.__tokenizer = tokenizer
        self.__steps = steps

    def processText(self, comment):
        tokens = self.__tokenizer.tokenize(comment)

        ###### which way is faster?
        for step in self.__steps:
            tokens = step.processAll(tokens)
        ######
        pTokens = []
        for token in tokens:
            pT = token
            for step in self.__steps:
                pT = step.process(pT)
            pTokens.append(pT)
        tokens = pTokens
        ###### which way is faster?

        return tokens

"""
    def tokenize(self, comment):
        from nltk import word_tokenize, sent_tokenize
        import string

        # tokenize into sentences and sentences into lower case words
        tokens = [word.lower() for sent in sent_tokenize(comment) for word in word_tokenize(sent)]
        # filter out punctuation
        tokens = filter(lambda word: word not in string.punctuation, tokens)
        # replace "n't" with "not"
        tokens = map(lambda word: word if word != "n't" else "not", tokens)
        return list(tokens)

    def removeStopwords(self, tokens):
        from nltk.corpus import stopwords

        return self.applyStopwordFilter(tokens, stopwords.words("english"))

    def applyStopwordFilter(self, tokens, stopwords):
        stops = set(stopwords) # lookup is faster in a set than a list
        return [token for token in tokens if token not in stops]

    def stem(self, tokens):
        from nltk.stem.porter import PorterStemmer

        porter = PorterStemmer()
        return [porter.stem(token) for token in tokens]
"""


def main():
    prep = PreprocessorBuilder().useNltkStopwordList().usePorterStemmer().build()
    tokens = prep.processText("WordNet® is a large lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept. Synsets are interlinked by means of conceptual-semantic and lexical relations. The resulting network of meaningfully related words and concepts can be navigated with the browser. WordNet is also freely and publicly available for download. WordNet’s structure makes it a useful tool for computational linguistics and natural language processing.")
    print(tokens)

main()


#searchEngine = SearchEngine()
#searchEngine.printAssignment2QueryResults()
