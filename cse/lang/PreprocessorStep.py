import abc

class PreprocessorStep(object, metaclass=abc.ABCMeta):


    @abc.abstractmethod
    def processAll(self, tokens):
        return tokens


    @abc.abstractmethod
    def process(self, token):
        return token