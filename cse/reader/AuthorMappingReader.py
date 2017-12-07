import csv
import os
import warnings

class AuthorMappingReader(object):


    def __init__(self, authorsFilepath, delimiter=','):
        self.__delimiter = delimiter
        self.__authorsFilepath = authorsFilepath
        self.__authors = {}
        self.__loadAuthorMapping()


    def __loadAuthorMapping(self):
        with open(self.__authorsFilepath, 'r', newline='', encoding="UTF-8") as authorsFile:
            reader = csv.reader(authorsFile, delimiter=self.__delimiter)
            next(reader) # skip header row
            for row in reader:
                self.__authors[row[0]] = row[1]


    def lookupAuthorname(self, id):
        return self.__authors.get(id, "")


    def __iter__(self):
        return iter(self.__authors)



if __name__ == "__main__":
    r = AuthorMappingReader(os.path.join("data", "authorMapping.csv"))
    for aid in r:
        print(aid, r.lookupAuthorname(aid))
