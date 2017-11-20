from enum import Enum

class QueryParser(object):

    __queryTokens = []


    def __init__(self, query):
        self.__queryTokens = self.__tokenize(query, Operator.NOT)


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
    NOT = 1
    AND = 2
    OR = 3



query = "bla NOT blas OR blub AND fasel NOT my*"
print(QueryParser(query))