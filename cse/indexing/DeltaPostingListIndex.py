from sys import getsizeof

from cse.indexing.PostingList import PostingList

"""
Inverted Index (delta - in memory)
Structure: Line Number in File -> Posting List
Posting List Entry: (cid, tf, positionsList)
Positions List: [pos1, pos2, ...]
--> PostingsList: [(cid, tf, [pos1, pos2, ...]), ...]
idf is not calculated until a delta merge is performed (see MainPostingListIndex for that)
"""
class DeltaPostingListIndex(object):

    __margin = 300


    def __init__(self, entrySize=42): # import sys; cid = "14d2c537-d2ed-4e36-bf3d-a26f62c02370"; assert(sys.getsizeof(cid) == 85)
        self.__postingLists = {}
        self.__entrySize = entrySize
        self.__numCommentIds = 0


    def retrieve(self, pointer):
        if pointer not in self.__postingLists:
            return None
        return self.__postingLists[pointer]


    def insert(self, pointer, commentId, tf, positions):
        if pointer not in self.__postingLists:
            self.__postingLists[pointer] = PostingList()
        self.__postingLists[pointer].append(commentId, tf, positions)
        # should already be sorted:
        #self.__postingLists[pointer].sort()
        self.__numCommentIds = self.__numCommentIds + 1


    def clear(self):
        self.__postingLists = {}
        self.__numCommentIds = 0


    def estimatedSize(self):
        return self.__sizeof__()


    def lines(self):
        return self.__postingLists.keys()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        #           key, cid     , tf      , positionsList
        self.insert(key, value[0], value[1], value[2])


    def __iter__(self):
        return self.__postingLists.__iter__()


    def __contains__(self, item):
        return self.__postingLists.__contains__(item)


    def __sizeof__(self):
        return int(getsizeof(self.__postingLists)
                + self.__entrySize * self.__numCommentIds
                + self.__margin)


    def __len__(self):
        return self.__postingLists.__len__()
