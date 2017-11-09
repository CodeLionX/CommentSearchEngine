from cse.lang.PreprocessorStep import PreprocessorStep

class NltkLemmatizer(PreprocessorStep):

    __lemmatizerType = None

    def __init__(self, LemmatizerType):
        self.__lemmatizerType = LemmatizerType


    @staticmethod
    def nltkDefault():
        from nltk.stem import WordNetLemmatizer
        return WordNetLemmatizer()


    def processAll(self, tokens):
        return [self.__lemmatizerType.lemmatize(token) for token in tokens]


    def process(self, token):
        return self.__lemmatizerType.lemmatize(token)

