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
