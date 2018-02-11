import os
import errno
from cse.util import PackerUtil
from cse.indexing.commons import PARTIAL_THRESHOLD


class DocumentMapBuilder:

    def __init__(self, document_map_index, document_map_dict):
        if not os.path.exists(os.path.dirname(document_map_index)):
            try:
                os.makedirs(os.path.dirname(document_map_index))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        self.__document_map_index = document_map_index
        self.__document_map_dict = document_map_dict
        self.__index = {}
        if os.path.exists(self.__document_map_index):
            os.remove(self.__document_map_index)
        if os.path.exists(self.__document_map_dict):
            os.remove(self.__document_map_dict)
        dir = os.path.dirname(self.__document_map_index)
        if os.path.exists(os.path.join(dir, 'document_map_partials')):
            os.removedirs(os.path.join(dir, 'document_map_partials'))

    def close(self):
        self._build_partial_files()
        #PackerUtil.packToFile(self.__index, self.__document_map_index, type=PackerUtil.JSON)

    def _build_partial_files(self):
        i = 0
        content = 0
        partial_list = []
        for cid in self.__index:
            partial_list.append((cid, self.__index[cid]))
            content += 1
            if content >= PARTIAL_THRESHOLD:
                partial_list.sort()
                self.__save_partial_index(partial_list, i)
                partial_list = []
                content = 0
                i += 1
        partial_list.sort()
        self.__save_partial_index(partial_list, i)

    def insert(self, cid, pointer):
        self.__index[cid] = pointer

    def get(self, cid):
        return self.__index[cid]

    def listCids(self):
        return [cid for cid in self.__index]

    def __enter__(self):
        return self.open()

    def __exit__(self, type, value, traceback):
        self.close()

    def __save_partial_index(self, partial_list, i):
        dir = os.path.dirname(self.__document_map_index)
        file_name = os.path.basename(self.__document_map_index)
        if not os.path.exists(os.path.join(dir, 'document_map_partials')):
            os.makedirs(os.path.join(dir, 'document_map_partials'))

        with open(os.path.join(dir, 'document_map_partials', file_name + str(i)), 'w') as partial:
            for tuple in partial_list:
                partial.write(str(tuple[0]) + ',' + str(tuple[1]) + '\n')
