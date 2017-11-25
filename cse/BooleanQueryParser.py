from enum import Enum

class BooleanQueryParser(object):

    __queryTokens = []


    def __init__(self, query):
        #query = query.replace("*", "STAR")
        self.__queryTokens = self.__tokenize(query, Operator.STAR)


    def __str__(self):
        tokens = [str(token) for token in self.__queryTokens]
        return " ".join(tokens)


    def get(self, ):
        return self.__queryTokens


    def __tokenize(self, query, op):
        tmp = []
        noNextOp = False
        try:
            nextOp = Operator(op.value + 1)
        except ValueError:
            noNextOp = True

        for e in query.split(op.name):
            if noNextOp:
                tmp.append(e.strip())
            else:
                tmp = tmp + self.__tokenize(e.strip(), nextOp)
            tmp.append(op)
        tmp.pop()
        return tmp



class Operator(Enum):
    #STAR = 1
    NOT = 2
    AND = 3
    OR = 4



if __name__ == '__main__':
    print(BooleanQueryParser("bla NOT blas"))
    print(BooleanQueryParser("blas OR blub"))
    print(BooleanQueryParser("blub AND fasel"))
    print(BooleanQueryParser("fasel NOT my*"))
    print(BooleanQueryParser("x* AND c NOT d"))
