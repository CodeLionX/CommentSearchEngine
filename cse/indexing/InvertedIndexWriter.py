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
    MEMORY_THRESHOLD = 50 * MB     # 500 MB
    # entry size estimation for simple heursitic to determine memory consumption of the
    # delta index
    POSTING_LIST_ENTRY_SIZE = 30    #  30 B


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__dIndex = DeltaPostingListIndex(entrySize=InvertedIndexWriter.POSTING_LIST_ENTRY_SIZE)
        self.__mIndexFilepath = os.path.join(filepath, "postingLists.index")
        self.__calls = 0
        self.__nDocuments = 0


    def __shouldDeltaMerge(self):
        print("delta size check [Bytes]:", self.__dIndex.estimatedSize())
        # check memory usage
        if self.__dIndex.estimatedSize() > InvertedIndexWriter.MEMORY_THRESHOLD:
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()


    def insert(self, term, commentId, nTerms, positions):
        self.__dIndex.insert(
            term,
            int(commentId),
            calcTf(nTerms, len(positions)),
            positions
        )

        if self.__calls % int(InvertedIndexWriter.MEMORY_THRESHOLD / 250) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1


    def terms(self):
        return [term for term in self.__dictionary]


    def deltaMerge(self):
        # quit method early if no values are in delta
        if not self.__dIndex:
            print(self.__class__.__name__ + ":", "no delta merge needed")
            return

        # init values
        mIndex = MainPostingListIndex(self.__mIndexFilepath)
        fh, tempFilePath = mkstemp(text=True)
        visited = set()
        merged, added = 0, 0

        # helper func
        def updateIdfAndWritePostingList(tempFile, postingList):
            postingList.updateIdf(self.__nDocuments)
            seekPosition = tempFile.tell()
            bytesWritten = tempFile.write(PostingList.encode(postingList))
            return seekPosition, bytesWritten

        # beginning of merge
        print("!! delta merge !!")
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / InvertedIndexWriter.MB, "mb")

        with open(tempFilePath, 'wb') as tempFile:
            # merge step 1: for each term in main update postingList (add delta and recalc idf)
            for term in sorted(self.__dictionary):
                pointer, size = self.__dictionary[term]
                postingList = mIndex.retrieve(pointer, size)

                if term in self.__dIndex:
                    postingList = postingList.merge(self.__dIndex[term])

                seekPosition, bytesWritten = updateIdfAndWritePostingList(tempFile, postingList)
                self.__dictionary.insert(term, seekPosition, bytesWritten)
                visited.add(term)

            added = len(set(self.__dIndex.lines()) - visited)
            merged = len(set(self.__dIndex.lines())) - added
            print(self.__class__.__name__ + ":", "merged", merged, "posting lists")

            # merge step 2: for all remaining terms save postingLists in main
            for term in sorted(self.__dIndex):
                if term not in visited:
                    postingList = self.__dIndex[term]
                    seekPosition, bytesWritten = updateIdfAndWritePostingList(tempFile, postingList)
                    self.__dictionary.insert(term, seekPosition, bytesWritten)

        # cleaning up
        os.close(fh)
        mIndex.close()
        remove(self.__mIndexFilepath)
        move(tempFilePath, self.__mIndexFilepath)
        self.__dIndex.clear()

        print(self.__class__.__name__ + ":", "added", added, "new posting lists")
        print(self.__class__.__name__ + ":", "new postinglist index file has size:", os.path.getsize(self.__mIndexFilepath) / InvertedIndexWriter.MB, "mb")


    def incDocumentCounter(self):
        self.__nDocuments += 1
