import os
import errno
import shutil

from cse.util import PackerUtil
from cse.indexing.commons import PARTIAL_THRESHOLD, SKIP_SIZE, DICT_TMP_DIR

class DictionaryBuilder(object):
    """
    Dictionary (in memory)
    Structure: Term -> (Seek pointer, PostingList Size in Bytes)
    """


    def __init__(self, dictionary_index_path, dictionary_dict_path):
        self.__dictionary_index_path = dictionary_index_path
        self.__dictionary_dict_path = dictionary_dict_path
        dir = os.path.dirname(self.__dictionary_dict_path)
        self.__tmp_dir = os.path.join(dir, DICT_TMP_DIR + '_' + os.path.basename(self.__dictionary_dict_path))
        self.__dictionary = []
        self.__i = 0
        self.__content = 0
        self.__open()

    def __open(self):
        if os.path.exists(self.__dictionary_index_path):
            os.remove(self.__dictionary_index_path)
        if os.path.exists(self.__dictionary_dict_path):
            os.remove(self.__dictionary_dict_path)
        if os.path.isdir(self.__tmp_dir):
            shutil.rmtree(self.__tmp_dir)

    def __clear(self):
        self.__dictionary = []
        self.__content = 0
        self.__i += 1

    def save(self):
        pass

    def close(self):
        self.__dictionary.sort()
        self.__save_partial_index(self.__dictionary, self.__i)
        dic_dict = self._build_index_and_dict()
        PackerUtil.packToFile(dic_dict, self.__dictionary_dict_path, type=PackerUtil.PICKLE)
        self.__clear()

    def insert(self, term, pointer, size):
        self.__dictionary.append((term, int(pointer)))
        self.__content += 1
        if self.__content >= PARTIAL_THRESHOLD:
            self.__dictionary.sort()
            self.__save_partial_index(self.__dictionary, self.__i)
            self.__clear()

    def __save_partial_index(self, partial_list, i):
        file_name = os.path.basename(self.__dictionary_index_path)
        if not os.path.exists(self.__tmp_dir):
            os.makedirs(self.__tmp_dir)

        with open(os.path.join(self.__tmp_dir, file_name + str(i)), 'w') as partial:
            for tuple in partial_list:
                partial.write(str(tuple[0]) + ',' + str(tuple[1]) + '\n')

    def _build_index_and_dict(self):
        dic_dict = ([], [])
        partials_dir = self.__tmp_dir
        partial_files = []
        current_lines = []
        skips = SKIP_SIZE
        with open(self.__dictionary_index_path, 'w') as out_index:
            for file in os.listdir(partials_dir):
                partial_files.append(open(os.path.join(partials_dir, file)))

            for file_handle in partial_files:
                current_lines.append(self._read_partial_line(file_handle))

            while partial_files:
                min_index = current_lines.index(min(current_lines))
                skips += 1
                if skips >= SKIP_SIZE:
                    dic_dict[0].append(str(current_lines[min_index][0]))
                    dic_dict[1].append(out_index.tell())
                    skips = 0
                out_index.write(','.join(current_lines[min_index]))
                current_lines[min_index] = self._read_partial_line(partial_files[min_index])
                if not current_lines[min_index]:
                    partial_files[min_index].close()
                    del partial_files[min_index]
                    del current_lines[min_index]
        # TODO delete partial files
        return dic_dict

    def _read_partial_line(self, file_handle):
        line = file_handle.readline()
        if line:
            return tuple(line.split(','))
        else:
            return None

    def __len__(self):
        return self.__dictionary.__len__()

    def __setitem__(self, key, value):
        self.insert(key, value[0], value[1])

    def iterkeys(self): self.__iter__()
    def __iter__(self):
        return self.__dictionary.__iter__()

    def __str__(self):
        return str(self.__dictionary)

