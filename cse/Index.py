import os
from os import remove
from tempfile import mkstemp
from shutil import move
from cse.util import Util


class DeltaPostingListIndex(object):

    """
    Inverted Index (delta - in memory)
    Structure: Line Number in File -> Posting List
    """
    __pl = None
    __margin = 300
    __cidSize = 0
    __numCids = 0


    def __init__(self, cidSize=35): # import sys; cid = "14d2c537-d2ed-4e36-bf3d-a26f62c02370"; assert(sys.getsizeof(cid) == 85)
        self.__pl = {}
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


    def clear(self):
        self.__pl = {}
        self.__numCids = 0


    def estimatedSize(self):
        return self.__sizeof__()


    def lines(self):
        return self.__pl.keys()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        self.insert(key, value)


    def __iter__(self):
        return self.__pl.__iter__()


    def __contains__(self, item):
        return self.__pl.__contains__(item)


    def __sizeof__(self):
        from sys import getsizeof
        return int(getsizeof(self.__pl)
                + self.__cidSize * self.__numCids
                + self.__margin)



class MainPostingListIndex(object):

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
            print("postinglist file not available...creating file")
            os.mknod(self.__postingListsFilename)
        self.__postingLists = open(self.__postingListsFilename, 'r', newline='', encoding="utf-8")


    def __decodePlLine(self, line):
        return list(line.replace("\n", "").split(","))


    def __encodePlLine(self, pl):
        return ",".join(pl) + "\n"


    def close(self): self.save()
    def save(self):
        self.__postingLists.close()


    def retrieve(self, line):
        self.__postingLists.seek(0)
        for i, pl in enumerate(self.__postingLists):
            if i == line:
                return self.__decodePlLine(pl)
        return None


    def estimatedSize(self):
        return self.__sizeof__()


    def mergeInDeltaIndex(self, dIndex):
        self.__postingLists.seek(0)
        sh, tempFilePath = mkstemp()
        visited = set()
        with open(tempFilePath, 'w', newline='', encoding="utf-8") as tempFile:
            for i, line in enumerate(self.__postingLists):
                if i in dIndex:
                    pl = self.__decodePlLine(line)
                    pl = pl + dIndex[i]
                    pl.sort()
                    tempFile.write(self.__encodePlLine(pl))
                else:
                    tempFile.write(line)
                visited.add(i)
            for pointer in dIndex:
                if pointer not in visited:
                    tempFile.write(self.__encodePlLine(dIndex[pointer]))
        
        added = len(set(dIndex.lines()) - visited)
        merged = len(set(dIndex.lines())) - added
        print("MainPL: merged", merged, "posting lists")
        print("MainPL: added", added, "new posting lists")

        self.__postingLists.close()
        del self.__postingLists
        remove(self.__postingListsFilename)
        move(tempFilePath, self.__postingListsFilename)
        self.__postingLists = open(self.__postingListsFilename, 'r', newline='', encoding="utf-8")
        print("MainPL: new postinglist index file has size:", os.path.getsize(self.__postingListsFilename) / 1024 / 1024, "mb")


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __iter__(self):
        return enumerate(self.__postingLists)



class InvertedIndex(object):


    __dictionary = None
    __dIndex = None
    __mIndex = None
    __calls = 0


    def __init__(self, filepath):
        self.__dictionary = Dictionary(os.path.join(filepath, "dictionary.index"))
        self.__dIndex = DeltaPostingListIndex()
        self.__mIndex = MainPostingListIndex(os.path.join(filepath, "postingLists.index"))
        self.__calls = 0


    def __shouldDeltaMerge(self):
        # check memory usage
        if self.__dIndex.estimatedSize() > (50 * 1024*1024):
            self.deltaMerge()
            self.__calls = -1


    def close(self):
        self.deltaMerge()
        self.__dictionary.close()
        self.__mIndex.close()


    def insert(self, term, documentId):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
        else:
            pointer = self.__dictionary.nextFreeLinePointer()
            self.__dictionary[term] = pointer

        self.__dIndex.insert(pointer, documentId)

        if self.__calls % (1000 * 50) == 0:
            self.__shouldDeltaMerge()

        self.__calls = self.__calls + 1   


    def get(self, term):
        if term not in self.__dictionary:
            raise KeyError
        pointer = self.__dictionary[term]

        #TODO


    def terms(self):
        return [term for term in self.__dictionary]


    def deltaMerge(self):
        print("!! delta merge !!")
        print("  delta estimated size:", self.__dIndex.estimatedSize() / 1024 / 1024, "mb")
        self.__mIndex.mergeInDeltaIndex(self.__dIndex)
        self.__dIndex.clear()



"""
def __addToPl(self, line, cid):
    
    self.__postingList.seek(0)
    for i, pl in enumerate(self.__postingList):
        if i == line:
            # unsorted!!
            self.__postingList.write(",".join([pl, cid])) # i guess this will overwrite existing postinglist in the following line
    
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
"""



"""
Dictionary (in memory)
Structure: Term -> Postinglist Line Number (referred to as pointer)
"""
class Dictionary(object):


    __filename = ""
    __dictionary = None
    __nextPointerCache = 0


    def __init__(self, filename):
        self.__filename = filename
        self.__open()
        self.__nextPointerCache = max(self.__dictionary.values(), default = -1) + 1


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
            self.__dictionary = {}
        else:
            with open(self.__filename, 'r', newline='', encoding="utf-8") as file:
                self.__dictionary = Util.fromJsonString(file.read())


    def close(self): self.save()
    def save(self):
        with open(self.__filename, 'w', newline='', encoding="utf-8") as file:
            file.write(Util.toJsonString(self.__dictionary))


    def retrieve(self, term):
        if str(term) not in self.__dictionary:
            return None
        return int(self.__dictionary[term])


    def insert(self, term, pointer):
        self.__dictionary[str(term)] = int(pointer)


    def nextFreeLinePointer(self):
        nextPointer = self.__nextPointerCache
        self.__nextPointerCache = self.__nextPointerCache + 1
        return nextPointer


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        self.insert(key, value)


    def iterkeys(self): self.__iter__()
    def __iter__(self):
        return self.__dictionary.__iter__()


    def __contains__(self, item):
        return self.__dictionary.__contains__(str(item))


if __name__ == '__main__':
    d = Dictionary(os.path.join("data", "dictionary.index"))

    if "hello" in d:
        pointer = d["hello"]
    else:
        pointer = 2
        d["hello"] = pointer
    print(d["hello"])

    if "hello" in d:
        pointer = d["hello"]
    else:
        pointer = 3
        d["hello"] = pointer
    print(d["hello"])

    i = DeltaPostingListIndex()
    i.insert(2, "cid1")
    cid = i.retrieve(2)
    print(cid)
    i[5] = "cid2"
    i[5] = "cid3"
    print(i[5])
    print(list(i))
    print(5 in i)
    print(6 in i)