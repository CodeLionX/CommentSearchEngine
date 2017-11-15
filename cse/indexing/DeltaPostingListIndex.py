from sys import getsizeof


"""
Inverted Index (delta - in memory)
Structure: Line Number in File -> Posting List
"""
class DeltaPostingListIndex(object):


    __pl = None
    __margin = 300
    __cidSize = 0
    __numCids = 0


    def __init__(self, cidSize=35): # import sys; cid = "14d2c537-d2ed-4e36-bf3d-a26f62c02370"; assert(sys.getsizeof(cid) == 85)
        self.__pl = {}
        self.__cidSize = cidSize
        self.__numCids = 0


    def retrieve(self, line):
        if line not in self.__pl:
            return None
        return self.__pl[line]


    def insert(self, line, cid):
        if line not in self.__pl:
            self.__pl[line] = []
        self.__pl[line].append(cid)
        self.__pl[line].sort()
        self.__numCids = self.__numCids + 1


    def clear(self):
        self.__pl = {}
        self.__numCids = 0


    def estimatedSize(self):
        return self.__sizeof__()


    def lines(self):
        return self.__pl.keys()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        self.insert(key, value)


    def __iter__(self):
        return self.__pl.__iter__()


    def __contains__(self, item):
        return self.__pl.__contains__(item)


    def __sizeof__(self):
        return int(getsizeof(self.__pl)
                + self.__cidSize * self.__numCids
                + self.__margin)
