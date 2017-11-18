import abc

class PreprocessorStep(object, metaclass=abc.ABCMeta):


    @abc.abstractmethod
    def processAll(self, tokenTuples):
        return tokenTuples


    @abc.abstractmethod
    def process(self, tokenTuple):
        return tokenTuple