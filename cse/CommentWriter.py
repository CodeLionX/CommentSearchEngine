import csv
import os

class CommentWriter(object):

    __delimiter = ''
    __filepath = ""
    __file = None
    __writer = None

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

    def close(self):
        self.__file.close()


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["cid", "url", "author", "text", "time", "parent", "votes", "article_id"])
        else:
            self.__writer.writerow(template)
        self.__file.flush()


    def printData(self, data):
        article_url = data["article_url"]
        article_id = data["article_id"]

        for commentId in data["comments"]:
            self.__writer.writerow([
                str(commentId),
                article_url,
                data["comments"][commentId]["comment_author"],
                data["comments"][commentId]["comment_text"].replace("\n", "\\n"),
                data["comments"][commentId]["timestamp"],
                str(data["comments"][commentId]["parent_comment_id"]),
                data["comments"][commentId]["votes"],
                article_id
            ])
        self.__file.flush()
