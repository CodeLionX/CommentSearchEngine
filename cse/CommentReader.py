import csv
import os


class CommentReader(object):

    __delimiter = ''
    __filepath = ""
    __file = None
    __reader = None


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath


    def open(self):
        if not os.path.exists(os.path.dirname(self.__filepath)):
            raise Exception("file not found!")

        self.__file = open(self.__filepath, 'r', newline='')
        self.__reader = csv.reader(self.__file, delimiter=self.__delimiter)


    def close(self):
        self.__file.close()


    def readData(self):
        first = True
        second = True

        articleUrl = ""
        articleId = ""
        comments = {}

        for row in self.__reader:
            if first:
                first = False
                continue

            if second:
                articleUrl = row[1]
                articleId = row[8]
                second = False

            commentId = row[0]
            comments[commentId] = self.__parseRow(row)

        return {
            "article_url": articleUrl,
            "article_id": articleId,
            "comments": comments
        }


    def __parseRow(self, row):
        author = row[2]
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = row[5]
        upvotes = int(row[6])
        downvotes = int(row[7])

        return {
            "comment_author": author,
            "comment_text" : text,
            "timestamp" : timestamp,
            "parent_comment_id" : parentId,
            "upvotes" : upvotes,
            "downvotes": downvotes
        }