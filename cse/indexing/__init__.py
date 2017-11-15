"""
CSE - a web crawling and web searching application for news paper
comments written in Python

index creation and using package, this package also deales with the index persistence
"""
import os
from cse.indexing.InvertedIndexWriter import InvertedIndexWriter
from cse.indexing.InvertedIndexReader import InvertedIndexReader



def dictTest():
    from cse.indexing.Dictionary import Dictionary
    d = Dictionary(os.path.join("data", "dictionary.index"))

    if "hello" in d:
        pointer = d["hello"]
    else:
        pointer = 2
        d["hello"] = pointer
    print(d["hello"])

    if "hello" in d:
        pointer = d["hello"]
    else:
        pointer = 3
        d["hello"] = pointer
    print(d["hello"])


def deltaTest():
    from cse.indexing.DeltaPostingListIndex import DeltaPostingListIndex
    i = DeltaPostingListIndex()
    i.insert(2, "cid1")
    cid = i.retrieve(2)
    print(cid)
    i[5] = "cid2"
    i[5] = "cid3"
    print(i[5])
    print(list(i))
    print(5 in i)
    print(6 in i)


if __name__ == '__main__':
    dictTest()
    deltaTest()
