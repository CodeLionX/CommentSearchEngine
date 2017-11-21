import os

from cse.helper.MultiFileMap import MultiFileMap

class FileIndexer(object):


    def __init__(self):
        pass

    def indexMultiFile(self, directory):
        # lookup for article file ids
        multiFileMap = MultiFileMap()
        multiFileMap.loadJson(os.path.join(directory, "index.json"))

        # to be created inverted index
        ii = InvertedIndexWriter(directory)


        # for just one article
        """
        randomCid = multiFileMap.listCids()[0:1][0]
        filename = multiFileMap.get(randomCid)["fileId"]
        self.__createIndexForArticle(ii, prep, filename)
        ii.close()
        """

        # for all articles
        filenames = []
        for cid in multiFileMap.listCids():
            filenames.append(multiFileMap.get(cid)["fileId"])

        for filename in set(filenames):
            print("Processing file", filename)
            self.__createIndexForArticle(ii, filename)

        ii.close()


    def __createIndexForArticle(self, index, filename):
        cr = CommentReader(os.path.join("data", "raw", filename))
        cr.open()
        fileData = cr.readData()

        for cid in fileData["comments"]:
            tokenTuples = self.__prep.processText(fileData["comments"][cid]["comment_text"])

            tokenDict = {}
            for token, position in tokenTuples:
                positionList = tokenDict.get(token, [])
                positionList.append(position)
                positionList.sort()
                tokenDict[token] = positionList

            for token in tokenDict:
                index.insert(token, cid, tokenDict[token]) # and also positionList = tokenDict[token]

        cr.close()