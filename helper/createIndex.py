import os
from cse.indexing import DocumentMap
from cse.CommentReader import CommentReader

"""
Helper file for creating an index over the multiple csv files
containing the comments of each article
"""

def createMultiFileIndex(path, name="multiFileIndex.index"):
    index = DocumentMap()
    directory = os.fsencode(os.path.join(path, "raw"))

    files = os.listdir(directory)

    for file in files:
        filename = os.fsdecode(file)
        print("processing file", filename)

        if '\0' in open(os.path.join(os.fsdecode(directory), filename)).read():
            print("   " + filename + "has null byte .. skipping")
            continue

        cr = CommentReader(os.path.join(os.fsdecode(directory), filename))
        cr.open()
        articleData = cr.readData()
        cr.close()
        for commentId in articleData["comments"]:
            index.insert(commentId, filename, articleData["article_id"], articleData["article_url"])

    index.saveJson(os.path.join(path, name))
    print("saved multifile index to", os.path.join(path, name))



if __name__ == '__main__':
    createMultiFileIndex("data")
