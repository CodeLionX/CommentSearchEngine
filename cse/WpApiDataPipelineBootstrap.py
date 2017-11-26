from threading import Lock
from cse.WpApiAdapter import WpApiAdapter
from cse.WpApiParser import WpApiParser
from cse.pipeline import (Pipeline, SyncedHandlerContextFactory, AsyncedHandlerContextFactory, Handler)
from cse.pipeline.wpHandler import (DuplicateHandler, RemoveDuplicatesHandler)

class WpApiDataPipelineBootstrap(Handler):


    def __init__(self):
        super(WpApiDataPipelineBootstrap, self).__init__("PipelineBootstrap for data listeners")
        self.__pipeline = None
        self.__wpApiAdapter = WpApiAdapter()
        self.__countHandler = CountHandler("Counter")
        self.__listeners = []
        self.__listenersLock = Lock()
        self.__wasPipeBuild = False


    def setupPipeline(self, asynchronous=False):
        if self.__wasPipeBuild:
            return

        if not asynchronous:
            self.__pipeline = Pipeline(SyncedHandlerContextFactory())
        else:
            self.__pipeline = Pipeline(AsyncedHandlerContextFactory(), 4)
            #raise Exception("Currently not supported")

        self.__pipeline.addLast(self.__wpApiAdapter) # url/json -> recursive datastructures
        self.__pipeline.addLast(WpApiParser()) # recursive datastructures -> flat datastructures
        self.__pipeline.addLast(RemoveDuplicatesHandler())
        #self.__pipeline.addLast(self.__countHandler) # debug: counts all comments
        #self.__pipeline.addLast(DebugHandler("DebugHandler")) # debug: shows some processing output
        self.__pipeline.addLast(self) # _ -> listeners

        self.__wasPipeBuild = True


    # Overrides Handler.process()
    def process(self, ctx, data):
        with self.__listenersLock:
            for callback in self.__listeners:
                callback(data)
        
        print("wrote to csv")


    def crawlComments(self, url):
        if not self.__wasPipeBuild:
            raise Exception("Pipeline uninitialized! First init pipeline with setupPipeline()")
        self.__countHandler.reset()
        self.__wpApiAdapter.loadComments(url)
        #print("Processed comments with new API: " + str(self.__countHandler.get()))


    def registerDataListener(self, listener):
        print("   adding " + str(listener))
        self.__listeners.append(listener) # append() is atomic


    def unregisterDataListener(self, listener):
        with self.__listenersLock:
            print("   removing " + str(listener))
            self.__listeners.remove(listener)


    def shutdown(self):
        self.__pipeline.shutdown()



class CountHandler(Handler):
    
    def __init__(self, name):
        super(CountHandler, self).__init__(name)
        self.__count = 0
        self.__lock = Lock()

    def get(self):
        return self.__count

    def reset(self):
        with self.__lock:
            self.__count = 0

    def process(self, ctx, data):
        ctx.write(data)
        with self.__lock:
            self.__count = self.__count + len(data["comments"])



class DebugHandler(Handler):
    def process(self, ctx, data):
        print(str(data)[0:50] + "[...]", len(data["comments"]))
        #print(data["url"][0:50], data["assetId"], len(data["comments"]), data["parentId"])
        ctx.write(data)



def perfTest():
    import time
    from datetime import timedelta
    from cse.CommentWriter import CommentWriter

    firstStart = time.clock()
    writer = CommentWriter("data/perfTest1")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    bs.registerDataListener(writer.printData)
    bs.setupPipeline(asynchronous=False)
    bs.crawlComments(url='https://www.washingtonpost.com/politics/the-shrinking-profile-of-jared-kushner/2017/11/25/5baf7068-c103-11e7-af84-d3e2ee4b2af1_story.html')
    writer.close()
    bs.shutdown()
    firstEnd = time.clock()

    secondStart = time.clock()
    writer = CommentWriter("data/perfTest2")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    bs.registerDataListener(writer.printData)
    bs.setupPipeline(asynchronous=True)
    bs.crawlComments(url='https://www.washingtonpost.com/politics/the-shrinking-profile-of-jared-kushner/2017/11/25/5baf7068-c103-11e7-af84-d3e2ee4b2af1_story.html')
    writer.close()
    bs.shutdown()
    secondEnd = time.clock()

    print("\nTimings:")
    print("Synchronous:  " + str(timedelta(seconds=firstEnd-firstStart)))
    print("Asynchronous: " + str(timedelta(seconds=secondEnd-secondStart)))


def dataListenerTest():
    from cse.CommentWriter import CommentWriter
    writer = CommentWriter("data/dataListenerTest1")
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
    writer = CommentWriter("data/dataListenerTest2")
    writer.open()
    writer.printHeader()
    bs.registerDataListener(writer.printData)
    bs.crawlComments(url='https://www.washingtonpost.com/news/wonk/wp/2017/11/02/winners-and-losers-in-the-gop-tax-plan/')
    writer.close()
    print("shutting down...")
    bs.shutdown()
    print("..finished")


def syncTest():
    from cse.CommentWriter import CommentWriter
    writer = CommentWriter("data/syncTest")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    bs.registerDataListener(writer.printData)
    bs.setupPipeline()
    bs.crawlComments(url='https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html')
    writer.close()
    bs.shutdown()


def asyncTest():
    import time
    from cse.CommentWriter import CommentWriter
    writer = CommentWriter("data/asyncTest")
    writer.open()
    writer.printHeader()
    bs = WpApiDataPipelineBootstrap()
    bs.registerDataListener(writer.printData)
    bs.setupPipeline(asynchronous=True)
    bs.crawlComments(url='https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html')
    writer.close()
    time.sleep(10)
    bs.shutdown()


# just for testing
if __name__ == "__main__":
    #syncTest()
    asyncTest()
