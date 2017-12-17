import os
import msgpack
import errno


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
            with open(self.__filename, 'rb') as file:
                self.__dictionary = msgpack.unpack(file, encoding="UTF-8")


    def close(self):
        self.save()


    def save(self):
        with open(self.__filename, 'wb') as file:
            msgpack.pack(self.__dictionary, file, use_bin_type=True)


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
        self.insert(key, value)


    def iterkeys(self): self.__iter__()
    def __iter__(self):
        return self.__dictionary.__iter__()


    def __contains__(self, item):
        return self.__dictionary.__contains__(str(item))



if __name__ == "__main__":
    print("creating dictionary")
    d = Dictionary(os.path.join("data", "test.dict"))
    d.insert("a", 0)
    d.insert("c", 1)
    d.insert("b", 2)
    d.close()
    print("saved to disk")

    # reopen dict
    print("re-open dictionary file")
    d2 = Dictionary(os.path.join("data", "test.dict"))
    a = d2.retrieve("a")
    print("a=", a)
    assert(a == 0)
    b = d2.retrieve("b")
    print("b=", b)
    assert(b == 2)
    c = d2.retrieve("c")
    print("c=", c)
    assert(c == 1)
    d2.close()
