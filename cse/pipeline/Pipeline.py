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


    def addFirst(self, handler):
        if handler is None:
            raise Exception("handler was None")
        else:
            print("adding handler " + str(handler))
            ctx = self.__createContext(handler)
            if self.__head is None or self.__tail is None:
                self.__init(ctx)
            else:
                self.__addFirst(ctx)
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

    
    def __addFirst(self, ctx):
        # set point of previous ctx
        self.__tail.nxt = ctx

        # set pointer of next ctx
        self.__head.prev = ctx

        # set pointer of ctx itself
        ctx.prev = self.__tail
        ctx.nxt = self.__head

        # set new tail pointer
        self._head = ctx


    def __createContext(self, handler):
        ctx = self.__ctxFactory.createCtx(handler, self)
        handler.registeredAt(ctx)
        return ctx


    def write(self, dataToPass):
        self.__head.invokeRead(dataToPass)
