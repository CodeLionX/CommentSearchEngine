import os
import csv
from cse.CommentReader import CommentReader
from cse.util import Util

"""
Helper file for creating an index over the multiple csv files
containing the comments of each article
"""
def scanRawDir(path):
    directory = os.fsencode(path)

    files = os.listdir(directory)
    fileIndex = []

    for file in files:
        filename = os.fsdecode(file)

        print("processing file " + filename)
        if '\0' in open(os.path.join(os.fsdecode(directory), filename)).read():
            print("   " + filename + "has null byte .. skipping")
            continue

        cr = CommentReader(os.path.join(os.fsdecode(directory), filename))
        cr.open()
        articleData = cr.readData()
        cr.close()
        for commentId in articleData["comments"]:
            fileIndex.append({
                "cid": commentId,
                "fileId": filename,
                "articleId": articleData["article_id"],
                "articleUrl": articleData["article_url"]
            })
    
    return fileIndex


def persistIndexCsv(filepath, data):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    print("persisting index in " + filepath)
    index = open(filepath, 'w', newline='')
    writer = csv.writer(index)

    # write header
    writer.writerow(["cid", "fileId", "articleId", "articleUrl"])

    # write index
    for record in data:
        writer.writerow([
            str(record["cid"]),
            str(record["fileId"]),
            str(record["articleId"]),
            record["articleUrl"]
        ])
    print("index persistet in file " + filepath)


def persistIndexJson(filepath, data):
    if not os.path.exists(os.path.dirname(filepath)):
        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    print("persisting index in " + filepath)
    with open(filepath, 'w', newline='') as file:
        file.write(Util.toJsonString(data))
    print("index persistet in file " + filepath)


def loadIndexJson(filepath):
    if not os.path.exists(os.path.dirname(filepath)):
            raise Exception("file not found!")
    
    index = None
    with open(filepath, 'r', newline='') as file:
        index = Util.fromJsonString(file.read())

    return index


#persistIndexCsv("data/index.csv", scanRawDir("data/raw"))
#persistIndexJson("data/index.json", scanRawDir("data/raw"))
persistIndexCsv("data/index.csv", loadIndexJson("data/index.json"))
