import abc

class Pipeline:

    __head = None
    __tail = None

    __ctxFactory = None

    def __init__(self, ctxFactory):
        self.__ctxFactory = ctxFactory

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
        return self.__ctxFactory.createCtx(handler, self)

    def write(self, dataToPass):
        self.__head.invokeRead(dataToPass)


if __name__ == '__main__':
    pipe = Pipeline()
    pipe.addLast(Handler3("Change Datatype Handler"))
    pipe.addLast(Handler1("Forwarding Handler"))
    pipe.addLast(Handler2("Print Handler"))
    pipe.write("test data")
