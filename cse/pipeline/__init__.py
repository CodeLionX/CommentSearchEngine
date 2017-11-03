"""
CSE - a web crawling and web searching application for news paper
comments written in Python

simple pipeline for data processing
"""

import abc

from cse.pipeline.SynchronousHandlerContext import SynchronousHandlerContext
from cse.pipeline.Pipeline import Pipeline
from cse.pipeline.stdHandler import (SimpleConsolePrintHandler, SimpleForwardHandler, SinkHandler)
from cse.pipeline.Handler import Handler


class SyncedHandlerContextFactory:
    def createCtx(self, handler, pipeline):
        return SynchronousHandlerContext(handler, pipeline)


if __name__ == '__main__':
    print("Testing pipeline...")
    pipe = Pipeline(SyncedHandlerContextFactory())
    pipe.addLast(SimpleForwardHandler())
    pipe.addLast(SimpleConsolePrintHandler())
    pipe.addLast(SinkHandler())
    pipe.write("test data")
