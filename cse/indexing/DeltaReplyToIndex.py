from sys import getsizeof

from cse.indexing.PostingList import PostingList

"""
ReplyTo Index (delta - in memory)
Structure: Parent CID -> Replyed to CID List
ReplyTo List: [cid1, cid2, ...]
"""
class DeltaReplyToIndex(object):

    ESTIMATION_MARGIN = 300


    def __init__(self, entrySize=15):
        self.__replyToLists = {}
        self.__entrySize = entrySize
        self.__numCommentIds = 0


    def retrieve(self, parentCid):
        if parentCid not in self.__replyToLists:
            return None
        return self.__replyToLists[parentCid]


    def insert(self, parentCid, cid):
        if parentCid not in self.__replyToLists:
            self.__replyToLists[parentCid] = []
        self.__replyToLists[parentCid].append(cid)
        # should already be sorted:
        #self.__replyToLists[pointer].sort()
        self.__numCommentIds = self.__numCommentIds + 1


    def clear(self):
        self.__replyToLists = {}
        self.__numCommentIds = 0


    def estimatedSize(self):
        return self.__sizeof__()


    def lines(self):
        return self.__replyToLists.keys()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        #           key, cid
        self.insert(key, value)


    def __iter__(self):
        return self.__replyToLists.__iter__()


    def __contains__(self, item):
        return self.__replyToLists.__contains__(item)


    def __sizeof__(self):
        return int(getsizeof(self.__replyToLists)
                + len(self) * getsizeof([])
                + getsizeof(int) * self.__numCommentIds
                + DeltaReplyToIndex.ESTIMATION_MARGIN)


    def __len__(self):
        return self.__replyToLists.__len__()
