import os

from cse.helper.MultiFileMap import MultiFileMap
from cse.indexing import InvertedIndexWriter
from cse.indexing import DocumentMap
from cse.CommentReader import CommentReader



class FileIndexer(object):


    def __init__(self, directory, preprocessor):
        self.__directory = directory
        self.__prep = preprocessor
        self.__multiFileIndexPath   = os.path.join(directory, "multiFileIndex.index")
        self.__documentMapPath      = os.path.join(directory, "documentMap.index")
        self.__dictionaryPath       = os.path.join(directory, "dictionary.index")
        self.__postingListsPath     = os.path.join(directory, "postingLists.index")
        self.__dataFolderPath       = os.path.join(directory, "raw")
        self.__dataFilePath         = os.path.join(directory, "comments.data")


    def index(self):
        self.__index = InvertedIndexWriter(self.__directory)
        documentMap = DocumentMap(self.__documentMapPath).open()

        #print("Starting indexing...")
        with CommentReader(self.__dataFilePath) as dataFile:
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
        # load multi file index
        if not os.path.exists(self.__multiFileIndexPath):
            print("multifile index does not exist...creating new one")
            self.__createMultiFileIndex()

        multiFileMap = MultiFileMap()
        multiFileMap.loadJson(self.__multiFileIndexPath)
        self.__index = InvertedIndexWriter(self.__directory)

        print("multifile index and inverted index instance loaded")

        # load all article ids = filenames
        filenames = []
        for cid in multiFileMap.listCids():
            filenames.append(multiFileMap.get(cid)["fileId"])

        # process each file
        for filename in set(filenames):
            print("Processing file", filename)
            self.__createIndexForArticle(filename)
            self.__index.incDocumentCounter()

        self.__index.close()


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
