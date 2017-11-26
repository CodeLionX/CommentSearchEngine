class AsynchronousHandlerContext(object):
    handler = None
    pipeline = None
    nxt = None
    prev = None


    def __init__(self, handler, pipeline):
        self.handler = handler
        self.pipeline = pipeline


    def write(self, msg):
        if str(self.handler) == "WpApiAdapter":
            print("API Adapter writes to pipeline")
        self.__invokeNextRead(self.__findNextNode(), msg)


    def __invokeNextRead(self, nxt, msg):
        nxt.invokeRead(msg)


    def invokeRead(self, msg):
        print(str(self), "received invokeRead")
        # asynchronous over pipeline scheduler
        try:
            self.pipeline.schedule(self.handler.process, self, msg)
        except Exception as e:
            print("Exception during processing of handler '" + str(self.handler) + "', cause: " + str(e))


    def __findNextNode(self):
        return self.nxt


    def __str__(self):
        return "AsynchronousHandlerContext for " + str(self.handler)
