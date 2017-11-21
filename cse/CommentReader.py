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
        return self


    def close(self):
        self.__file.close()


    def readAllData(self):
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
                articleId = row[7]
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
        votes = int(row[6])

        return {
            "comment_author": author,
            "comment_text" : text,
            "timestamp" : timestamp,
            "parent_comment_id" : parentId,
            "votes" : votes
        }


    def __parseIterRow(self, row):
        articleUrl = row[1]
        author = row[2]
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = row[5]
        votes = int(row[6])
        articleId = row[7]

        return {
            "article_url": articleUrl,
            "article_id": articleId,
            "comment_author": author,
            "comment_text" : text,
            "timestamp" : timestamp,
            "parent_comment_id" : parentId,
            "votes" : votes
        }


    def __iter__(self):
        self.__reader.__iter__()
        self.__reader.__next__()
        return self


    def __next__(self):
        return self.__parseIterRow(self.__reader.__next__())


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    with CommentReader("data/comments.csv") as reader:
        for e in reader:
            print(e)
