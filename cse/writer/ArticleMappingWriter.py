import csv
import os
import errno



class ArticleMappingWriter(object):


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath
        self.__file = None
        self.__writer = None
        self.__currentId = -1
        self.__currentOrigId = ""


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
        self.__file.close()


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["article_id", "arcticle_url"])
        else:
            self.__writer.writerow(template)


    def mapToId(self, origArticleId, articleUrl):
        if self.__currentOrigId == origArticleId:
            return self.__currentId

        self.__currentId += 1
        self.__currentOrigId = origArticleId
        self.__writer.writerow([self.__currentId, articleUrl])
        return self.__currentId


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == '__main__':
    writer = ArticleMappingWriter(os.path.join("data", "arcticleIdsTest.csv"))
    writer.open()
    writer.printHeader()
    writer.mapToId("abc", "url1")
    writer.mapToId("abc", "url1")
    writer.mapToId("bcd", "url2")
    writer.mapToId("cde", "url3")
    writer.close()
