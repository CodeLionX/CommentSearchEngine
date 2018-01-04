import os
import errno

from cse.util import PackerUtil



class DocumentMap(object):


    def __init__(self, filepathname):
        if not os.path.exists(os.path.dirname(filepathname)):
            try:
                os.makedirs(os.path.dirname(filepathname))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.__filePathname = filepathname
        self.__index = {}


    def open(self):
        if os.path.exists(self.__filePathname):
            self.__index = PackerUtil.unpackFromFile(self.__filePathname)
        else:
            print(self.__class__.__name__ + ":", "No DocumentMap available...creating new one")
            self.__index = {}
        return self


    def close(self):
        PackerUtil.packToFile(self.__index, self.__filePathname)


    def insert(self, cid, pointer, size):
        self.__index[cid] = (pointer, size)


    def get(self, cid):
        return self.__index[cid]


    def getPointer(self, cid):
        return self.__index[cid][0]


    def getSize(self, cid):
        return self.__index[cid][1]


    def listCids(self):
        return [cid for cid in self.__index]


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()
