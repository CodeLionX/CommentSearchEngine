import os

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
        self.__articleFilePath      = os.path.join(directory, "articleMapping.data")
        self.__authorsFilePath      = os.path.join(directory, "authorMapping.data")


    def index(self):
        # cleanup
        self.__deleteAllPreviousIndexFiles()

        # indexing
        self.__index = InvertedIndexWriter(self.__directory)
        documentMap = DocumentMap(self.__documentMapPath).open()

        #print("Starting indexing...")
        with CommentReader(self.__commentsFilePath, self.__articleFilePath, self.__authorsFilePath) as dataFile:
            lastPointer = None
            for data in dataFile:
                if lastPointer == None:
                    lastPointer = dataFile.startSeekPointer()
                try:
                    documentMap.get(data["commentId"])
                except KeyError:
                    tokens = self.__processComment(data["commentId"], data["comment_text"])
                    documentMap.insert(data["commentId"], lastPointer)
                    self.__index.incDocumentCounter()
                
                lastPointer = dataFile.currentSeekPointer()

        #print("Saving index...")
        documentMap.close()
        self.__index.close()


    def __deleteAllPreviousIndexFiles(self):
        if os.path.exists(self.__documentMapPath):
            os.remove(self.__documentMapPath)

        if os.path.exists(self.__dictionaryPath):
            os.remove(self.__dictionaryPath)

        if os.path.exists(self.__postingListsPath):
            os.remove(self.__postingListsPath)


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
            positionList.append(int(position))
            tokenPositionsDict[token] = positionList

        for token in tokenPositionsDict:
            positionsList = tokenPositionsDict[token]
            # already sorted:
            #positionsList.sort()
            self.__index.insert(token, cid, tokens, positionsList)

        return tokens



if __name__ == "__main__":
    import time
    from cse.lang import PreprocessorBuilder
    from cse.SearchEngine import CustomPpStep
    prep = (
        PreprocessorBuilder()
        .useNltkTokenizer()
        #.useNltkStopwordList()
        .usePorterStemmer()
        .addCustomStepToEnd(CustomPpStep())
        .build()
    )

    start = time.process_time()
    FileIndexer("data", prep).index()
    end = time.process_time()

    print("==========================================")
    print("elapsed time:", end - start, "secs")

    # test document map and comment reading
    dm = DocumentMap(os.path.join("data", "documentMap.index")).open()
    print(dm.get(1))

    reader = CommentReader(os.path.join("data", "comments.data"), os.path.join("data", "articleMapping.data"), os.path.join("data", "authorMapping.data")).open()
    start = time.process_time()
    for i in range(0, 10000, 100):
        reader.readline(dm.get(i))
    end = time.process_time()
    withoutArticleMapping = end -start

    start = time.process_time()
    for i in range(0, 10000, 100):
        reader.readline(dm.get(i), skipArticleMapping=False)
    end = time.process_time()
    withArticleMapping = end -start

    print("==========================================")
    print("timings for loading 100 comments from different positions (seeking)")
    print("\nelapsed time without article mapping:")
    print("\t", withoutArticleMapping, "secs")
    print("\nelapsed time with article mapping:")
    print("\t", withArticleMapping, "secs")
