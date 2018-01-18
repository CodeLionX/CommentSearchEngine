import os

from os import remove
from tempfile import mkstemp
from shutil import move

from cse.WeightCalculation import calcTf
from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainIndex import MainIndex
from cse.indexing.DeltaIndex import DeltaIndex
from cse.indexing.posting.PostingList import PostingList


class IndexWriter(object):

    MB = 1024*1024
    # threshold for delta index to reside in memory
    # if the memory consumption of the delta index itself gets higher than this threshold
    # a delta merge is performend and the index will be written to disk
    MEMORY_THRESHOLD = 500 * MB     # 500 MB
    # entry size estimation for simple heursitic to determine memory consumption of the
    # delta index
    POSTING_LIST_ENTRY_SIZE = 30    #  30 B


    def __init__(self, dictFilepath, mainFilepath):
        self.__dictionary = Dictionary(dictFilepath)
        self.__dIndex = DeltaIndex(PostingList, entrySize=IndexWriter.POSTING_LIST_ENTRY_SIZE)
        self.__mIndexFilepath = mainFilepath
        self.__calls = 0
        self.__nDocuments = 0


    def __shouldDeltaMerge(self):
        print("delta size check [Bytes]:", self.__dIndex.estimatedSize())
        # check memory usage
        if self.__dIndex.estimatedSize() > IndexWriter.MEMORY_THRESHOLD:
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()


    def insert(self, term, commentId, nTerms, positions):
        self.__dIndex.insert(
            term,
            (int(commentId), calcTf(nTerms, len(positions)), positions)
        )

        if self.__calls % int(IndexWriter.MEMORY_THRESHOLD / 250) == 0:
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
        mIndex = MainIndex(self.__mIndexFilepath, PostingList.decode)
        fh, tempFilePath = mkstemp(text=False)
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
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / IndexWriter.MB, "mb")

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


        # cleaning up and store current snapshot
        mIndex.close()
        os.close(fh)
        self.__dIndex.clear()
        remove(self.__mIndexFilepath)
        move(tempFilePath, self.__mIndexFilepath)
        self.__dictionary.save()

        print(self.__class__.__name__ + ":", "added", added, "new posting lists")
        print(self.__class__.__name__ + ":", "new postinglist index file has size:", os.path.getsize(self.__mIndexFilepath) / IndexWriter.MB, "mb")


    def incDocumentCounter(self):
        self.__nDocuments += 1



if __name__ == "__main__":
    # data
    doc1 = [("term1", [1]), ("term5", [2,4]), ("term2", [3]), ("term4", [5])]
    doc2 = [("term3", [1]), ("term2", [2,3,4])]
    doc3 = [("term1", [1]), ("term5", [2,3]), ("term2", [4])]
    doc4 = [("term2", [1,2,3])]

    # cleanup
    if os.path.exists(os.path.join("data", "test", "dictionary.index")):
        os.remove(os.path.join("data", "test", "dictionary.index"))
    if os.path.exists(os.path.join("data", "test", "postingLists.index")):
        os.remove(os.path.join("data", "test", "postingLists.index"))

    # indexing
    print("\n\n#### creating index ####\n")
    index = IndexWriter(os.path.join("data", "test", "dictionary.index"), os.path.join("data", "test", "postingLists.index"))
    for term, posList in doc1:
        index.insert(term, 0, len(doc1), posList)
    index.incDocumentCounter()
    # delta merge
    index.deltaMerge()

    for term, posList in doc2:
        index.insert(term, 1, len(doc2), posList)
    index.incDocumentCounter()
    for term, posList in doc3:
        index.insert(term, 2, len(doc3), posList)
    index.incDocumentCounter()
    index.deltaMerge()

    for term, posList in doc4:
        index.insert(term, 3, len(doc4), posList)
    index.close()


    # check index structure
    print("\n\n#### checking index ####\n")
    from cse.indexing import IndexReader
    index = IndexReader(os.path.join("data", "test"))

    print("term1\n", index.idf("term1"), index.postingList("term1"), "\n")
    assert(len(index.postingList("term1")) == 2)

    print("term2\n", index.idf("term2"), index.postingList("term2"), "\n")
    assert(len(index.postingList("term2")) == 4)

    print("term3\n", index.idf("term3"), index.postingList("term3"), "\n")
    assert(len(index.postingList("term3")) == 1)

    print("term4\n", index.idf("term4"), index.postingList("term4"), "\n")
    assert(len(index.postingList("term4")) == 1)

    print("term5\n", index.idf("term5"), index.postingList("term5"), "\n")
    print(index.retrieve("term5").postingList())
    assert(len(index.postingList("term5")) == 2)
