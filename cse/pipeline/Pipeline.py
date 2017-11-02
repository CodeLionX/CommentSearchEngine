import abc

class Pipeline:

    __head = None
    __tail = None

    def __init__(self):
        pass

    def addLast(self, handler):
        if handler is None:
            raise Exception("handler was None")
        else:
            print("adding handler " + str(handler))
            ctx = self.__createContext(handler)
            if self.__head is None or self.__tail is None:
                self.__init(ctx)
            else:
                self.__addLast(ctx)
            print("new head: " + str(self.__head) + ", new tail: " + str(self.__tail))

    def __init(self, ctx):
        # change pointers to both point to same ctx
        self.__head = ctx
        self.__tail = ctx

        # set pointer of ctx itself
        ctx.nxt = ctx
        ctx.prev = ctx


    def __addLast(self, ctx):
        # set point of previous ctx
        self.__tail.nxt = ctx

        # set pointer of next ctx
        self.__head.prev = ctx

        # set pointer of ctx itself
        ctx.prev = self.__tail
        ctx.nxt = self.__head

        # set new tail pointer
        self.__tail = ctx

    def __createContext(self, handler):
        return SynchronousHandlerContext(handler, self)

    def write(self, dataToPass):
        self.__head.invokeRead(dataToPass)


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

class Handler1(Handler):
    def __init__(self, name):
        super().__init__(name)

    def process(self, ctx, data):
        ctx.write(data)


class Handler2(Handler):
    def __init__(self, name):
        super().__init__(name)

    def process(self, ctx, data):
        print(str(data))

class Handler3(Handler):
    def __init__(self, name):
        super().__init__(name)

    def process(self, ctx, data):
        ctx.write({"data":[data]})



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
            print("Exception during processing of handler" + str(self.handler) + ", origin: " + str(e))

    def __findNextNode(self):
        return self.nxt

    def __str__(self):
        return str(self.handler)


if __name__ == '__main__':
    pipe = Pipeline()
    pipe.addLast(Handler3("Change Datatype Handler"))
    pipe.addLast(Handler1("Forwarding Handler"))
    pipe.addLast(Handler2("Print Handler"))
    pipe.write("test data")
