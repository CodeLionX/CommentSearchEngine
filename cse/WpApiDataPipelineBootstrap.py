from cse.WpApiAdapter import WpApiAdapter
from cse.WpApiParser import WpApiParser
from cse.CSVWriter import CSVWriter
from cse.pipeline import (Pipeline, SyncedHandlerContextFactory, Handler)
from cse.pipeline.wpHandler import (WpApiAdapterHandler, WpApiParserHandler, ListenerHandler)

class WpApiDataPipelineBootstrap:

    __wasPipeBuild = False
    __wpApiAdapter = None
    __pipeline = None

    __listeners = []

    __countHandler = None

    def __init__(self):
        self.__wpApiAdapter = WpApiAdapter()
        self.__wasPipeBuild = False
        self.__countHandler = CountHandler("Counter")


    def setupPipeline(self, asynchronous=False):
        if self.__wasPipeBuild:
            return

        ctxFactory = None
        if not asynchronous:
            ctxFactory = SyncedHandlerContextFactory()
        else:
            raise Exception("Currently not supported")
            
        self.__pipeline = Pipeline(ctxFactory)
        self.__pipeline.addLast(WpApiAdapterHandler("WashingtonPost API Adapter", self.__wpApiAdapter)) # url/json -> recursive datastructures
        self.__pipeline.addLast(WpApiParserHandler("WashingtonPostParser", WpApiParser())) # recursive datastructures -> flat datastructures
        self.__pipeline.addLast(self.__countHandler)
        self.__pipeline.addLast(DebugHandler("DebugHandler"))
        self.__pipeline.addLast(ListenerHandler(self.__listeners)) # _ -> listeners

        self.__wasPipeBuild = True


    def process(self, url):
        if not self.__wasPipeBuild:
            raise Exception("Pipeline uninitialized! First init pipeline with setupPipeline()")
        self.__wpApiAdapter.loadComments(url)
        print(self.__countHandler.getCount())


    def registerDataListener(self, listener):
        if self.__wasPipeBuild:
            raise Exception("Pipeline already running! Can't add listeners at runtime")
        self.__listeners.append(listener)


    def unregisterDataListener(self, listener):
        if self.__wasPipeBuild:
            raise Exception("Pipeline already running! Can't remove listeners at runtime")
        self.__listeners.remove(listener)



class CountHandler(Handler):
    __count = 0

    def getCount(self):
        return self.__count

    def process(self, ctx, data):
        self.__count = self.__count + len(data["comments"])
        ctx.write(data)


class DebugHandler(Handler):
    def process(self, ctx, data):
        print(str(data)[0:50] + "[...]", len(data["comments"]))
        #print(data["url"][0:50], data["assetId"], len(data["comments"]), data["parentId"])
        ctx.write(data)


# just for testing
if __name__ == "__main__":
    writer = CSVWriter("data/file1")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    bs.registerDataListener(writer.printData)
    bs.setupPipeline()
    bs.process(url='https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html')
    writer.close()
