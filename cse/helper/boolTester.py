import functools

from cse.BooleanQueryParser import Operator

def cidSetCombiner(op):
    def notFunc(x, y):
        return x - y
    def andFunc(x, y):
        return x & y
    def orFunc(x, y):
        return x | y

    switcher = {
        Operator.NOT: notFunc,
        Operator.AND: andFunc,
        Operator.OR:  orFunc
    }
    return switcher.get(op)


def test(op):
    cidSets = [
        {1,2,5,7,9},
        {2,5,11,13,17},
        {2,7,20,13}
    ]


    firstCids = cidSets[0]
    cidSets.remove(firstCids)
    cids = functools.reduce(cidSetCombiner(op), cidSets, firstCids)
    print(cids)
    return cids


if __name__ == "__main__":
    assert(test(Operator.AND) == {2})
    assert(test(Operator.OR)  == {1, 2, 5, 7, 9, 11, 13, 17, 20})
    assert(test(Operator.NOT) == {1,9})
    print("all tests passed")