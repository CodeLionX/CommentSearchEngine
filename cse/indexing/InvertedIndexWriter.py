import os
import math

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


    def __calculateTf(self, nAllTerms, nTerm):
        return math.log10(nTerm/float(nAllTerms))


    def calculateIdf(self, pointer, nTermDocuments):
        """
        First approach!!!
        TODO: Optimize this!
              Solution could be to move the idf value also to the postingLists file, before the real postingList
              for each term. E.g. `(idf, [(cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])])` or
              `[idf, (cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])]`
        """
        idf = math.log10(self.__nDocuments/float(nTermDocuments))
        for term in self.__dictionary:
            p, _ = self.__dictionary[term]
            if p == pointer:
                self.__dictionary[term] = (p, idf)
                return

        raise ValueError("term for pointer", pointer, "not found!!!")


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()
        self.__mIndex.close()


    def insert(self, term, commentId, nTerms, positions):
        if term in self.__dictionary:
            pointer, _ = self.__dictionary[term]
        else:
            pointer = self.__dictionary.nextFreeLinePointer()
            # initialize idf with 0
            self.__dictionary[term] = (pointer, 0)

        self.__dIndex.insert(
            pointer, 
            commentId, 
            self.__calculateTf(nTerms, len(positions)), 
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
        self.__mIndex.mergeInDeltaIndex(self.__dIndex, self.calculateIdf)
        self.__dIndex.clear()


    def incDocumentCounter(self):
        self.__nDocuments += 1
