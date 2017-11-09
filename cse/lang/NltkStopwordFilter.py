from cse.lang.PreprocessorStep import PreprocessorStep

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