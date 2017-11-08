from cse.pipeline.Handler import Handler


class RemoveDuplicatesHandler(Handler):

    __ids = []

    def __init__(self):
        super()

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
        super()

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