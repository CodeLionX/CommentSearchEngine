import abc

class PostingListBase(abc.ABC):

    def __init__(self, idf):
        self._idf = idf
        self._postingList = []


    def _setPostingList(self, postingList):
        self._postingList = postingList

    def updateIdf(self, idf):
        self._idf = idf
    
    def numberOfPostings(self):
        return len(self._postingList)

    @abc.abstractmethod
    def append(self, cid, tf, positionList):
        pass

    @abc.abstractmethod
    def merge(cls1, cls2):
        pass

    @abc.abstractstaticmethod
    def decode(line):
        pass


class StringCodec(PostingListBase):

    @staticmethod
    def decode(line):
        # postingList line: <idf>;<cid1>|<tf1>|<pos1>,<pos2>,<pos3>;<cid2>|<tf2>|<pos1>,<pos2>\n
        # result:           (idf, [(cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])])
        # result type:      tuple[float, list[tuple[string, float, list[int]]]]
        plList = list(line.replace("\n", "").split(";"))
        result = StringCodec(float(plList[0]))
        result._setPostingList(list(
            map(
                lambda l: (int(l[0]), float(l[1]), [int(pos) for pos in l[2].split(",")]),
                map(
                    lambda s: s.split("|"),
                    plList[1:]
                )
            )
        ))
        return result


    def append(self, cid, tf, positionList):
        self._postingList.append((cid, tf, positionList))


    def merge(cls1, cls2):
        """
        Preserves idf of the first arguments posting list and appends the second
        arguments posting list to the first one.
        """
        result = StringCodec(cls1._idf)
        result._setPostingList(cls1._postingList + cls2._postingList)
        return result


    def encode(cls):
        # idf:              idf
        # postingList:      [(cid1, tf1, [pos1, pos2, pos3]), (cid2, tf2, [pos1, pos2])]
        # postingList type: list[tuple[string, int, list[int]]]
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



class DeltaCodec(PostingListBase):

    def __init__(self, idf):
        super().__init__(idf)
        self.__baseCid = 0

    def append(self, cid, tf, positionList):
        self._postingList.append((cid - self.__baseCid, tf, positionList))
        self.__baseCid = cid

    def merge(cls1, cls2):
        """
        Preserves idf of the first arguments posting list and appends the second
        arguments posting list to the first one.
        """
        result = StringCodec(cls1._idf)
        firstNewCid, newTf, newPositionList = cls2._postingList[0]
        result._setPostingList(cls1._postingList + [(firstNewCid - cls1.__baseCid, newTf, newPositionList)] + cls2._postingList[1:])
        return result



class PostingList(DeltaCodec, StringCodec, PostingListBase):
    pass



if __name__ == "__main__":
    p = PostingList(0.86)
    p.append(112, 0.1, [1,2,3])
    p.append(113, 0.112, [1,5,9])
    p.append(115, 0.23, [1,3,19])
    p.append(116, 0.002, [9,18,22])
    p2 = PostingList(0)
    p2.append(130, 0.001, [9])
    p2.append(131, 0.02, [4,7,9])

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
