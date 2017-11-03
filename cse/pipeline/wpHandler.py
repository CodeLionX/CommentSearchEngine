from cse.pipeline.Handler import Handler



class WpApiAdapterHandler(Handler):
    __wpApiAdapter = None

    def __init__(self, name, wpApiAdapter):
        super().__init__(name)
        self.__wpApiAdapter = wpApiAdapter

    def registeredAt(self, ctx):
        self.__wpApiAdapter.injectCtx(ctx)

    def process(self, ctx, data):
        raise Exception("This Adapter is the starting point of the pipeline, thus should not receive any data!")



class WpApiParserHandler(Handler):
    __wpApiParser = None

    def __init__(self, name, wpApiParser):
        super().__init__(name)
        self.__wpApiParser = wpApiParser

    def process(self, ctx, data):
        result = self.__wpApiParser.parse(
            comments=data["comments"],
            url=data["url"],
            assetId=data["assetId"],
            parentId=data["parentId"]
        )
        ctx.write(result)



class RemoveDuplicatesHandler(Handler):

    __ids = []

    def __init__(self):
        super().__init__("RemoveDuplicatesHandler")

    def getDuplicates(self):
        for id in self.__ids:
            print(id, self.__ids[id])

    def process(self, ctx, data):
        for id in self.__ids:
            data['comments'].pop(id, None)
        
        for id in data['comments']:
            self.__ids.append(id)
        
        ctx.write(data)



class DuplicateHandler(Handler):

    __ids = {}

    def __init__(self):
        super().__init__("DuplicateHandler")

    def getDuplicates(self):
        for id in self.__ids:
            print(id, self.__ids[id])

    def process(self, ctx, data):
        for id in data['comments']:
            try:
                self.__ids[id] = self.__ids[id] + 1
            except KeyError:
                self.__ids[id] = 1
        ctx.write(data)