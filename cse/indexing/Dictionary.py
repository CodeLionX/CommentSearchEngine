import os
import errno
from bisect import bisect_left

from cse.util import PackerUtil
from cse.indexing.commons import SKIP_SIZE

class Dictionary(object):
    """
    Dictionary (in memory)
    Structure: Term -> (Seek pointer, PostingList Size in Bytes)
    """


    def __init__(self, dictionary_index_path, dictionary_dict_path):
        self.__dictionary_index_path = dictionary_index_path
        self.__dictionary_dict_path = dictionary_dict_path
        self.__dictionary = None
        self.__dictionary_dict = None
        self.__open()


    def __open(self):
        if not os.path.exists(self.__dictionary_index_path):
            print(self.__class__.__name__ + ":", "dictionary file",
                  self.__dictionary_index_path,
                  "not available... Please start indexer.")
            raise FileNotFoundError
        else:
            self.__dictionary = open(self.__dictionary_index_path, 'r')

        if os.path.exists(self.__dictionary_dict_path):
            self.__dictionary_dict = PackerUtil.unpackFromFile(self.__dictionary_dict_path, type=PackerUtil.PICKLE)
        else:
            print(self.__class__.__name__ + ":", "No Dictionary Dictionary available...Please start indexer.")
            raise FileNotFoundError


    def close(self):
        self.save()


    def save(self):
        self.__dictionary.close()

    def retrieve(self, term):
        pos = self.__get_dict_pos(term, self.__dictionary_dict[0])
        snippet = self.__get_index_snippet(pos)
        pos = self.__get_dict_pos(term, snippet[0])
        if not snippet[0][pos] == str(term):
            raise FileNotFoundError("Dictionary doesn't contain term: {}".format(term))
        return snippet[1][pos], snippet[1][pos+1] - snippet[1][pos]

    def __get_dict_pos(self, term, list):
        pos = bisect_left(list, str(term))
        if len(list) == pos:
            return pos - 1
        if list[pos] == str(term):
            return pos
        return pos - 1

    def __get_index_snippet(self, start_pos):
        snippet = ([], [])
        start_offset = self.__dictionary_dict[1][start_pos]
        #print(start_offset)
        try:
            length = self.__dictionary_dict[1][start_pos + 1] - self.__dictionary_dict[1][start_pos]
            #print(self.__dictionary_dict[0][start_pos + 1])
        except IndexError:
            length = -1
        self.__dictionary.seek(start_offset)
        text = self.__dictionary.read(length)
        text = text.strip().split('\n')
        for line in text:
            try:
                term, pointer = line.split('|||')
            except ValueError:
                break
            snippet[0].append(str(term))
            snippet[1].append(int(pointer))
        return snippet

    def insert(self, term, pointer, size):
        raise DeprecationWarning


    def __len__(self):
        return len(self.__dictionary_dict[0]) * SKIP_SIZE


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value

    def __contains__(self, item):
        try:
            self.retrieve(item)
        except FileNotFoundError:
            return False
        return True

    def __str__(self):
        return str(self.__dictionary)



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
