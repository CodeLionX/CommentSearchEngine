import os
import errno

from cse.util import PackerUtil

class Dictionary(object):
    """
    Dictionary (in memory)
    Structure: Term -> (Seek pointer, PostingList Size in Bytes)
    """

    __filename = ""
    __dictionary = None
    __nextPointerCache = 0


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
            print(self.__class__.__name__ + ":", "dictionary file not available...creating new dictionary in-memory, " +
                  "call save() to save to disk!")
            self.__dictionary = {}
        else:
            self.__dictionary = PackerUtil.unpackFromFile(self.__filename)


    def close(self):
        self.save()


    def save(self):
        PackerUtil.packToFile(self.__dictionary, self.__filename)


    def retrieve(self, term):
        if str(term) not in self.__dictionary:
            return None
        return self.__dictionary[str(term)]


    def insert(self, term, pointer, size):
        self.__dictionary[str(term)] = (int(pointer), int(size))


    def __len__(self):
        return self.__dictionary.__len__()


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        self.insert(key, value[0], value[1])


    def iterkeys(self): self.__iter__()
    def __iter__(self):
        return self.__dictionary.__iter__()


    def __contains__(self, item):
        return self.__dictionary.__contains__(str(item))



if __name__ == "__main__":
    print("creating dictionary")
    d = Dictionary(os.path.join("data", "test.dict"))
    d.insert("a", 0, 1)
    d.insert("c", 1, 1)
    d.insert("b", 2, 4)
    d.close()
    print("saved to disk")

    # reopen dict
    print("re-open dictionary file")
    d2 = Dictionary(os.path.join("data", "test.dict"))
    a, _ = d2.retrieve("a")
    print("a=", a)
    assert  a == 0
    b, bS = d2.retrieve("b")
    print("b=", b, "size b=", bS)
    assert  b == 2
    assert bS == 4
    c, _ = d2.retrieve("c")
    print("c=", c)
    assert  c == 1
    d2.close()

    # cleanup
    os.remove(os.path.join("data", "test.dict"))
