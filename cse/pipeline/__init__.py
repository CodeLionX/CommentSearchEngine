"""
CSE - a web crawling and web searching application for news paper
comments written in Python

simple pipeline for data processing
"""

import abc

from cse.pipeline.SynchronousHandlerContext import SynchronousHandlerContext
from cse.pipeline.Pipeline import Pipeline


"""
Abstract class representing an handler processing data which flows
through the pipeline.
"""
class Handler(object, metaclass=abc.ABCMeta):
    __name = ""

    def __init__(self, name):
        self.__name = name

    @abc.abstractmethod
    def process(self, ctx, data):
        raise NotImplementedError(
            "Class %s doesn't implement process(), please do that yourself" %
            (self.__class__.__name__)
        )

    def __str__(self):
        return self.__name

class SyncedHandlerContextFactory:
    def createCtx(self, handler, pipeline):
        return SynchronousHandlerContext(handler, pipeline)
