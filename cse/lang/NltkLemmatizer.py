from cse.lang.PreprocessorStep import PreprocessorStep

class NltkLemmatizer(PreprocessorStep):

    __lemmatizerType = None

    def __init__(self, LemmatizerType):
        self.__lemmatizerType = LemmatizerType


    @staticmethod
    def nltkDefault():
        from nltk.stem import WordNetLemmatizer
        return WordNetLemmatizer()


    def processAll(self, tokenTuples):
        return [(self.__lemmatizerType.lemmatize(token), position) for token, position in tokenTuples]


    def process(self, tokenTuple):
        return (self.__lemmatizerType.lemmatize(tokenTuple[0]), tokenTuple[1])

