from cse.pipeline import Handler

class SimpleConsolePrintHandler(Handler):
    def process(self, ctx, data):
        print(str(data))
        ctx.write(data)

class SimpleForwardHandler(Handler):
    def process(self, ctx, data):
        ctx.write(data)
