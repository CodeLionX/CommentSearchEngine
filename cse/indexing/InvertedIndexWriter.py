import os
import math

from cse.WeightCalculation import calcTf
from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainPostingListIndex import MainPostingListIndex
from cse.indexing.DeltaPostingListIndex import DeltaPostingListIndex


class InvertedIndexWriter(object):


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__dIndex = DeltaPostingListIndex()
        self.__mIndex = MainPostingListIndex(os.path.join(filepath, "postingLists.index"))
        self.__calls = 0
        self.__nDocuments = 0


    def __shouldDeltaMerge(self):
        # check memory usage
        if self.__dIndex.estimatedSize() > (50 * 1024*1024):
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()
        self.__mIndex.close()


    def insert(self, term, commentId, nTerms, positions):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
        else:
            pointer = self.__dictionary.nextFreeLinePointer()
            self.__dictionary[term] = pointer

        self.__dIndex.insert(
            pointer, 
            commentId, 
            calcTf(nTerms, len(positions)), 
            positions
        )

        if self.__calls % (1000 * 50) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1   


    def terms(self):
        return [term for term in self.__dictionary]


    def deltaMerge(self):
        print("!! delta merge !!")
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / 1024 / 1024, "mb")
        self.__mIndex.mergeInDeltaIndex(self.__dIndex, self.__nDocuments)
        self.__dIndex.clear()


    def incDocumentCounter(self):
        self.__nDocuments += 1
