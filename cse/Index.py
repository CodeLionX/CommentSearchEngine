import os
from pandas.io import pickle
from cse.util import Util


class PostingListIndex(object):


    __pl = None
    __margin = 300
    __cidSize = 0
    __numCids = 0


    def __init__(self, cidSize=85): # import sys; cid = "14d2c537-d2ed-4e36-bf3d-a26f62c02370"; assert(sys.getsizeof(cid) == 85)
        self.__pl = dict()
        self.__cidSize = cidSize
        self.__numCids = 0


    def retrieve(self, line):
        if line not in self.__pl:
            return None
        return self.__pl[line]


    def insert(self, line, cid):
        if line not in self.__pl:
            self.__pl[line] = []
        self.__pl[line].append(cid)
        self.__pl[line].sort()
        self.__numCids = self.__numCids + 1


    def __getitem__(self, key):
        value = self.retrieve(key)
        if not value:
            raise KeyError


    def __setitem__(self, key, value):
        self.insert(key, value)


    def __iter__(self):
        return self.__pl.__iter__()


    def __contains__(self, item):
        return self.__pl.__contains__(item)


    def __sizeof__(self):
        from sys import getsizeof
        return (getsizeof(self.__pl)
                + self.__cidSize * self.__numCids
                + self.__margin)



class InvertedIndex(object):

    __dictionary = None
    """
    Inverted Index (on disk)
    Structure: Line Number in File -> Posting List
    """
    __postingList = None
    __postingListFilename = ""


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__postingListFilename = os.path.join(filepath, "pl.index")


    def open(self):
        if not os.path.exists(os.path.dirname(self.__postingListFilename)):
            try:
                os.makedirs(os.path.dirname(self.__postingListFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__postingListFilename):
            print("postinglist file not available...creating file")
            os.mknod(self.__postingListFilename)
        self.__postingList = open(self.__postingListFilename, 'r+', newline='', encoding="utf-8")


    def close(self):
        self.__dictionary.save()
        self.__postingList.close()


    def insert(self, term, documentId):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
            self.__addToPl(pointer, documentId)
        else:
            pointer = self.__insertPl([documentId])
            self.__dictionary[term] = pointer


    def get(self, term):
        try:
            return self.__lookupPl(self.__dictionary[term])
        except KeyError:
            return None


    def terms(self):
        return [term for term in self.__dictionary]


    def __lookupPl(self, line):
        self.__postingList.seek(0)
        for i, pl in enumerate(self.__postingList):
            if i == line:
                return list(pl.split(","))


    def __addToPl(self, line, cid):
        """
        self.__postingList.seek(0)
        for i, pl in enumerate(self.__postingList):
            if i == line:
                # unsorted!!
                self.__postingList.write(",".join([pl, cid])) # i guess this will overwrite existing postinglist in the following line
        """
        
        from tempfile import mkstemp
        from shutil import move
        from os import remove

        self.__postingList.close()
        sh, targetPath = mkstemp()
        with open(targetPath, 'w') as target_file:
            with open(self.__postingListFilename, 'r') as source_file:
                for i, pl in enumerate(source_file):
                    if i == line:
                        target_file.write(",".join([pl, cid]) + "\n")
                    else:
                        target_file.write(pl)
        remove(self.__postingListFilename)
        move(targetPath, self.__postingListFilename)
        self.__postingList = open(self.__postingListFilename, 'r+', newline='', encoding="utf-8")


    def __insertPl(self, cidList):
        self.__postingList.seek(0)
        line = 0
        for i, pl in enumerate(self.__postingList):
            line = i
        self.__postingList.write(",".join(cidList) + "\n")
        return line + 1



"""
Dictionary (in memory)
Structure: Term -> Postinglist Line Number (referred to as pointer)
"""
class Dictionary(object):


    __filename = ""
    __dictionary = None


    def __init__(self, filename):
        self.__filename = filename
        self.__open()


    def __open(self):
        if not os.path.exists(os.path.dirname(self.__filename)):
            try:
                os.makedirs(os.path.dirname(self.__filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__filename):
            print("dictionary file not available...creating new dictionary in-memory, " +
                  "call save() to save to disk!")
            self.__dictionary = dict()
        else:
            with open(self.__filename, 'r', newline='', encoding="utf-8") as file:
                self.__dictionary = Util.fromJsonString(file.read())


    def close(self): self.save()
    def save(self):
        with open(self.__filename, 'w', newline='', encoding="utf-8") as file:
            file.write(Util.toJsonString(self.__dictionary))


    def retrieve(self, term):
        if term not in self.__dictionary:
            return None
        return self.__dictionary[term]


    def insert(self, term, pointer):
        self.__dictionary[term] = pointer


    def __getitem__(self, key):
        value = self.retrieve(key)
        if not value:
            raise KeyError


    def __setitem__(self, key, value):
        self.insert(key, value)


    def __iter__(self):
        return self.__dictionary.__iter__()


    def __contains__(self, item):
        return self.__dictionary.__contains__(item)
