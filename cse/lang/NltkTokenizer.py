import string
from nltk import word_tokenize, sent_tokenize


class NltkTokenizer(object):


    def __init__(self):
        pass


    def tokenize(self, text):
        # tokenize into sentences and sentences into lower case words
        tokens = [word.lower() for sent in sent_tokenize(text) for word in word_tokenize(sent)]
        # filter out punctuation
        tokens = filter(lambda word: word not in string.punctuation, tokens)
        # replace "n't" with "not"
        tokens = map(lambda word: word if word != "n't" else "not", tokens)
        tokens = [word.replace("'", "") for word in tokens]
        tokens = filter(lambda word: word, tokens)
        return list(tokens)