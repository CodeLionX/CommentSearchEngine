import os

from cse.indexing import PostingList
from cse.indexing.Dictionary import Dictionary
from cse.indexing.posting.MainIndex import MainIndex as MainPosting
from cse.indexing.replyto.MainIndex import MainIndex as MainReplyTo


class InvertedIndexReader(object):


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__mIndex = MainPosting(os.path.join(filepath, "postingLists.index"))
        self.__replyToDictionary = Dictionary(os.path.join(filepath, "replyToDictionary.index"))
        self.__mReplyToIndex = MainReplyTo(os.path.join(filepath, "replyToLists.index"))


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


    def numberOfDistinctTerms(self):
        return len(self.__dictionary)


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.close()
