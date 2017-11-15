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


    def retrieve(self, term):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
            return self.__mIndex[pointer]
        else:
            return None


    def terms(self):
        return [term for term in self.__dictionary]
