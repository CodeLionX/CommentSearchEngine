import csv
import os
import errno

from cse.writer.AuthorMappingWriter import AuthorMappingWriter
from cse.writer.ArticleMappingWriter import ArticleMappingWriter



class CommentWriter(object):

    DEFAULT_DELIMITER = ','


    def __init__(self, commentsFilepath, articlesFilepath, authorsFilepath, delimiter=DEFAULT_DELIMITER):
        self.__delimiter = delimiter

        self.__commentsFilepath = commentsFilepath
        self.__commentsFile = None
        self.__commentsWriter = None

        self.__articlesWriter = ArticleMappingWriter(articlesFilepath)
        self.__authorsWriter = AuthorMappingWriter(authorsFilepath)


    def open(self):
        if not os.path.exists(os.path.dirname(self.__commentsFilepath)):
            try:
                os.makedirs(os.path.dirname(self.__commentsFilepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # w  = writing, will empty file and write from beginning (file is created)
        # a+ = read and append (file is created if it does not exist)
        self.__commentsFile = open(self.__commentsFilepath, 'w', newline='')   
        self.__commentsWriter = csv.writer(self.__commentsFile)

        self.__articlesWriter.open()
        self.__authorsWriter.open()
        return self


    def close(self):
        self.__commentsFile.close()
        self.__articlesWriter.close()
        self.__authorsWriter.close()


    def printHeader(self, template=None):
        if template is None:
            self.__commentsWriter.writerow(["cid", "article_id", "author_id", "text", "time", "parent", "upvotes", "downvotes"])
        else:
            self.__commentsWriter.writerow(template)
        
        self.__articlesWriter.printHeader()
        self.__authorsWriter.printHeader()


    def printData(self, data):
        article_url = data["article_url"]
        origArticle_id = data["article_id"]
        article_id = self.__articlesWriter.mapToId(origArticle_id, article_url)

        for commentId in data["comments"]:
            author = data["comments"][commentId]["comment_author"]
            authorId = self.__authorsWriter.mapToId(author)
            
            self.__commentsWriter.writerow([
                commentId,
                article_id,
                authorId,
                data["comments"][commentId]["comment_text"].replace("\n", "\\n"),
                data["comments"][commentId]["timestamp"],
                data["comments"][commentId]["parent_comment_id"],
                data["comments"][commentId]["upvotes"],
                data["comments"][commentId]["downvotes"]
            ])
        self.__commentsFile.flush()


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    writer = CommentWriter("data/commentTest.csv", "data/articleTest.csv", "data/authorTest.csv")
    writer.open()
    writer.printHeader()
    for i in range(4):
        writer.printData({
            "article_url": "url" + str(i),
            "article_id" : "originalId" + str(i),
            "comments" : {
                "comment_id1"+str(i) : {
                    "comment_author": "User1",
                    "comment_text" : "The comment itself",
                    "timestamp" : "The creation date",
                    "parent_comment_id" : None,
                    "upvotes" : 2,
                    "downvotes": 1
                },
                "comment_id2"+str(i) : {
                    "comment_author": "User2",
                    "comment_text" : "The comment itself",
                    "timestamp" : "The creation date",
                    "parent_comment_id" : None,
                    "upvotes" : 0,
                    "downvotes": 0
                },
                "comment_id3"+str(i) : {
                    "comment_author": "User1",
                    "comment_text" : "The comment itself",
                    "timestamp" : "The creation date",
                    "parent_comment_id" : "comment_id2"+str(i),
                    "upvotes" : 2,
                    "downvotes": 1
                },
                "comment_id4"+str(i) : {
                    "comment_author": "User3"+str(i),
                    "comment_text" : "The comment itself",
                    "timestamp" : "The creation date",
                    "parent_comment_id" : "comment_id2"+str(i),
                    "upvotes" : 2,
                    "downvotes": 1
                }
            }
        })
    writer.close()
