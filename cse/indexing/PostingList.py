import abc
import msgpack

from cse.WeightCalculation import calcIdf


class PostingListBase(abc.ABC):

    def __init__(self):
        self._idf = 0
        self._postingList = []

    def setPostingList(self, postingList):
        self._postingList = postingList
    
    def postingList(self):
        return self._postingList

    def numberOfPostings(self):
        return len(self._postingList)

    def updateIdf(self, nDocuments):
        try:
            self._idf = calcIdf(nDocuments, self.numberOfPostings())
        except ZeroDivisionError:
            self._idf = 0
    
    def idf(self):
        return self._idf

    def append(self, values):
        # cid, tf, positionList = values[0], values[1], values[2]
        self._postingList.append(values)

    def merge(cls1, cls2):
        """
        Preserves idf of the first arguments posting list and appends the second
        arguments posting list to the first one. Sorts the new list afterwards.
        """
        result = PostingList()
        result._idf = cls1._idf
        postingList = cls1._postingList + cls2._postingList
        postingList.sort(key=lambda x: x[0])
        result._postingList = postingList
        return result

    @abc.abstractmethod
    def encode(cls):
        pass

    @abc.abstractstaticmethod
    def decode(line):
        pass


class PostingListStringBase(PostingListBase):
    """
    ** OBSOLETE **

    Old interface for writing the posting lists encoded as strings (with separator chars) to disk.
    This is not supported anymore!
    """

    def encode(cls):
        # idf:              idf
        # postingList:      [(cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])]
        # postingList type: list[tuple[int, float, list[int]]]
        # result:           <idf>;<cid1>|<tf1>|<pos1>,<pos2>,<pos3>;<cid2>|<tf2>|<pos1>,<pos2>\n
        return ";".join([str(cls._idf)] + [
            str(termTuple[0])
                + "|"
                + str(termTuple[1])
                + "|"
                + ",".join(
                    str(position) for position in termTuple[2]
                )
            for termTuple in cls._postingList
        ]) + "\n"

    @staticmethod
    def decode(line):
        # postingList line: <idf>;<cid1>|<tf1>|<pos1>,<pos2>,<pos3>;<cid2>|<tf2>|<pos1>,<pos2>\n
        # result:           (idf, [(cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])])
        # result type:      tuple[float, list[tuple[string, float, list[int]]]]
        plList = list(line.replace("\n", "").split(";"))
        result = PostingList()
        result._idf = float(plList[0])
        result._postingList = list(
            map(
                lambda l: (int(l[0]), float(l[1]), [int(pos) for pos in l[2].split(",")]),
                map(
                    lambda s: s.split("|"),
                    plList[1:]
                )
            )
        )
        return result


class PostingListBinaryBase(PostingListBase):

    def encode(cls):
        return msgpack.packb((cls._idf, cls._postingList))

    @staticmethod
    def decode(line):
        t = msgpack.unpackb(line)
        result = PostingList()
        result._idf = t[0]
        result._postingList = list(t[1])
        return result


class CidDeltaCodec(PostingListBase):

    def __init__(self):
        super().__init__()
        self.__baseCid = 0
        self.__plWasDecoded = False

    def append(self, values):
        cid, tf, positionList = values
        self._postingList.append((cid - self.__baseCid, tf, positionList))
        self.__baseCid = cid

    def merge(main, delta):
        """
        Preserves idf of the first arguments posting list and appends the second
        arguments posting list to the first one.
        """
        result = PostingList()
        firstNewCid, newTf, newPositionList = delta._postingList[0]
        result._idf = main._idf

        # calc old base cid of main object
        mainBaseCid, _, _ = main._postingList[0]
        for cid, _, _ in main._postingList[1:]:
            mainBaseCid += cid

        result._postingList = main._postingList + [(firstNewCid - mainBaseCid, newTf, newPositionList)] + delta._postingList[1:]
        return result

    def postingList(self):
        """
        Decodes delta encoded cids and returns the posting list containing
        cid, tf, positionList
        """
        if self._postingList and not self.__plWasDecoded:
            self._postingList = self.__decodeCids(self._postingList)
            self.__plWasDecoded = True

        return self._postingList

    def __decodeCids(self, encodedPl):
        postingList = []
        firstCid, firstTf, firstPositionList = encodedPl[0]
        postingList.append((firstCid, firstTf, firstPositionList))

        runningCid = firstCid
        for deltaCid, tf, positionList in encodedPl[1:]:
            runningCid += deltaCid
            postingList.append((runningCid, tf, positionList))

        return postingList



class PostingList(CidDeltaCodec, PostingListBinaryBase):
    pass



if __name__ == "__main__":
    p = PostingList()
    p.append((112, 0.1, [1,2,3]))
    p.append((113, 0.112, [1,5,9]))
    p.append((115, 0.23, [1,3,19]))
    p.append((116, 0.002, [9,18,22]))
    p.updateIdf(6)
    p2 = PostingList()
    p2.append((130, 0.001, [9]))
    p2.append((131, 0.02, [4,7,9]))
    p2.updateIdf(6)

    pl1 = p.encode()
    pl2 = p2.encode()
    merged = p.merge(p2).encode()
    print("PL1", pl1)
    print("PL2", pl2)
    print("MERGED:", merged)

    print("==================")
    pl11 = PostingList.encode(p)
    pl21 = PostingList.encode(p2)
    merged1 = PostingList.encode(PostingList.merge(p, p2))
    print("PL1", pl11)
    print("PL2", pl21)
    print("MERGED:", merged1)
    assert(pl1 == pl11)
    assert(pl2 == pl21)
    assert(merged == merged1)

    print("==================")
    plString = PostingList.encode(p)
    p3 = PostingList.decode(plString)
    plString2 = p3.encode()
    print("Encode/Decode/Encode P1:", plString2)
    assert(plString == plString2)

    print("to StringCodec for output purposes:")    
    test = PostingListStringBase()
    test._idf = p3._idf
    test._postingList = p3._postingList
    print(test.encode())
