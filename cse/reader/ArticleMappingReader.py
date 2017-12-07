import csv
import os

class ArticleMappingReader(object):


    def __init__(self, arcticlesFilepath, delimiter=','):
        self.__delimiter = delimiter

        self.__articlesFilepath = arcticlesFilepath
        self.__articlesFile = None
        self.__articlesReader = None
        self.__currentArticleData = None


    def open(self):
        if not os.path.exists(os.path.dirname(self.__articlesFilepath)):
            raise Exception("article mapping file not found!")

        self.__articlesFile = open(self.__articlesFilepath, 'r', newline='', encoding="UTF-8")
        self.__articlesReader = csv.reader(self.__articlesFile, delimiter=self.__delimiter)
        return self


    def close(self):
        self.__articlesFile.close()


    def currentArticleId(self):
        return self.__currentArticleData[0]


    def currentArticleUrl(self):
        return self.__currentArticleData[1]


    def __parseIterRow(self, row):
        articleId = int(row[0])
        articleUrl = row[1]
        return (articleId, articleUrl)


    def __iter__(self):
        del self.__currentArticleData
        self.__articlesFile.seek(0)
        self.__articlesReader.__iter__()
        # skip csv header in iteration mode:
        self.__articlesReader.__next__()
        return self


    def __next__(self):
        self.__currentArticleData = self.__parseIterRow(self.__articlesReader.__next__())
        return self.__currentArticleData


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()



if __name__ == "__main__":
    with ArticleMappingReader(os.path.join("data", "articleIds.csv")) as reader:
        for aid, url in reader:
            print(aid, url)
