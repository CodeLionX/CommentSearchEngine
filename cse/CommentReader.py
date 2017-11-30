import csv
import os
import warnings

class CommentReader(object):

    __delimiter = ''
    __commentsFilepath = ""
    __commentsFile = None
    __commentReader = None
    
    __articlesFilepath = None
    __articlesFile = None
    __articlesReader = None
    __currentArticle = None

    __authorsFilepath = None
    __authorsFile = None
    __authorsReader = None
    __authors = None


    def __init__(self, commentsFilepath, arcticlesFilepath, authorsFilepath, delimiter=','):
        self.__delimiter = delimiter
        self.__commentsFilepath = commentsFilepath
        self.__articlesFilepath = arcticlesFilepath
        self.__authorsFilepath = authorsFilepath

    def open(self):
        if not os.path.exists(os.path.dirname(self.__commentsFilepath)):
            raise Exception("file not found!")

        self.__commentsFile = open(self.__commentsFilepath, 'r', newline='')
        self.__commentReader = csv.reader(self.__commentsFile, delimiter=self.__delimiter)

        self.__articlesFile = open(self.__articlesFilepath, 'r', newline='')
        self.__articlesReader = csv.reader(self.__articlesFile, delimiter=self.__delimiter)

        self.__authorsFile = open(self.__authorsFilepath, 'r', newline='')
        self.__authorsReader = csv.reader(self.__authorsFile, delimiter=self.__delimiter)

        return self


    def close(self):
        self.__commentsFile.close()
        self.__articlesFile.close()
        self.__authorsFile.close()


    def readAllData(self):
        raise DeprecationWarning("deprecated and not longer supported")
        if not self.__authors:
            self.__loadAuthors()
        return
        first = True

        articleUrl = ""
        articleId = ""
        comments = {}

        self.__commentsFile.seek(0)
        self.__articlesFile.seek(0)
        articlesFormat = next(self.__articlesReader)
        currentArticle = next(self.__articlesReader)
        for row in self.__commentReader:
            if first:
                first = False
                continue

            articleUrl = row[1]
            articleId = row[8]

            commentId = row[0]
            comments[commentId] = self.__parseRow(row)

        return {
            "article_url": articleUrl,
            "article_id": articleId,
            "comments": comments
        }

    
    def __loadAuthors(self):
        self.__authors = {}
        self.__authorsFile.seek(0)
        fileFormat = next(self.__authorsReader)

        for row in self.__authorsReader: # todo: don't load each author name. instead load seek offsets for each author id (less memory consumption). With delta encoding if necessary
            self.__authors[row[0]] = row[1]




    def __parseRow(self, row):
        raise DeprecationWarning("deprecated and not longer supported")
        if not self.__authors:
            self.__loadAuthors()
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


    def __parseIterRow(self, row):
        if not self.__authors:
            self.__loadAuthors()

        commentId = row[0]
        articleId = row[1]
        author = self.__authors[row[2]]
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = row[5]
        upvotes = int(row[6])
        downvotes = int(row[7])

        if not self.__currentArticle:
            self.__articlesFile.seek(0)
            articlesFormat = next(self.__articlesReader)
            self.__currentArticle = next(self.__articlesReader)

        while self.__currentArticle[0] is not articleId:
            self.__currentArticle = next(self.__articlesReader)
        articleUrl = self.__currentArticle[1]

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
        self.__commentsFile.seek(0)
        self.__commentReader.__iter__()
        # skip csv header in iteration mode:
        self.__commentReader.__next__()
        return self


    def __next__(self):
        return self.__parseIterRow(self.__commentReader.__next__())


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    with CommentReader("data/comments.data","data/articleIds.data", "data/authorMapping.data") as reader:
        for comment in reader:
            print(comment)
