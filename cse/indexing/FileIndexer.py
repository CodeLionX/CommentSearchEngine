import os

from cse.indexing.PostingIndexWriter import PostingIndexWriter
from cse.indexing.ReplyToIndexWriter import ReplyToIndexWriter
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
        self.__replyToDictPath      = os.path.join(directory, "replyToDict.index")
        self.__replyToListsPath     = os.path.join(directory, "replyToLists.index")
        self.__dataFolderPath       = os.path.join(directory, "raw")
        self.__commentsFilePath     = os.path.join(directory, "comments.data")
        self.__articleFilePath      = os.path.join(directory, "articleMapping.data")
        self.__authorsFilePath      = os.path.join(directory, "authorMapping.data")


    def index(self):
        # cleanup
        self.__deletePreviousIndexFiles()

        # setup index writers
        pIndex = PostingIndexWriter(self.__dictionaryPath, self.__postingListsPath)
        rIndex = ReplyToIndexWriter(self.__replyToListsPath, self.__replyToListsPath)
        documentMap = DocumentMap(self.__documentMapPath).open()

        # start indexing the comments file
        #print("Starting indexing...")
        with CommentReader(self.__commentsFilePath, self.__articleFilePath, self.__authorsFilePath) as dataFile:
            lastPointer = None
            for data in dataFile:
                if lastPointer == None:
                    lastPointer = dataFile.startSeekPointer()
                try:
                    documentMap.get(data["commentId"])
                except KeyError:
                    # update document map
                    documentMap.insert(data["commentId"], lastPointer)
                    # index comment text tokens
                    tokens = self.__processComment(pIndex, data["commentId"], data["comment_text"])
                    pIndex.incDocumentCounter()
                    # index comment parent-child structure
                    cid = data["commentId"]
                    parentCid = data["parent_comment_id"]
                    if parentCid:
                        rIndex.insert(parentCid, cid)

                lastPointer = dataFile.currentSeekPointer()

        #print("Saving index...")
        documentMap.close()
        pIndex.close()
        rIndex.close()


    def indexPostingList(self):
        # cleanup
        self.__deletePreviousIndexFiles(replyToLists=False)

        # setup index writers
        pIndex = PostingIndexWriter(self.__dictionaryPath, self.__postingListsPath)
        documentMap = DocumentMap(self.__documentMapPath).open()

        # start indexing the comments file
        #print("Starting indexing...")
        with CommentReader(self.__commentsFilePath, self.__articleFilePath, self.__authorsFilePath) as dataFile:
            lastPointer = None
            for data in dataFile:
                if lastPointer == None:
                    lastPointer = dataFile.startSeekPointer()
                try:
                    documentMap.get(data["commentId"])
                except KeyError:
                    # update document map
                    documentMap.insert(data["commentId"], lastPointer)
                    # index comment text tokens
                    tokens = self.__processComment(data["commentId"], data["comment_text"])
                    pIndex.incDocumentCounter()

                lastPointer = dataFile.currentSeekPointer()

        #print("Saving index...")
        documentMap.close()
        pIndex.close()
        pIndex = None


    def indexReplyToList(self):
        # cleanup
        self.__deletePreviousIndexFiles(documentMap=False, postingLists=False)

        # setup index writers
        rIndex = ReplyToIndexWriter(self.__replyToDictPath, self.__replyToListsPath)

        # start indexing the comments file
        #print("Starting indexing...")
        with CommentReader(self.__commentsFilePath, self.__articleFilePath, self.__authorsFilePath) as dataFile:
            lastPointer = None
            for data in dataFile:
                if lastPointer == None:
                    lastPointer = dataFile.startSeekPointer()

                # index comment parent-child structure
                cid = data["commentId"]
                parentCid = data["parent_comment_id"]
                if parentCid:
                    rIndex.insert(parentCid, cid)
                lastPointer = dataFile.currentSeekPointer()

        #print("Saving index...")
        rIndex.close()
        rIndex = None


    def __deletePreviousIndexFiles(self, documentMap=True, postingLists=True, replyToLists=True):
        if documentMap and os.path.exists(self.__documentMapPath):
            os.remove(self.__documentMapPath)

        if postingLists and os.path.exists(self.__dictionaryPath):
            os.remove(self.__dictionaryPath)

        if postingLists and os.path.exists(self.__postingListsPath):
            os.remove(self.__postingListsPath)

        if replyToLists and os.path.exists(self.__replyToDictPath):
            os.remove(self.__replyToDictPath)

        if replyToLists and os.path.exists(self.__replyToListsPath):
            os.remove(self.__replyToListsPath)


    def __processComment(self, index, cid, comment):
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
            index.insert(token, cid, tokens, positionsList)

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
    FileIndexer("data", prep).indexReplyToList()
    end = time.process_time()

    print("==========================================")
    print("elapsed time:", end - start, "secs")

    """
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
    """
