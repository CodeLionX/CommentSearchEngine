class Preprocessor(object):

    __tokenizer = None
    __steps = []


    def __init__(self, tokenizer, steps):
        self.__tokenizer = tokenizer
        self.__steps = steps


    def processText(self, comment):
        tokens = self.__tokenizer.tokenize(comment)
        tokenTuple = [(token, position) for position, token in enumerate(tokens)]

        ###### which way is faster?
        for step in self.__steps:
            tokenTuple = step.processAll(tokenTuple)
        ######
        """
        pTokenTuple = []
        for token, position in tokenTuple:
            pT = (token, position)
            for step in self.__steps:
                pT = step.process(pT)
            if pT: pTokenTuple.append(pT)
        tokenTuple = pTokenTuple
        """
        ###### which way is faster?
        ## doesn't make a huge difference:
        """
           ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        first one:
           81098    0.342    0.000  114.429    0.001 /vagrant/cse/lang/Preprocessor.py:12(processText)
           81098    0.057    0.000   65.668    0.001 /vagrant/cse/lang/NltkStemmer.py:22(processAll)
        compared to second one:
           81098    2.708    0.000  119.330    0.001 /vagrant/cse/lang/Preprocessor.py:12(processText)
         2955756    1.275    0.000   67.069    0.000 /vagrant/cse/lang/NltkStemmer.py:26(process)

        --> only about 5 seconds difference in cumulative execution time for 81098 calls        
        """

        return tokenTuple
