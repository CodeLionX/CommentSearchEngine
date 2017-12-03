import csv
import os

class AuthorMappingWriter(object):

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
        return self


    def close(self):
        self.__file.close()


    def printHeader(self, template=None):
        if template is None:
            self.__writer.writerow(["author_id", "author"])
        else:
            self.__writer.writerow(template)
        self.__file.flush()


    def printData(self, data):
        for author in data:
            self.__writer.writerow([
                str(data[author]),
                author,
            ])
        self.__file.flush()


    def __enter__(self):
        return self.open()


    def __exit__(self, type, value, traceback):
        self.close()


if __name__ == '__main__':
    writer = AuthorMappingWriter(os.path.join("data", 'AuthorMappingTest.csv'))
    writer.open()
    writer.printHeader()
    writer.printData({'authorName': 0})
    writer.close()