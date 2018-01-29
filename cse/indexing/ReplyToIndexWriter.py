import os
import msgpack

from os import remove
from tempfile import mkstemp
from shutil import move

from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainIndex import MainIndex
from cse.indexing.DeltaIndex import DeltaIndex


class ReplyToIndexWriter(object):

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
        self.__dIndex = DeltaIndex(list, entrySize=ReplyToIndexWriter.ENTRY_SIZE)
        self.__mIndexFilepath = mainFilepath
        self.__calls = 0


    def __shouldDeltaMerge(self):
        print("delta size check [Bytes]:", self.__dIndex.estimatedSize())
        # check memory usage
        if self.__dIndex.estimatedSize() > ReplyToIndexWriter.MEMORY_THRESHOLD:
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()


    def insert(self, parentCid, childCid):
        self.__dIndex.insert(
            parentCid,
            childCid
        )

        if self.__calls % int(ReplyToIndexWriter.MEMORY_THRESHOLD / 250) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1


    def deltaMerge(self):
        # quit method early if no values are in delta
        if not self.__dIndex:
            print(self.__class__.__name__ + ":", "no delta merge needed")
            return

        # init values
        mIndex = MainIndex(self.__mIndexFilepath, msgpack.unpackb)
        fh, tempFilePath = self.__mIndexFilepath + ".tmp"
        visited = set()
        merged, added = 0, 0

        # helper func
        def writeCids(tempFile, cids):
            seekPosition = tempFile.tell()
            bytesWritten = tempFile.write(msgpack.packb(cids))
            return seekPosition, bytesWritten

        # beginning of merge
        print("!! delta merge !!")
        print(self.__class__.__name__ + ":", "delta estimated size:", self.__dIndex.estimatedSize() / ReplyToIndexWriter.MB, "mb")

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
        self.__dIndex.clear()
        remove(self.__mIndexFilepath)
        move(tempFilePath, self.__mIndexFilepath)
        self.__dictionary.save()

        print(self.__class__.__name__ + ":", "added", added, "new entries")
        print(self.__class__.__name__ + ":", "new ReplyTo index file has size:", os.path.getsize(self.__mIndexFilepath) / ReplyToIndexWriter.MB, "mb")



if __name__ == "__main__":
    # data
    docs = [(1,1), (2,1), (3,2), (4,1), (5,4), (6,4), (7,6), (8,2)]
    docs2 = [(9,1), (10,4), (11,2), (12,1), (13,6), (14,5)]
    n_parents = {
        1: 5,
        2: 3,
        4: 3,
        5: 1,
        6: 2
    }

    # cleanup
    if os.path.exists(os.path.join("data", "test", "replyToDict.index")):
        os.remove(os.path.join("data", "test", "replyToDict.index"))
    if os.path.exists(os.path.join("data", "test", "replyToLists.index")):
        os.remove(os.path.join("data", "test", "replyToLists.index"))

    # indexing
    print("\n\n#### creating index ####\n")
    index = ReplyToIndexWriter(os.path.join("data", "test", "replyToDict.index"), os.path.join("data", "test", "replyToLists.index"))
    for cid, parentCid in docs:
        index.insert(parentCid, cid)
    # delta merge
    index.deltaMerge()

    for cid, parentCid in docs2:
        index.insert(parentCid, cid)
    index.close()


    # check index structure
    print("\n\n#### checking index ####\n")
    from cse.indexing import IndexReader
    index = IndexReader(os.path.join("data", "test"))

    assert len(index.parentCids()) > 0
    for i in index.parentCids():
        print("cid " + str(i) + ":\n", index.repliedTo(i), "\n")
        assert len(index.repliedTo(i)) == n_parents.get(i, 0)
