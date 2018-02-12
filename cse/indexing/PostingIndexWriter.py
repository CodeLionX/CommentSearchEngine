import os
import shutil

from os import remove
from tempfile import mkstemp
from shutil import move

from cse.WeightCalculation import calcTf
from cse.indexing.Dictionary import Dictionary
from cse.indexing.MainIndex import MainIndex
from cse.indexing.DeltaIndex import DeltaIndex
from cse.indexing.PostingList import PostingList
from cse.indexing.commons import POSTING_LIST_TMP_DIR

class PostingIndexWriter(object):

    MB = 1024*1024
    # threshold for delta index to reside in memory
    # if the memory consumption of the delta index itself gets higher than this threshold
    # a delta merge is performend and the index will be written to disk
    MEMORY_THRESHOLD = 5 * MB     # 500 MB
    # entry size estimation for simple heursitic to determine memory consumption of the
    # delta index
    POSTING_LIST_ENTRY_SIZE = 30    #  30 B


    def __init__(self, dictFilepath, mainFilepath):
        self.__dictionary = Dictionary(dictFilepath)
        self.__dIndex = DeltaIndex(PostingList, entrySize=PostingIndexWriter.POSTING_LIST_ENTRY_SIZE)
        self.__mIndexFilepath = mainFilepath
        self.__calls = 0
        self.__nDocuments = 0
        self.__i = 0
        dir = os.path.dirname(self.__mIndexFilepath)
        if os.path.isdir(os.path.join(dir, POSTING_LIST_TMP_DIR)):
            shutil.rmtree(os.path.join(dir, POSTING_LIST_TMP_DIR))


    def __should_create_partial(self):
        # check memory usage
        if self.__dIndex.estimatedSize() > PostingIndexWriter.MEMORY_THRESHOLD:
            self._save_partial()
            self.__calls = -1


    def close(self):
        self._save_partial()
        self.deltaMerge()
        self.__dictionary.close()


    def insert(self, term, commentId, nTerms, positions):
        self.__dIndex.insert(
            term,
            (int(commentId), calcTf(nTerms, len(positions)), positions)
        )

        if self.__calls % int(PostingIndexWriter.MEMORY_THRESHOLD / 250) == 0:
            self.__should_create_partial()

        self.__calls = self.__calls + 1


    def terms(self):
        return [term for term in self.__dictionary]


    def deltaMerge(self):
        # quit method early if no values are in delta
        dir = os.path.dirname(self.__mIndexFilepath)
        partials_dir = os.path.join(dir, POSTING_LIST_TMP_DIR)
        if not os.listdir(partials_dir):
            print(self.__class__.__name__ + ":", "no delta merge needed")
            return
        if self.__dIndex:
            self._save_partial()

        # init values
        # mIndex = MainIndex(self.__mIndexFilepath, PostingList.decode)
        # fh, tempFilePath = mkstemp(text=False)
        visited = set()

        # helper func
        def updateIdfAndWritePostingList(tempFile, postingList):
            postingList.updateIdf(self.__nDocuments)
            seekPosition = tempFile.tell()
            bytesWritten = tempFile.write(PostingList.encode(postingList))
            return seekPosition, bytesWritten

        # beginning of merge
        print("!! delta merge !!")

        with open(self.__mIndexFilepath, 'wb') as main_index_file:
            partial_files = []
            current_lines = []
            for file in os.listdir(partials_dir):
                partial_files.append(open(os.path.join(partials_dir, file)))

            for file_handle in partial_files:
                current_lines.append(self._read_partial_line(file_handle))

            while partial_files:
                min_line = min(current_lines, key=lambda x: x[0])
                min_indexes = [i for i,x in enumerate(current_lines) if x[0] == min_line[0]]

                #setup postinglist list
                posting_lists = []
                current_term = current_lines[min_indexes[0]][0]
                for index in min_indexes:
                    posting_lists.append(current_lines[index][1])

                if len(posting_lists) % 2 != 0 and len(posting_lists) > 1:
                    posting_lists[1] = posting_lists[0].merge(posting_lists[1])
                    del posting_lists[0]

                while len(posting_lists) > 1:
                    new_lists = []
                    for list1, list2 in pairwise(posting_lists):
                        new_lists.append(list1.merge(list2))
                    posting_lists = new_lists

                seekPosition, bytesWritten = updateIdfAndWritePostingList(main_index_file, posting_lists[0])
                self.__dictionary.insert(current_term, seekPosition, bytesWritten)
                for index in min_indexes:
                    current_lines[index] = self._read_partial_line(partial_files[index])

                for i, _ in enumerate(current_lines):
                    if not current_lines[i]:
                        partial_files[i].close()
                        del partial_files[i]
                        del current_lines[i]

        dir = os.path.dirname(self.__mIndexFilepath)
        if os.path.isdir(os.path.join(dir, POSTING_LIST_TMP_DIR)):
            shutil.rmtree(os.path.join(dir, POSTING_LIST_TMP_DIR))
        self.__dictionary.save()

    def _read_partial_line(self, file_handle):
        line = file_handle.readline()
        if line:
            term, posting_list_string = line.split('|||')

            return term, eval(posting_list_string.strip())
        else:
            return None

    def incDocumentCounter(self):
        self.__nDocuments += 1

    def _save_partial(self):
        dir = os.path.dirname(self.__mIndexFilepath)
        file_name = os.path.basename(self.__mIndexFilepath)
        if not os.path.exists(os.path.join(dir, POSTING_LIST_TMP_DIR)):
            os.makedirs(os.path.join(dir, POSTING_LIST_TMP_DIR))
        list = self.__dIndex.convert_to_sorted_list()
        with open(os.path.join(dir, POSTING_LIST_TMP_DIR, file_name + str(self.__i)), 'w') as partial:
            for posting_list in list:
                partial.write(str(posting_list[0]) + '|||' + repr(posting_list[1]) + '\n')
        print("saved_partial posting list {}".format(self.__i))
        self.__i += 1
        self.__dIndex.clear()

def pairwise(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

if __name__ == "__main__":
    # data
    doc1 = [("term1", [1]), ("term5", [2,4]), ("term2", [3]), ("term4", [5])]
    doc2 = [("term3", [1]), ("term2", [2,3,4])]
    doc3 = [("term1", [1]), ("term5", [2,3]), ("term2", [4])]
    doc4 = [("term2", [1,2,3])]

    # cleanup
    if os.path.exists(os.path.join("data", "test", "dictionary.index")):
        os.remove(os.path.join("data", "test", "dictionary.index"))
    if os.path.exists(os.path.join("data", "test", "postingLists.index")):
        os.remove(os.path.join("data", "test", "postingLists.index"))

    # indexing
    print("\n\n#### creating index ####\n")
    index = PostingIndexWriter(os.path.join("data", "test", "dictionary.index"), os.path.join("data", "test", "postingLists.index"))
    for term, posList in doc1:
        index.insert(term, 0, len(doc1), posList)
    index.incDocumentCounter()
    # delta merge
    index.deltaMerge()

    for term, posList in doc2:
        index.insert(term, 1, len(doc2), posList)
    index.incDocumentCounter()
    for term, posList in doc3:
        index.insert(term, 2, len(doc3), posList)
    index.incDocumentCounter()
    index.deltaMerge()

    for term, posList in doc4:
        index.insert(term, 3, len(doc4), posList)
    index.close()


    # check index structure
    print("\n\n#### checking index ####\n")
    from cse.indexing import IndexReader
    index = IndexReader(os.path.join("data", "test"))

    print("term1\n", index.idf("term1"), index.postingList("term1"), "\n")
    assert(len(index.postingList("term1")) == 2)

    print("term2\n", index.idf("term2"), index.postingList("term2"), "\n")
    assert(len(index.postingList("term2")) == 4)

    print("term3\n", index.idf("term3"), index.postingList("term3"), "\n")
    assert(len(index.postingList("term3")) == 1)

    print("term4\n", index.idf("term4"), index.postingList("term4"), "\n")
    assert(len(index.postingList("term4")) == 1)

    print("term5\n", index.idf("term5"), index.postingList("term5"), "\n")
    print(index.retrieve("term5").postingList())
    assert(len(index.postingList("term5")) == 2)
