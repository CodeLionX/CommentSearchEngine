import os

from cse.helper.MultiFileMap import MultiFileMap
from cse.indexing import InvertedIndexWriter
from cse.indexing import DocumentMap
from cse.reader import CommentReader



class FileIndexer(object):


    def __init__(self, directory, preprocessor):
        self.__directory = directory
        self.__prep = preprocessor
        self.__multiFileIndexPath   = os.path.join(directory, "multiFileIndex.index")
        self.__documentMapPath      = os.path.join(directory, "documentMap.index")
        self.__dictionaryPath       = os.path.join(directory, "dictionary.index")
        self.__postingListsPath     = os.path.join(directory, "postingLists.index")
        self.__dataFolderPath       = os.path.join(directory, "raw")
        self.__commentsFilePath     = os.path.join(directory, "comments.data")
        self.__articleFilePath      = os.path.join(directory, "articleIds.data")
        self.__authorsFilePath      = os.path.join(directory, "authorMapping.data")


    def index(self):
        self.__index = InvertedIndexWriter(self.__directory)
        documentMap = DocumentMap(self.__documentMapPath).open()

        #print("Starting indexing...")
        with CommentReader(self.__commentsFilePath, self.__articleFilePath, self.__authorsFilePath) as dataFile:
            for pointer, data in enumerate(dataFile):
                try:
                    documentMap.get(data["commentId"])
                except KeyError:
                    tokens = self.__processComment(data["commentId"], data["comment_text"])
                    documentMap.insert(data["commentId"], pointer, tokens)
                    self.__index.incDocumentCounter()

        #print("Saving index...")
        documentMap.close()
        self.__index.close()



    def indexMultiFile(self):
        raise DeprecationWarning("deprecated and not longer supported")


    def __createMultiFileIndex(self):
        from cse.helper.createIndex import createMultiFileIndex
        createMultiFileIndex(self.__directory, os.path.basename(self.__multiFileIndexPath))


    def __createIndexForArticle(self, filename):
        cr = CommentReader(os.path.join("data", "raw", filename))
        cr.open()
        fileData = cr.readAllData()

        for cid in fileData["comments"]:
            self.__processComment(cid, fileData["comments"][cid]["comment_text"])

        cr.close()


    def __processComment(self, cid, comment):
        tokenTuples = self.__prep.processText(comment)
        tokens = len(tokenTuples)

        tokenPositionsDict = {}
        for token, position in tokenTuples:
            positionList = tokenPositionsDict.get(token, [])
            positionList.append(position)
            positionList.sort()
            tokenPositionsDict[token] = positionList

        for token in tokenPositionsDict:
            self.__index.insert(token, cid, tokens, tokenPositionsDict[token])

        return tokens



if __name__ == "__main__":
    from cse.lang import PreprocessorBuilder
    prep = (
        PreprocessorBuilder()
        .useNltkTokenizer()
        .useNltkStopwordList()
        .usePorterStemmer()
        #.addCustomStepToEnd(CustomPpStep())
        .build()
    )
    FileIndexer("data", prep).index()
