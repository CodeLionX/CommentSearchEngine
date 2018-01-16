from sys import getsizeof

from cse.indexing.posting.PostingList import PostingList

"""
Inverted Index (delta - in memory)
Structure: Term -> Posting List
Posting List Entry: (cid, tf, positionsList)
Positions List: [pos1, pos2, ...]
--> PostingsList: [(cid, tf, [pos1, pos2, ...]), ...]
idf is not calculated until a delta merge is performed (see InvertedIndexWriter for that)
"""
class DeltaIndex(object):

    ESTIMATION_MARGIN = 300


    def __init__(self, entrySize=42):
        self.__postingLists = {}
        self.__entrySize = entrySize
        self.__numCommentIds = 0


    def retrieve(self, term):
        if term not in self.__postingLists:
            return None
        return self.__postingLists[term]


    def insert(self, term, commentId, tf, positions):
        if term not in self.__postingLists:
            self.__postingLists[term] = PostingList()
        self.__postingLists[term].append(commentId, tf, positions)
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
                + DeltaIndex.ESTIMATION_MARGIN)


    def __len__(self):
        return self.__postingLists.__len__()
