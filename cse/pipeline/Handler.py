import abc

"""
Abstract class representing an handler processing data which flows
through the pipeline.
"""
class Handler(object, metaclass=abc.ABCMeta):
    __name = ""

    def __init__(self):
        pass


    def __init__(self, name):
        self.__name = name


    def registeredAt(self, ctx):
        pass


    @abc.abstractmethod
    def process(self, ctx, data):
        """
        Calls to this method can be asynchronous and form different threads
        if AsynchronousHandlerContext is used. Be aware of that!
        """
        raise NotImplementedError(
            "Class %s doesn't implement process(), please do that yourself" %
            (self.__class__.__name__)
        )


    def __str__(self):
        if not self.__name:
            return self.__class__.__name__
        else:
            return self.__name
