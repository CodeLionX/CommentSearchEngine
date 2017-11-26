import threading
from cse.pipeline.Handler import Handler


class RemoveDuplicatesHandler(Handler):

    def __init__(self):
        super()
        self.__ids = set()
        self.__lock = threading.Lock()


    def process(self, ctx, data):
        ctx.write(data)

        with self.__lock:
            for id in self.__ids:
                data['comments'].pop(id, None)
            
            for id in data['comments']:
                self.__ids.add(id)



class DuplicateHandler(Handler):

    def __init__(self):
        super()
        self.__ids = {}
        self.__lock = threading.Lock()

    def getDuplicates(self):
        for id in self.__ids:
            print(id, self.__ids[id])

    def process(self, ctx, data):
        ctx.write(data)
        with self.__lock:
            for id in data['comments']:
                try:
                    self.__ids[id] = self.__ids[id] + 1
                except KeyError:
                    self.__ids[id] = 1
