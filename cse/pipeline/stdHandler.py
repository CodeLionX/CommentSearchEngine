from cse.pipeline.Handler import Handler

class SimpleConsolePrintHandler(Handler):
    def __init__(self):
        super().__init__("Simple Console Print Handler")

    def process(self, ctx, data):
        print(str(data))
        ctx.write(data)


class SimpleForwardHandler(Handler):
    def __init__(self):
        super().__init__("Simple Forward Handler")

    def process(self, ctx, data):
        ctx.write(data)

class SinkHandler(Handler):
    def __init__(self):
        super().__init__("Sink Handler")

    def process(self, ctx, data):
        pass
