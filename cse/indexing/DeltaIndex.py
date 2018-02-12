from sys import getsizeof



class DeltaIndex(object):
    """
    Inverted Index (delta - in memory)
    idf is not calculated until a delta merge is performed (see InvertedIndexWriter for that)
    """

    ESTIMATION_MARGIN = 300


    def __init__(self, entryContainerConstructor, entrySize=42):
        self._deltaIndexDict = {}
        self._deltaIndex = []
        self._entryContainerConstructor = entryContainerConstructor
        self._entrySize = entrySize
        self._numDocuments = 0


    def retrieve(self, key):
        if key not in self._deltaIndexDict:
            return None
        return self._deltaIndex[self._deltaIndexDict[key]][1]


    def insert(self, key, entry):

        if key == '':
            # TODO Quick and dirty. Normally this should never occur!
            return
        if key not in self._deltaIndexDict:
            tuple = (key, self._entryContainerConstructor())
            self._deltaIndex.append(tuple)
            index = self._deltaIndex.index(tuple)
            self._deltaIndexDict[key] = index
        index = self._deltaIndexDict[key]
        self._deltaIndex[index][1].append(entry)
        self._numDocuments = self._numDocuments + 1


    def clear(self):
        self._deltaIndexDict = {}
        self._deltaIndex = []
        self._numDocuments = 0


    def estimatedSize(self):
        return getsizeof(self)


    def lines(self):
        return self._deltaIndexDict.keys()

    def convert_to_sorted_list(self):
        self._deltaIndex.sort()
        return self._deltaIndex


    def __getitem__(self, key):
        value = self.retrieve(key)
        if value is None:
            raise KeyError
        return value


    def __setitem__(self, key, value):
        self.insert(key, value)


    def __iter__(self):
        return iter(self._deltaIndexDict)


    def __contains__(self, item):
        return item in self._deltaIndexDict


    def __sizeof__(self):
        return int(
            getsizeof(self._deltaIndexDict)
                + self._entrySize * self._numDocuments
                + DeltaIndex.ESTIMATION_MARGIN
        )


    def __len__(self):
        return len(self._deltaIndexDict)
