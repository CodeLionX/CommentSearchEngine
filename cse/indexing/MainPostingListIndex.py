import os
from os import remove
from tempfile import mkstemp
from shutil import move


"""
Inverted Index (main - on disk)
Structure: Line Number in File -> Posting List
"""
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


    def close(self):
        self.save()


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
