import os

from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainPostingListIndex import MainPostingListIndex


class InvertedIndexReader(object):


    __dictionary = None
    __dIndex = None
    __mIndex = None


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__mIndex = MainPostingListIndex(os.path.join(filepath, "postingLists.index"))


    def close(self):
        self.__dictionary.close()
        self.__mIndex.close()


    def retrieveAll(self, term):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
            return self.__mIndex[pointer]
        else:
            return (None, None)


    def retrievePostingList(self, term):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
            return [(cid, posList) for cid, tf, posList in self.__mIndex[pointer][1]]
        else:
            return None


    def tf(self, term, commentId):
        if term not in self.__dictionary:
            return 0

        pointer = self.__dictionary[term]
        _, pl = self.__mIndex[pointer]
        for cid, tf, _ in pl:
            if cid == commentId:
                return tf

        return 0


    def idf(self, term):
        if term not in self.__dictionary:
            return 0

        pointer = self.__dictionary[term]
        idf, _ = self.__mIndex[pointer]
        return idf


    def tfIdf(self, term, commentId):
        if term not in self.__dictionary:
            return None

        pointer = self.__dictionary.retrieve(term)
        idf, pl = self.__mIndex[pointer]
        for cid, tf, _ in pl:
            if cid == commentId:
                return (tf, idf)

        return (0, idf)


    def terms(self):
        return [term for term in self.__dictionary]


    def numberOfDistinctTerms(self):
        return len(self.__dictionary)


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.close()
