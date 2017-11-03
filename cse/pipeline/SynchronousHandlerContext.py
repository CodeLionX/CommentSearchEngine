class SynchronousHandlerContext:
    handler = None
    pipeline = None
    nxt = None
    prev = None


    def __init__(self, handler, pipeline):
        self.handler = handler
        self.pipeline = pipeline


    def write(self, msg):
        self.__invokeNextRead(self.__findNextNode(), msg)


    def __invokeNextRead(self, nxt, msg):
        # add multithreading
        # start a new task before invoking next handler --> new HandlerContextClass
        nxt.invokeRead(msg)


    def invokeRead(self, msg):
        try:
            self.handler.process(self, msg)
        except Exception as e:
            print("Exception during processing of handler '" + str(self.handler) + "', cause: " + str(e))


    def __findNextNode(self):
        return self.nxt


    def __str__(self):
        return str(self.handler)
