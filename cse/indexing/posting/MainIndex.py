import os
import errno

from cse.WeightCalculation import calcIdf
from cse.indexing.posting.PostingList import PostingList


"""
Inverted Index (main - on disk)
Structure: Offset, Size -> Posting List
Posting List Entry: (cid, tf, positionsList)
Positions List: [pos1, pos2, ...]
--> PostingsList: [(cid, tf, [pos1, pos2, ...]), ...]
"""
class MainIndex(object):

    __postingLists = None
    __postingListsFilename = ""


    def __init__(self, filename):
        self.__postingListsFilename = filename
        self.__open()


    def __open(self):
        if not os.path.exists(os.path.dirname(self.__postingListsFilename)):
            try:
                os.makedirs(os.path.dirname(self.__postingListsFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__postingListsFilename):
            print(self.__class__.__name__ + ":", "postinglist file not available...creating file")
            os.mknod(self.__postingListsFilename)
        #self.__postingLists = open(self.__postingListsFilename, 'r', newline='', encoding="utf-8")
        self.__postingLists = open(self.__postingListsFilename, 'rb')


    def close(self):
        self.__postingLists.close()


    def retrieve(self, pointer, size):
        self.__postingLists.seek(pointer)
        readBytes = self.__postingLists.read(size)
        return PostingList.decode(readBytes)


    def sizeOnDisk(self):
        return os.path.getsize(self.__postingListsFilename)


    def __getitem__(self, key):
        value = self.retrieve(key[0], key[1])
        if value is None:
            raise KeyError
        return value
