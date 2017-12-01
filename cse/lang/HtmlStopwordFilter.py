import re

from cse.lang.PreprocessorStep import PreprocessorStep

class HtmlStopwordFilter(PreprocessorStep):

    __inlineJS = r"(?is)<(script|style).*?>.*?(</\1>)"
    __htmlComments = r"(?s)<!--(.*?)-->[\n]?"
    __tags = r"(?s)<.*?>"


    def __init__(self, stopwordList):
        # lookup is faster in a set than a list
        self.__stopwordlist = set(stopwordList)


    def processAll(self, tokenTuples):
        return [(self.__cleanHtml(token), position) for token, position in tokenTuples]


    def process(self, tokenTuple):
        return self.__clean_html(tokenTuple[0])


    def __cleanHtml(html):
        """
        Copied from NLTK package.
        Remove HTML markup from the given string.

        :param html: the HTML string to be cleaned
        :type html: str
        :rtype: str
        """

        # First we remove inline JavaScript/CSS:
        cleaned = re.sub(self.__inlineJS, "", html.strip())
        # Then we remove html comments. This has to be done before removing regular
        # tags since comments can contain '>' characters.
        cleaned = re.sub(self.__htmlComments, "", cleaned)
        # Next we can remove the remaining tags:
        cleaned = re.sub(self.__tags " ", cleaned)
        # Finally, we deal with whitespace
        cleaned = re.sub(r"&nbsp;", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        cleaned = re.sub(r"  ", " ", cleaned)
        return cleaned.strip()