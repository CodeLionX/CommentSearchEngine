import csv
import os
from collections import OrderedDict



class AuthorMappingWriter(object):


    def __init__(self, filepath, delimiter=','):
        self.__delimiter = delimiter
        self.__filepath = filepath
        self.__file = None
        self.__writer = None

        self.__nextAuthorId = 0
        self.__authorIdMapping = OrderedDict()


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
        self.__printData()
        self.__file.close()


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["author_id", "author"])
        else:
            self.__writer.writerow(template)


    def mapToId(self, author):
        if author in self.__authorIdMapping:
            authorId = self.__authorIdMapping[author]
        else:
            authorId = self.__nextAuthorId
            self.__authorIdMapping[author] = authorId
            self.__nextAuthorId += 1
        return authorId


    def __printData(self):
        for author in self.__authorIdMapping:
            self.__writer.writerow([
                self.__authorIdMapping[author],
                author,
            ])


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()


if __name__ == '__main__':
    writer = AuthorMappingWriter(os.path.join("data", 'AuthorMappingTest.csv'))
    writer.open()
    writer.printHeader()
    writer.mapToId("Ulli")
    writer.mapToId("Hans")
    writer.mapToId("Moritz")
    writer.mapToId("Hans")
    writer.close()
