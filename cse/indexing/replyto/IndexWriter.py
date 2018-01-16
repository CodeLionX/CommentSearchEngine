import os
import msgpack

from os import remove
from tempfile import mkstemp
from shutil import move

from cse.indexing.Dictionary import Dictionary
from cse.indexing.replyto.MainIndex import MainIndex
from cse.indexing.replyto.DeltaIndex import DeltaIndex


class IndexWriter(object):

    MB = 1024*1024
    # threshold for delta index to reside in memory
    # if the memory consumption of the delta index itself gets higher than this threshold
    # a delta merge is performend and the index will be written to disk
    MEMORY_THRESHOLD = 500 * MB     # 500 MB
    # entry size estimation for simple heursitic to determine memory consumption of the
    # delta index
    ENTRY_SIZE       = 10           #  10 B


    def __init__(self, dictFilepath, mainFilepath):
        self.__dictionary = Dictionary(dictFilepath)
        self.__dIndex = DeltaIndex(entrySize=IndexWriter.ENTRY_SIZE)
        self.__mIndexFilepath = mainFilepath
        self.__calls = 0


    def __shouldDeltaMerge(self):
        print("delta size check [Bytes]:", self.__dIndex.estimatedSize())
        # check memory usage
        if self.__dIndex.estimatedSize() > IndexWriter.MEMORY_THRESHOLD:
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()


    def insert(self, parentCid, childCids):
        self.__dIndex.insert(
            parentCid,
            childCids
        )

        if self.__calls % int(IndexWriter.MEMORY_THRESHOLD / 250) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1


    def deltaMerge(self):
        # quit method early if no values are in delta
        if not self.__dIndex:
            print(self.__class__.__name__ + ":", "no delta merge needed")
            return

        # init values
        mIndex = MainIndex(self.__mIndexFilepath)
        fh, tempFilePath = mkstemp(text=False)
        visited = set()
        merged, added = 0, 0

        # helper func
        def writeCids(tempFile, cids):
            seekPosition = tempFile.tell()
            bytesWritten = tempFile.write(msgpack.packb(cids))
            return seekPosition, bytesWritten

        # beginning of merge
        print("!! delta merge !!")
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / IndexWriter.MB, "mb")

        with open(tempFilePath, 'wb') as tempFile:
            # merge step 1: for each parent cid in main update cid list (add delta)
            for parentCid in sorted(self.__dictionary):
                pointer, size = self.__dictionary[parentCid]
                cidList = mIndex.retrieve(pointer, size)

                if parentCid in self.__dIndex:
                    cidList = cidList + self.__dIndex[parentCid]

                seekPosition, bytesWritten = writeCids(tempFile, cidList)
                self.__dictionary.insert(parentCid, seekPosition, bytesWritten)
                visited.add(parentCid)

            added = len(set(self.__dIndex.lines()) - visited)
            merged = len(set(self.__dIndex.lines())) - added
            print(self.__class__.__name__ + ":", "merged", merged, "cid lists")

            # merge step 2: for all remaining parent cids save cid lists in main
            for parentCid in sorted(self.__dIndex):
                if parentCid not in visited:
                    cidList = self.__dIndex[parentCid]
                    seekPosition, bytesWritten = writeCids(tempFile, cidList)
                    self.__dictionary.insert(parentCid, seekPosition, bytesWritten)


        # cleaning up and store current snapshot
        mIndex.close()
        os.close(fh)
        self.__dIndex.clear()
        remove(self.__mIndexFilepath)
        move(tempFilePath, self.__mIndexFilepath)
        self.__dictionary.save()

        print(self.__class__.__name__ + ":", "added", added, "new posting lists")
        print(self.__class__.__name__ + ":", "new postinglist index file has size:", os.path.getsize(self.__mIndexFilepath) / IndexWriter.MB, "mb")



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
    index = IndexWriter(os.path.join("data", "test"))
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
    from cse.indexing import InvertedIndexReader
    index = InvertedIndexReader(os.path.join("data", "test"))

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
