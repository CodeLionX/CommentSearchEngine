import os

from cse.util import Util



class Dictionary(object):
    """
    Dictionary (in memory)
    Structure: Term -> Postinglist Line Number (referred to as pointer)
    """

    __filename = ""
    __dictionary = None
    __nextPointerCache = 0


    def __init__(self, filename):
        self.__filename = filename
        self.__open()
        self.__nextPointerCache = max(self.__dictionary.values(), default=-1) + 1


    def __open(self):
        if not os.path.exists(os.path.dirname(self.__filename)):
            try:
                os.makedirs(os.path.dirname(self.__filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__filename):
            print(self.__class__.__name__ + ":", "dictionary file not available...creating new dictionary in-memory, " +
                  "call save() to save to disk!")
            self.__dictionary = {}
        else:
            with open(self.__filename, 'r', newline='', encoding="utf-8") as file:
                self.__dictionary = Util.fromJsonString(file.read())


    def close(self):
        self.save()


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


    def __len__(self):
        return self.__dictionary.__len__()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        """
        value: pointer
        """
        self.insert(key, value)


    def iterkeys(self): self.__iter__()
    def __iter__(self):
        return self.__dictionary.__iter__()


    def __contains__(self, item):
        return self.__dictionary.__contains__(str(item))
