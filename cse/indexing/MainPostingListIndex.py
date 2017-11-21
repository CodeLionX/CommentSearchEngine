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
        # postingList line: <cid1>|<pos1>,<pos2>,<pos3>;<cid2>|<pos1>,<pos2>\n
        # result:           [(cid1, [pos1, pos2, pos3]), (cid2, [pos1, pos2])]
        # result type:      list[tuple[string, list[int]]]
        return list(map(
            lambda s: (s.split("|")[0], list(s.split("|")[1].split(","))),
            list(line.replace("\n", "").split(";"))
        ))


    def __encodePlLine(self, postingList):
        # postingList:      [(cid1, [pos1, pos2, pos3]), (cid2, [pos1, pos2])]
        # postingList type: list[tuple[string, list[int]]]
        # result:           <cid1>|<pos1>,<pos2>,<pos3>;<cid2>|<pos1>,<pos2>\n
        return ";".join([
            termTuple[0]
                + "|"
                + ",".join(
                    str(position) for position in termTuple[1]
                )
            for termTuple in postingList
        ]) + "\n"


    def close(self):
        self.save()


    def save(self):
        self.__postingLists.close()


    def retrieve(self, pointer):
        self.__postingLists.seek(0)
        for i, plLine in enumerate(self.__postingLists):
            if i == pointer:
                return self.__decodePlLine(plLine)
        return None


    def estimatedSize(self):
        return self.__sizeof__()


    def mergeInDeltaIndex(self, dIndex):
        self.__postingLists.seek(0)
        fd, tempFilePath = mkstemp(text=True)
        visited = set()

        with open(tempFilePath, 'w', newline='', encoding="utf-8") as tempFile:
            for i, plLine in enumerate(self.__postingLists):
                if i in dIndex:
                    postingList = self.__decodePlLine(plLine)
                    postingList = postingList + dIndex[i]
                    postingList.sort(key=lambda x: x[0]) # sort based on cid
                    tempFile.write(self.__encodePlLine(postingList))
                else:
                    tempFile.write(plLine)
                visited.add(i)
            for pointer in sorted(dIndex):
                if pointer not in visited:
                    tempFile.write(self.__encodePlLine(dIndex[pointer]))

        tempFile.close()
        os.close(fd)

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
