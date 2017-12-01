import csv
import os
from cse.pipeline.Handler import Handler

class CommentIdWriter(Handler):

    __delimiter = ''
    __filepath = ""
    __file = None
    __writer = None

    __commentIdMap = {}
    __nextCommentId = 0
    __currentArticle = None


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
        self.printHeader()
        return self


    def close(self):
        self.printData()
        self.__file.close()

        
    def process(self, ctx, data):
        if self.__currentArticle is not data["article_id"]:
            self.printData()
            self.__currentArticle = data["article_id"]

        tempCommentData = {}
        for commentId in data["comments"]:
            if commentId not in self.__commentIdMap:
                self.__commentIdMap[commentId] = self.__nextCommentId
                self.__nextCommentId = self. __nextCommentId + 1
            if data["comments"][commentId]["parent_comment_id"] and data["comments"][commentId]["parent_comment_id"] not in self.__commentIdMap:
                self.__commentIdMap[ data["comments"][commentId]["parent_comment_id"] ] = self.__nextCommentId
                self.__nextCommentId = self. __nextCommentId + 1
            
            newCommentId = self.__commentIdMap[commentId]
            tempCommentData[newCommentId] = data["comments"][commentId]

            try:
                newParentId = self.__commentIdMap[ data["comments"][commentId]["parent_comment_id"] ]
                tempCommentData[newCommentId]["parent_comment_id"] = newParentId
            except KeyError:
                pass

        data["comments"] = tempCommentData

        ctx.write(data)


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["ccid", "cid"])
        else:
            self.__writer.writerow(template)
        self.__file.flush()


    def printData(self):
        if not self.__writer:
            self.open()

        for commentId in self.__commentIdMap:
                       
            self.__writer.writerow([
                str(self.__commentIdMap[commentId]),
                commentId
            ])
        self.__file.flush()
        self.__commentIdMap = {}



    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()
