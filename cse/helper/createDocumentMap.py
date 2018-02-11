import os

from cse.indexing.DocumentMapBuilder import DocumentMapBuilder
from cse.reader import CommentReader

from cse.indexing.commons import (
    DOCUMENT_MAP_NAME,
    DOCUMENT_MAP_DICT_NAME
)

def indexDocMap(directory, commentsFilePath, articleFilePath, authorsFilePath):
    documentMapPath = os.path.join(directory, DOCUMENT_MAP_NAME)
    document_map_dict_path = os.path.join(directory, DOCUMENT_MAP_DICT_NAME)
    commentsFilePath = os.path.join(directory, commentsFilePath)
    articleFilePath = os.path.join(directory, articleFilePath)
    authorsFilePath = os.path.join(directory, authorsFilePath)

    # setup index writers
    documentMap = DocumentMapBuilder(documentMapPath, document_map_dict_path)

    # start indexing the comments file
    #print("Starting indexing...")
    with CommentReader(commentsFilePath, articleFilePath, authorsFilePath) as dataFile:
        lastPointer = None
        for data in dataFile:
            if lastPointer == None:
                lastPointer = dataFile.startSeekPointer()
            try:
                documentMap.get(data["commentId"])
            except KeyError:
                # update document map
                documentMap.insert(data["commentId"], lastPointer)

            lastPointer = dataFile.currentSeekPointer()

    print("Saving index...")
    documentMap.close()


if __name__ == '__main__':
    indexDocMap(".", "comments.csv", "articles.csv", "authors.csv")
