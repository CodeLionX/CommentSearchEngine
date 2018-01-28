import os
import msgpack

from cse.indexing.Dictionary import Dictionary
from cse.indexing.PostingList import PostingList
from cse.indexing.MainIndex import MainIndex

from cse.indexing.commons import (
    POSTING_DICT_NAME,
    POSTING_LISTS_NAME,
    REPLYTO_DICT_NAME,
    REPLYTO_LISTS_NAME
)


class IndexReader(object):


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, POSTING_DICT_NAME))
        self.__mIndex = MainIndex(os.path.join(filepath, POSTING_LISTS_NAME), PostingList.decode)
        self.__replyToDictionary = Dictionary(os.path.join(filepath, REPLYTO_DICT_NAME))
        self.__mReplyToIndex = MainIndex(os.path.join(filepath, REPLYTO_LISTS_NAME), msgpack.unpackb)


    def close(self):
        self.__dictionary.close()
        self.__mIndex.close()
        self.__replyToDictionary.close()
        self.__mReplyToIndex.close()


    def retrieve(self, term):
        if term in self.__dictionary:
            pointer, size = self.__dictionary[term]
            return self.__mIndex[(pointer, size)]
        else:
            return PostingList()


    def repliedTo(self, parentCid):
        if parentCid in self.__replyToDictionary:
            pointer, size = self.__replyToDictionary[parentCid]
            return self.__mReplyToIndex[(pointer, size)]
        else:
            return []


    def postingList(self, term):
        return self.retrieve(term).postingList()


    def tf(self, term, commentId):
        if term in self.__dictionary:
            postingList = self.retrieve(term)
            for cid, tf, _ in postingList.postingList():
                if cid == commentId:
                    return tf

        return 0


    def idf(self, term):
        return self.retrieve(term).idf()


    def tfIdf(self, term, commentId):
        if term not in self.__dictionary:
            return (0, 0)

        postingList = self.retrieve(term)
        for cid, tf, _ in postingList.postingList():
            if cid == commentId:
                return (tf, postingList.idf())

        return (0, postingList.idf())


    def terms(self):
        return [term for term in self.__dictionary]

    def parentCids(self):
        return [cid for cid in self.__replyToDictionary]

    def numberOfDistinctTerms(self):
        return len(self.__dictionary)


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    reader = IndexReader("data")
    for i in range(0, 2000, 10):
        replies = reader.repliedTo(i)
        if replies:
            print("Parent", i, " has following replies:", replies)
