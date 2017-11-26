import abc
import concurrent.futures


class Pipeline(object):

    __head = None
    __tail = None

    __ctxFactory = None
    __threadPoolExecutor = None


    def __init__(self, ctxFactory, threads=None):
        self.__ctxFactory = ctxFactory
        self.__threadPoolExecutor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)


    def schedule(self, task, ctx, msg):
        # returns a Future
        return self.__threadPoolExecutor.submit(task, ctx, msg)


    def shutdown(self):
        # this method is blocking!
        if self.__threadPoolExecutor:
            self.__threadPoolExecutor.shutdown()


    def write(self, dataToPass):
        self.__head.invokeRead(dataToPass)


    def addLast(self, handler):
        if handler is None:
            raise Exception("handler was None")
        else:
            print("   Pipeline: adding handler " + str(handler))
            ctx = self.__createContext(handler)
            if self.__head is None or self.__tail is None:
                self.__init(ctx)
            else:
                self.__addLast(ctx)


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
