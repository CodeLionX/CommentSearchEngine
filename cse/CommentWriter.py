import csv
import os
from cse.AuthorMappingWriter import AuthorMappingWriter
from collections import OrderedDict

class CommentWriter(object):

    __delimiter = ''
    __filepath = ""
    __file = None
    __writer = None
    __nextAuthorId = 0
    __authorIdMapping = OrderedDict()


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath


    def open(self):
        if not os.path.exists(os.path.dirname(self.__filepath)):
            try:
                os.makedirs(os.path.dirname(self.__filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # w  = writing, will empty file and write from beginning (file is created)
        # a+ = read and append (file is created if it does not exist)
        self.__file = open(self.__filepath, 'w', newline='')   
        self.__writer = csv.writer(self.__file)
        return self


    def close(self):
        self.__file.close()
        mappingWrtier = AuthorMappingWriter(os.path.join(os.path.dirname(self.__filepath), 'authorMapping.csv'))
        mappingWrtier.open()
        mappingWrtier.printHeader()
        mappingWrtier.printData(self.__authorIdMapping)
        mappingWrtier.close()

        
        


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["cid", "article_id", "author_id", "text", "time", "parent", "upvotes", "downvotes", ])
        else:
            self.__writer.writerow(template)
        self.__file.flush()


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
            
            self.__writer.writerow([
                str(commentId),
                article_id,
                authorId,
                data["comments"][commentId]["comment_text"].replace("\n", "\\n"),
                data["comments"][commentId]["timestamp"],
                str(data["comments"][commentId]["parent_comment_id"]),
                data["comments"][commentId]["upvotes"],
                data["comments"][commentId]["downvotes"]
            ])
        self.__file.flush()


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()
