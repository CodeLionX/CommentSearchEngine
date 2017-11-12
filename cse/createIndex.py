import os
from cse.Index import (Index, InvertedIndex)
from cse.CommentReader import CommentReader

"""
Helper file for creating an index over the multiple csv files
containing the comments of each article
"""

def scanRawDir(path, index):
    directory = os.fsencode(path)

    files = os.listdir(directory)

    for file in files:
        filename = os.fsdecode(file)

        if '\0' in open(os.path.join(os.fsdecode(directory), filename)).read():
            print("   " + filename + "has null byte .. skipping")
            continue

        cr = CommentReader(os.path.join(os.fsdecode(directory), filename))
        cr.open()
        articleData = cr.readData()
        cr.close()
        for commentId in articleData["comments"]:
            index.insert(commentId, {
                "cid": commentId,
                "fileId": filename,
                "articleId": articleData["article_id"],
                "articleUrl": articleData["article_url"]
            })

#persistIndexCsv("data/index.csv", scanRawDir("data/raw"))
#persistIndexJson("data/index.json", scanRawDir("data/raw"))
#i = Index()
#scanRawDir("data/raw", i)
#i.saveJson("data/index.json")

i = InvertedIndex("data/invertedIndex.json")
i.load()
print("terms:", len(i.terms()))