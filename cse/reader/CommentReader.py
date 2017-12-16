import csv
import os

from cse.reader.ArticleMappingReader import ArticleMappingReader
from cse.reader.AuthorMappingReader import AuthorMappingReader

class CommentReader(object):


    def __init__(self, commentsFilepath, arcticlesFilepath, authorsFilepath, delimiter=','):
        self.__delimiter = delimiter

        self.__commentsFile = None
        self.__commentReader = None

        self.__commentsFilepath = commentsFilepath
        self.__authorsReader = AuthorMappingReader(authorsFilepath)
        self.__articlesReader = ArticleMappingReader(arcticlesFilepath)


    def open(self):
        if not os.path.exists(os.path.dirname(self.__commentsFilepath)):
            raise Exception("comments file not found!")

        self.__commentsFile = open(self.__commentsFilepath, 'r', newline='', encoding="UTF-8")
        self.__commentReader = csv.reader(self.__commentsFile, delimiter=self.__delimiter)

        self.__articlesReader.open()

        return self


    def close(self):
        self.__commentsFile.close()
        self.__articlesReader.close()


    def __silentParseToInt(self, data, default):
        try:
            return int(data)
        except ValueError:
            return default


    def __parseIterRow(self, row):
        commentId = int(row[0])
        articleId = int(row[1])
        author = self.__authorsReader.lookupAuthorname(row[2])
        text = row[3].replace("\\n", "\n")
        timestamp = row[4]
        parentId = self.__silentParseToInt(row[5], None)
        upvotes = self.__silentParseToInt(row[6], 0)
        downvotes = self.__silentParseToInt(row[7], 0)

        # sequentially load article mapping
        # if there are some articles without comments we skip these articles
        while self.__articlesReader.currentArticleId() != articleId:
            try:
                next(self.__articlesReader)
            except StopIteration as e:
                # restart article iterator
                iter(self.__articlesReader)
                next(self.__articlesReader)
                print("!-- restarted article id mapping iterator --!")
                print("    searching article", articleId, author, commentId)

        articleUrl = self.__articlesReader.currentArticleUrl()

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

        # setup article iterator
        iter(self.__articlesReader)
        # load first article mapping
        next(self.__articlesReader)
        return self


    def __next__(self):
        return self.__parseIterRow(self.__commentReader.__next__())


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    with CommentReader("data/comments.csv", "data/articleIds.csv", "data/authorMapping.csv") as reader:
        for comment in reader:
            print(comment["commentId"])
