import abc

"""
Abstract class representing an handler processing data which flows
through the pipeline.
"""
class Handler(object, metaclass=abc.ABCMeta):
    __name = ""

    def __init__(self, name):
        self.__name = name

    def registeredAt(self, ctx):
        pass

    @abc.abstractmethod
    def process(self, ctx, data):
        raise NotImplementedError(
            "Class %s doesn't implement process(), please do that yourself" %
            (self.__class__.__name__)
        )

    def __str__(self):
        return self.__name
