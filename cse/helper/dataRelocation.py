import csv
import os

from cse.CommentWriter import CommentWriter
from cse.CommentReader import CommentReader
from cse.pipeline import HtmlStopwordsHandler

class OldCommentReader(object):

    __delimiter = ''
    __filepath = ""
    __file = None
    __reader = None


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath


    def __parseIterRow(self, row):
        commentId = row[0]
        articleUrl = row[1]
        author = row[2]
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = row[5]
        upvotes = int(row[6])
        articleId = row[7]

        return {
            "commentId": commentId,
            "article_url": articleUrl,
            "article_id": articleId,
            "comment_author": author,
            "comment_text" : text,
            "timestamp" : timestamp,
            "parent_comment_id" : parentId,
            "upvotes" : upvotes,
            "downvotes": 0
        }


    def __iter__(self):
        self.__file.seek(0)
        self.__reader.__iter__()
        # skip csv header in iteration mode:
        self.__reader.__next__()
        return self


    def __next__(self):
        return self.__parseIterRow(self.__reader.__next__())


    def __enter__(self):
        if not os.path.exists(os.path.dirname(self.__filepath)):
            raise Exception("file not found!")

        self.__file = open(self.__filepath, 'r', newline='')
        self.__reader = csv.reader(self.__file, delimiter=self.__delimiter)
        return self


    def __exit__(self, type, value, traceback):
        self.__file.close()


class CtxHelper(object):
    
    def __init__(self, writer):
        self.__writer = writer
    
    def write(self, data):
        self.__writer.printData(data)


def fromVotesToUpAndDownvotes(oldFile, newFile):
    with OldCommentReader(oldfile) as oldReader:
        with CommentWriter(newFile) as writer:
            writer.printHeader()
            for row in oldReader:
                data = {}
                data["article_url"] = row["article_url"]
                data["article_id"] = row["article_id"]
                data["comments"] = {}
                data["comments"][row["commentId"]] = {
                    "comment_author": row["comment_author"],
                    "comment_text" : row["comment_text"].replace("\\n", "\n"),
                    "timestamp" : row["timestamp"],
                    "parent_comment_id" : row["parent_comment_id"],
                    "upvotes" : row["upvotes"],
                    "downvotes": row["downvotes"]
                }
                writer.printData(data)


def removeHtmlTags(oldFile, newFile):
    with CommentReader(oldfile) as reader:
        with CommentWriter(newFile) as writer:
            writer.printHeader()
            handler = HtmlStopwordsHandler()
            ctx = CtxHelper(writer)
            for row in reader:
                data = {
                    "article_url": row["article_url"],
                    "article_id": row["article_id"],
                    "comments": {}
                }
                data["comments"][row["commentId"]] = row
                handler.process(ctx, data)


if __name__ == "__main__":
    oldfile = os.path.join("data", "comments_with_downvotes.data")
    newFile = os.path.join("data", "comments_without_html.data")
    removeHtmlTags(oldfile, newFile)
