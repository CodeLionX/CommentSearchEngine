import os

from os import remove
from tempfile import mkstemp
from shutil import move

from cse.WeightCalculation import calcTf
from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainPostingListIndex import MainPostingListIndex
from cse.indexing.DeltaPostingListIndex import DeltaPostingListIndex
from cse.indexing.PostingList import PostingList


class InvertedIndexWriter(object):

    MB = 1024*1024
    # threshold for delta index to reside in memory
    # if the memory consumption of the delta index itself gets higher than this threshold
    # a delta merge is performend and the index will be written to disk
    MEMORY_THRESHOLD = 500 * MB     # 500 MB
    # entry size estimation for simple heursitic to determine memory consumption of the 
    # delta index
    POSTING_LIST_ENTRY_SIZE = 30    #  30 B


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__dIndex = DeltaPostingListIndex(entrySize=InvertedIndexWriter.POSTING_LIST_ENTRY_SIZE)
        self.__mIndex = MainPostingListIndex(os.path.join(filepath, "postingLists.index"))
        self.__calls = 0
        self.__nDocuments = 0


    def __shouldDeltaMerge(self):
        print("delta check:", self.__dIndex.estimatedSize())
        # check memory usage
        if self.__dIndex.estimatedSize() > InvertedIndexWriter.MEMORY_THRESHOLD:
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
            int(commentId),
            calcTf(nTerms, len(positions)),
            positions
        )

        if self.__calls % (InvertedIndexWriter.MEMORY_THRESHOLD / 100) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1


    def terms(self):
        return [term for term in self.__dictionary]


    def deltaMerge(self):
        print("!! delta merge !!")
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / InvertedIndexWriter.MB, "mb")

        if not self.__dIndex:
            print(self.__class__.__name__ + ":", "no delta merge needed")
            return

        fd, tempFilePath = mkstemp(text=True)
        visited = set()

        #with open(tempFilePath, 'w', newline='', encoding="utf-8") as tempFile:
        with open(tempFilePath, 'wb') as tempFile:
            for i, plLine in enumerate(self.__postingLists):
                postingList = PostingList.decode(plLine)
                if i in self.__dIndex:
                    postingList = postingList.merge(self.__dIndex[i])
                    #print("merging pointer", i)

                postingList.updateIdf(calcIdf(self.__nDocuments, postingList.numberOfPostings()))
                tempFile.write(PostingList.encode(postingList))
                visited.add(i)

            for pointer in sorted(self.__dIndex):
                if pointer not in visited:
                    postingList = self.__dIndex[pointer]
                    postingList.updateIdf(calcIdf(self.__nDocuments, postingList.numberOfPostings()))
                    tempFile.write(PostingList.encode(postingList))
                    #print("adding pointer", pointer)

        tempFile.close()
        os.close(fd)

        added = len(set(self.__dIndex.lines()) - visited)
        merged = len(set(self.__dIndex.lines())) - added
        print(self.__class__.__name__ + ":", "merged", merged, "posting lists")
        print(self.__class__.__name__ + ":", "added", added, "new posting lists")

        self.__postingLists.close()
        del self.__postingLists
        remove(self.__postingListsFilename)
        move(tempFilePath, self.__postingListsFilename)
        #self.__postingLists = open(self.__postingListsFilename, 'r', newline='', encoding="utf-8")
        self.__postingLists = open(self.__postingListsFilename, 'rb')
        print(self.__class__.__name__ + ":", "new postinglist index file has size:", os.path.getsize(self.__postingListsFilename) / 1024 / 1024, "mb")

        self.__dIndex.clear()


    def incDocumentCounter(self):
        self.__nDocuments += 1
