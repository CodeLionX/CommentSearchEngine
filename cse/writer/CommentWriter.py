import csv
import os
from cse.writer.AuthorMappingWriter import AuthorMappingWriter
from collections import OrderedDict

class CommentWriter(object):

    DEFAULT_DELIMITER = ','


    def __init__(self, commentsFilepath, arcticlesFilepath, authorsFilepath, delimiter=DEFAULT_DELIMITER):
        self.__delimiter = delimiter
        self.__nextAuthorId = 0
        self.__authorIdMapping = OrderedDict()

        self.__commentsFilepath = commentsFilepath
        self.__commentsFile = None
        self.__commentsWriter = None

        self.__articlesFilepath = arcticlesFilepath
        self.__articlesFile = None
        self.__articlesWriter = None
        self.__currentArticle = None

        self.__authorsFilepath = authorsFilepath
        self.__authorsFile = None
        self.__authorsWriter = None
        self.__authors = None


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
        return self


    def close(self):
        self.__commentsFile.close()
        mappingWriter = AuthorMappingWriter(os.path.join(os.path.dirname(self.__commentsFilepath), 'authorMapping.csv'))
        mappingWriter.open()
        mappingWriter.printHeader()
        mappingWriter.printData(self.__authorIdMapping)
        mappingWriter.close()


    def printHeader(self, template=None):
        if template is None:
            self.__commentsWriter.writerow(["cid", "article_id", "author_id", "text", "time", "parent", "upvotes", "downvotes", ])
        else:
            self.__commentsWriter.writerow(template)
        self.__commentsFile.flush()


    def printData(self, data):
        article_id = data["article_id"]

        for commentId in data["comments"]:
            author = data["comments"][commentId]["comment_author"]
            if author in self.__authorIdMapping:
                authorId = self.__authorIdMapping[author]
            else:
                authorId = self.__nextAuthorId
                self.__authorIdMapping[author] = authorId
                self.__nextAuthorId = self.__nextAuthorId + 1
            
            self.__commentsWriter.writerow([
                str(commentId),
                article_id,
                authorId,
                data["comments"][commentId]["comment_text"].replace("\n", "\\n"),
                data["comments"][commentId]["timestamp"],
                str(data["comments"][commentId]["parent_comment_id"]),
                data["comments"][commentId]["upvotes"],
                data["comments"][commentId]["downvotes"]
            ])
        self.__commentsFile.flush()


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()
