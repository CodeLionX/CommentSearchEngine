from cse.lang.PreprocessorStep import PreprocessorStep

class NltkStemmer(PreprocessorStep):

    __stemmerType = None

    def __init__(self, stemmerType):
        self.__stemmerType = stemmerType


    @staticmethod
    def porter():
        from nltk.stem.porter import PorterStemmer
        return PorterStemmer()

    @staticmethod
    def porter2():
        from nltk.stem import SnowballStemmer
        return SnowballStemmer("english")


    def processAll(self, tokenTuples):
        return [(self.__stemmerType.stem(token), position) for token, position in tokenTuples]


    def process(self, tokenTuple):
        return (self.__stemmerType.stem(tokenTuple[0]), tokenTuple[1])
