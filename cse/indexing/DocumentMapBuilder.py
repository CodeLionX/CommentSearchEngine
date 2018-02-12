import os
import errno
import shutil

from cse.util import PackerUtil
from cse.indexing.commons import PARTIAL_THRESHOLD, SKIP_SIZE, DOCUMENT_MAP_TMP_DIR


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
        self.__index = []
        self.__i = 0
        self.__content = 0
        if os.path.exists(self.__document_map_index):
            os.remove(self.__document_map_index)
        if os.path.exists(self.__document_map_dict):
            os.remove(self.__document_map_dict)
        dir = os.path.dirname(self.__document_map_index)
        if os.path.isdir(os.path.join(dir, DOCUMENT_MAP_TMP_DIR)):
            shutil.rmtree(os.path.join(dir, DOCUMENT_MAP_TMP_DIR))

    def close(self):
        self.__index.sort()
        self.__save_partial_index(self.__index, self.__i)
        doc_dict = self._build_index_and_dict()
        PackerUtil.packToFile(doc_dict, self.__document_map_dict, type=PackerUtil.PICKLE)
        self.__clear()

    def __clear(self):
        self.__index = []
        self.__content = 0
        self.__i += 1

    def insert(self, cid, pointer):
        self.__index.append((cid, pointer))
        self.__content += 1
        if self.__content >= PARTIAL_THRESHOLD:
            self.__index.sort()
            self.__save_partial_index(self.__index, self.__i)
            self.__clear()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __save_partial_index(self, partial_list, i):
        dir = os.path.dirname(self.__document_map_index)
        file_name = os.path.basename(self.__document_map_index)
        if not os.path.exists(os.path.join(dir, DOCUMENT_MAP_TMP_DIR)):
            os.makedirs(os.path.join(dir, DOCUMENT_MAP_TMP_DIR))

        with open(os.path.join(dir, DOCUMENT_MAP_TMP_DIR, file_name + str(i)), 'w') as partial:
            for tuple in partial_list:
                partial.write(str(tuple[0]) + ',' + str(tuple[1]) + '\n')

    def _build_index_and_dict(self):
        doc_dict = ([], [])
        dir = os.path.dirname(self.__document_map_index)
        partials_dir = os.path.join(dir, DOCUMENT_MAP_TMP_DIR)
        partial_files = []
        current_lines = []
        skips = SKIP_SIZE
        with open(self.__document_map_index, 'w') as out_index:
            for file in os.listdir(partials_dir):
                partial_files.append(open(os.path.join(partials_dir, file)))

            for file_handle in partial_files:
                current_lines.append(self._read_partial_line(file_handle))

            while partial_files:
                min_index = current_lines.index(min(current_lines))
                skips += 1
                if skips >= SKIP_SIZE:
                    doc_dict[0].append(int(current_lines[min_index][0]))
                    doc_dict[1].append(out_index.tell())
                    skips = 0
                out_index.write(','.join(current_lines[min_index]))
                current_lines[min_index] = self._read_partial_line(partial_files[min_index])
                if not current_lines[min_index]:
                    partial_files[min_index].close()
                    del partial_files[min_index]
                    del current_lines[min_index]
        dir = os.path.dirname(self.__document_map_index)
        if os.path.isdir(os.path.join(dir, DOCUMENT_MAP_TMP_DIR)):
            shutil.rmtree(os.path.join(dir, DOCUMENT_MAP_TMP_DIR))
        return doc_dict

    def _read_partial_line(self, file_handle):
        line = file_handle.readline()
        if line:
            return tuple(line.split(','))
        else:
            return None
