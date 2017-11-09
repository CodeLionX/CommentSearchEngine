class Preprocessor(object):

    __tokenizer = None
    __steps = []


    def __init__(self, tokenizer, steps):
        self.__tokenizer = tokenizer
        self.__steps = steps


    def processText(self, comment):
        tokens = self.__tokenizer.tokenize(comment)

        ###### which way is faster?
        for step in self.__steps:
            tokens = step.processAll(tokens)
        ######
        pTokens = []
        for token in tokens:
            pT = token
            for step in self.__steps:
                pT = step.process(pT)
            pTokens.append(pT)
        tokens = pTokens
        ###### which way is faster?

        return tokens