import os

from cse.util import Util



class DocumentMap(object):


    __filePathname = ""
    __index = {}


    def __init__(self, filepathname):
        if not os.path.exists(os.path.dirname(filepathname)):
            try:
                os.makedirs(os.path.dirname(filepathname))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        
        self.__filePathname = filepathname

    
    def open(self):
        # a+ = read and append (file is created if it does not exist)
        with open(self.__filePathname, 'a+', newline='') as file:
            file.seek(0)
            fileContent = file.read()
            if fileContent:
                self.__index = Util.fromJsonString(fileContent)
            else:
                print(self.__class__.__name__ + ":", "No DocumentMap available...creating new one")
                self.__index = {}
        return self


    def close(self):
        with open(self.__filePathname, 'w', newline='') as file:
            file.seek(0)
            file.write(Util.toJsonString(self.__index))


    def insert(self, cid, pointer, numberOfTokens):
        self.__index[cid] = (pointer, numberOfTokens)


    def get(self, cid):
        return self.__index[cid]

    
    def getPointer(self, cid):
        return self.__index[cid][0]


    def listCids(self):
        return [cid for cid in self.__index]


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()
