import os
from cse.helper.MultiFileMap import MultiFileMap
from cse.CommentReader import CommentReader
from cse.CommentWriter import CommentWriter


multiFileIndexName = "multiFileIndex.index"
dataFileName = "comments.data"


def createCombinedFile(path):
    fileIndexPath = os.path.join(path, multiFileIndexName)

    # create index if it does not exist
    if not os.path.exists(fileIndexPath):
        print("multifile index does not exist...creating new one")
        from cse.helper.createIndex import createMultiFileIndex
        createMultiFileIndex(path)
    
    multiFileMap = MultiFileMap().loadJson(fileIndexPath)
    print("multifile index loaded")

    # load file ids
    fileIds = set()
    for cid in multiFileMap.listCids():
        fileIds.add(multiFileMap.get(cid)["fileId"])

    # copy comments from files into single data file
    writer = CommentWriter(os.path.join(path, dataFileName))
    writer.open()
    writer.printHeader()
    for fileId in fileIds:
        print("copying file", fileId)
        reader = CommentReader(os.path.join(path, "raw", fileId))
        reader.open()
        data = reader.readData()
        writer.printData(data)
        reader.close()

    writer.close()



if __name__ == "__main__":
    createCombinedFile("data")
