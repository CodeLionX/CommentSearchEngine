"""
CSE - a web crawling and web searching application for news paper
comments written in Python

simple language processing for transforming text into indexable tokens
"""
import abc

from cse.lang.Preprocessor import Preprocessor
from cse.lang.NltkTokenizer import NltkTokenizer
from cse.lang.NltkStopwordFilter import NltkStopwordFilter
from cse.lang.NltkStemmer import NltkStemmer
from cse.lang.NltkLemmatizer import NltkLemmatizer


class PreprocessorBuilder(object):

    __useStopwords = False
    __useStemming = False
    __useLemmatizing = False

    __stopwords = []
    __tokenizer = None
    __stemmer = None
    __lemmatizer = None
    __custemSteps = []


    def __init__(self):
        pass


    def useNltkTokenizer(self):
        self.__tokenizer = NltkTokenizer()
        return self


    def useNltkStopwordList(self):
        self.__useStopwords = True
        self.__stopwords = NltkStopwordFilter.english()
        return self


    def useCustomStopwordList(self, stopwords):
        self.__useStopwords = True
        self.__stopwords = stopwords
        return self


    def appendToStopwordList(self, *stopwords):
        self.__useStopwords = True
        self.__stopwords = self.__stopwords + list(stopwords)
        return self


    def usePorterStemmer(self):
        self.__useStemming = True
        self.__stemmer = NltkStemmer(NltkStemmer.porter())
        return self


    def useNltkLemmatizer(self):
        self.__useLemmatizing = True
        self.__lemmatizer = NltkLemmatizer(NltkLemmatizer.nltkDefault())
        return self


    def addCustomStepToEnd(self, step):
        self.__custemSteps.append(step)
        return self


    def build(self):
        if not self.__tokenizer:
            raise Exception("You must specify at least a tokenizer to use the preprocessor!")
        if self.__useStemming and self.__useLemmatizing:
            raise Exception("You can't use both Stemmer and Lemmatizer at the same time!")

        steps = []
        if self.__useStopwords:
            steps.append(NltkStopwordFilter(self.__stopwords))

        if self.__useStemming and not self.__useLemmatizing:
            steps.append(self.__stemmer)

        if self.__useLemmatizing and not self.__useStemming:
            steps.append(self.__lemmatizer)

        if self.__custemSteps:
            for step in self.__custemSteps:
                steps.append(step)

        return Preprocessor(self.__tokenizer, steps)



if __name__ == '__main__':
    prep = (
        PreprocessorBuilder()
        .useNltkTokenizer()
        .useNltkStopwordList()
        .appendToStopwordList("a", "of")
        #.usePorterStemmer()
        .useNltkLemmatizer()
        .build()
    )
    tokenTuples = prep.processText("WordNet® is a large lexical database of English. Nouns, verbs, adjectives and adverbs are grouped into sets of cognitive synonyms (synsets), each expressing a distinct concept. Synsets are interlinked by means of conceptual-semantic and lexical relations. The resulting network of meaningfully related words and concepts can be navigated with the browser. WordNet is also freely and publicly available for download. WordNet’s structure makes it a useful tool for computational linguistics and natural language processing.")
    for term, position in tokenTuples:
        print(term, position)
