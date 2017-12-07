import csv
import os
import errno
from collections import OrderedDict



class CommentIdMappingWriter(object):


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath
        self.__file = None
        self.__writer = None

        self.__commentIdMap = OrderedDict()
        self.__nextCommentId = 0
        self.__currentArticle = None


    def open(self):
        if not os.path.exists(os.path.dirname(self.__filepath)):
            try:
                os.makedirs(os.path.dirname(self.__filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # w  = writing, will empty file and write from beginning (file is created)
        # a+ = read and append (file is created if it does not exist)
        self.__file = open(self.__filepath, 'w', newline='', encoding="UTF-8")
        self.__writer = csv.writer(self.__file)
        return self


    def close(self):
        self.flushDataForArticle()
        self.__file.close()


    def mapToId(self, origCommentId, parent=False):
        if not origCommentId:
            return None

        if parent and origCommentId not in self.__commentIdMap:
            print("No Parent ID Mapping found for: " + origCommentId)
            raise KeyError("No Parent ID Mapping found for: " + origCommentId)

        if origCommentId not in self.__commentIdMap:
            self.__commentIdMap[origCommentId] = self.__nextCommentId
            self.__nextCommentId = self. __nextCommentId + 1

        return self.__commentIdMap[origCommentId]


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["cid", "orig_comment_id"])
        else:
            self.__writer.writerow(template)


    def flushDataForArticle(self):
        if not self.__writer:
            self.open()

        for commentId in self.__commentIdMap:
            self.__writer.writerow([
                self.__commentIdMap[commentId],
                commentId
            ])
        self.__file.flush()
        self.__commentIdMap = OrderedDict()


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    writer = CommentIdMappingWriter(os.path.join("data", 'CommentIdMappingTest.csv'))
    writer.open()
    writer.printHeader()
    writer.mapToId("origid1")
    writer.mapToId("origid2")
    writer.mapToId(None)
    writer.mapToId("origid1")
    writer.mapToId("origid4")
    writer.mapToId("")
    writer.mapToId("origid4")
    writer.mapToId("origid4")
    writer.mapToId("origid3")
    writer.close()
