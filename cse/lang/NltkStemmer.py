from cse.lang.PreprocessorStep import PreprocessorStep

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