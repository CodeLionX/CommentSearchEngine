from threading import Lock
from cse.WpApiAdapter import WpApiAdapter
from cse.WpApiParser import WpApiParser
from cse.pipeline import (Pipeline, SyncedHandlerContextFactory, Handler)
from cse.pipeline.wpHandler import (DuplicateHandler, RemoveDuplicatesHandler)

class WpApiDataPipelineBootstrap(Handler):

    __wasPipeBuild = False
    __wpApiAdapter = None
    __pipeline = None

    __listeners = []
    __listenersLock = None

    __countHandler = None
    __duplicateHandler = None


    def __init__(self):
        super(WpApiDataPipelineBootstrap, self).__init__("PipelineBootstrap for data listeners")
        self.__wpApiAdapter = WpApiAdapter()
        self.__countHandler = CountHandler("Counter")
        self.__listenersLock = Lock()
        self.__wasPipeBuild = False


    def setupPipeline(self, asynchronous=False):
        if self.__wasPipeBuild:
            return

        ctxFactory = None
        if not asynchronous:
            ctxFactory = SyncedHandlerContextFactory()
        else:
            raise Exception("Currently not supported")
            
        self.__pipeline = Pipeline(ctxFactory)
        self.__pipeline.addLast(self.__wpApiAdapter) # url/json -> recursive datastructures
        self.__pipeline.addLast(WpApiParser()) # recursive datastructures -> flat datastructures
        self.__pipeline.addLast(RemoveDuplicatesHandler())
        #self.__pipeline.addLast(self.__duplicateHandler) # debug: count comment ids
        self.__pipeline.addLast(self.__countHandler) # debug: counts all comments
        #self.__pipeline.addLast(DebugHandler("DebugHandler")) # debug: shows some processing output
        self.__pipeline.addLast(self) # _ -> listeners

        self.__wasPipeBuild = True


    # Overrides Handler.process()
    def process(self, ctx, data):
        with self.__listenersLock:
            for callback in self.__listeners:
                callback(data)


    def crawlComments(self, url):
        if not self.__wasPipeBuild:
            raise Exception("Pipeline uninitialized! First init pipeline with setupPipeline()")
        self.__countHandler.reset()
        self.__wpApiAdapter.loadComments(url)
        print("Processed comments with new API: " + str(self.__countHandler.get()))


    def registerDataListener(self, listener):
        print("   adding " + str(listener))
        self.__listeners.append(listener) # append() is atomic


    def unregisterDataListener(self, listener):
        with self.__listenersLock:
            print("   removing " + str(listener))
            self.__listeners.remove(listener)



class CountHandler(Handler):
    __count = 0

    def get(self):
        return self.__count

    def reset(self):
        self.__count = 0

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
    from cse.CommentWriter import CommentWriter
    writer = CommentWriter("data/file1")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    printListener = writer.printData
    bs.registerDataListener(printListener)
    bs.setupPipeline()
    bs.crawlComments(url='https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html')
    bs.unregisterDataListener(printListener)
    writer.close()

    ## try changing data listener
    writer = CommentWriter("data/file2")
    writer.open()
    writer.printHeader()
    bs.registerDataListener(writer.printData)
    bs.crawlComments(url='https://www.washingtonpost.com/news/wonk/wp/2017/11/02/winners-and-losers-in-the-gop-tax-plan/?hpid=hp_hp-top-table-main_tax-winnerslosers-230pm%3Ahomepage%2Fstory&utm_term=.d2381570c5bc')
    writer.close()
