from sys import getsizeof



class DeltaIndex(object):
    """
    Inverted Index (delta - in memory)
    idf is not calculated until a delta merge is performed (see InvertedIndexWriter for that)
    """

    ESTIMATION_MARGIN = 300


    def __init__(self, entryContainerConstructor, entrySize=42):
        self._deltaIndexDict = {}
        self._entryContainerConstructor = entryContainerConstructor
        self._entrySize = entrySize
        self._numDocuments = 0


    def retrieve(self, key):
        if key not in self._deltaIndexDict:
            return None
        return self._deltaIndexDict[key]


    def insert(self, key, entry):
        if key not in self._deltaIndexDict:
            self._deltaIndexDict[key] = self._entryContainerConstructor()
        self._deltaIndexDict[key].append(entry)
        self._numDocuments = self._numDocuments + 1


    def clear(self):
        self._deltaIndexDict = {}
        self._numDocuments = 0


    def estimatedSize(self):
        return getsizeof(self)


    def lines(self):
        return self._deltaIndexDict.keys()


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
