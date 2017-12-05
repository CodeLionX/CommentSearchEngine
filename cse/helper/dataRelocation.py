import csv
import os

from cse.CommentWriter import CommentWriter
from cse.pipeline import HtmlStopwordsHandler

class OldCommentReader(object):
    """
    OldCommentReader for older version of the comment data files.

    Specify a version to support different kinds of data files.

    Version = 1: <currently not supported> data is divided into
                 multiply files, which all contain comments from
                 a single article

    Version = 2: comment data file does not contain separated fields
                 for upvotes and downvotes, just a single votes-field

    Version = 3: comment data file has separated upvotes and downvotes
                 but could contain html tags in comment texts
    """
    V1 = 1
    V2 = 2
    V3 = 3

    __delimiter = ''
    __filepath = ""
    __file = None
    __reader = None


    def __init__(self, version, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath
        self.__version = version

        if self.__version == self.V1:
            raise ValueError("V1 not supported")


    def __parseIterRow(self, row):
        commentId = row[0]
        articleUrl = row[1]
        author = row[2]
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = row[5]

        if self.__version == self.V1:
            raise ValueError("V1 not supported")
        if self.__version == self.V2:
            upvotes = int(row[6])
            downvotes = 0
            articleId = row[7]
        elif self.__version == self.V3:
            upvotes = int(row[6])
            downvotes = int(row[7])
            articleId = row[8]

        return {
            "commentId": commentId,
            "article_url": articleUrl,
            "article_id": articleId,
            "comment_author": author,
            "comment_text" : text,
            "timestamp" : timestamp,
            "parent_comment_id" : parentId,
            "upvotes" : upvotes,
            "downvotes": downvotes
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
    with OldCommentReader(OldCommentReader.V2, oldfile) as oldReader:
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
    with OldCommentReader(OldCommentReader.V3, oldfile) as reader:
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
    oldfile = os.path.join("data", "comments.data")
    newFile = os.path.join("data", "comments_without_html.data")
    removeHtmlTags(oldfile, newFile)
