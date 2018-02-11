import os
import errno
from cse.util import PackerUtil
from bisect import bisect_left

class DocumentMap(object):

    def __init__(self, document_map_index, document_map_dict):
        if not os.path.exists(os.path.dirname(document_map_index)):
            try:
                os.makedirs(os.path.dirname(document_map_index))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.document_map_index_path = document_map_index
        self.document_map_dict_path = document_map_dict
        self.__index = None
        self.__dict = None

    def open(self):
        if os.path.exists(self.document_map_index_path):
            self.__index = open(self.document_map_index_path, 'r')
        else:
            print(self.__class__.__name__ + ":", "No DocumentMap available...Please start indexer.")
            raise FileNotFoundError

        if os.path.exists(self.document_map_dict_path):
            self.__dict = PackerUtil.unpackFromFile(self.document_map_dict_path, type=PackerUtil.PICKLE)
        else:
            print(self.__class__.__name__ + ":", "No DocumentMap Dictionary available...Please start indexer.")
            raise FileNotFoundError

        return self

    def close(self):
        self.__index.close()

    def insert(self, cid, pointer):
        raise DeprecationWarning

    def get(self, cid):
        pos = self.__get_dict_pos(cid, self.__dict[0])
        snippet = self.__get_index_snippet(pos)
        pos = self.__get_dict_pos(cid, snippet[0])
        if not snippet[0][pos] == int(cid):
            raise FileNotFoundError("DocumentMap doesn't contain cid: {}".format(cid))
        return snippet[1][pos]

    def __get_dict_pos(self, cid, list):
        pos = bisect_left(list, int(cid))
        if list[pos] == int(cid):
            return pos
        return pos - 1

    def __get_index_snippet(self, start_pos):
        snippet = ([], [])
        start_offset = self.__dict[1][start_pos]
        length = self.__dict[1][start_pos + 1] - self.__dict[1][start_pos]
        self.__index.seek(start_offset)
        text = self.__index.read(length)
        text = text.strip().split('\n')
        for line in text:
            cid, pointer = line.split(',')
            snippet[0].append(int(cid))
            snippet[1].append(int(pointer))
        return snippet

    def listCids(self):
        cids = []
        self.__index.seek(0)
        for line in self.__index:
            cids.append(int(line.split(',')[0]))
        return cids

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, traceback):
        self.close()
