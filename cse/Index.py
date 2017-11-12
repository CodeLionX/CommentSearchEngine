import os
import csv
from cse.util import Util


class InvertedIndex(object):

    __index = dict()
    __indexFile = ""


    def __init__(self, filepath):
        self.__indexFile = filepath


    def load(self):
        if not os.path.exists(os.path.dirname(self.__indexFile)):
            raise Exception("file not found!")
    
        with open(self.__indexFile, 'r', newline='') as file:
            self.__index = Util.fromJsonString(file.read())
        

    def save(self):
        if not os.path.exists(os.path.dirname(self.__indexFile)):
            try:
                os.makedirs(os.path.dirname(self.__indexFile))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(self.__indexFile, 'w', newline='') as file:
            file.write(Util.toJsonString(self.__index))


    def insert(self, term, documentId):
        pl = self.get(term)
        if not pl:
            pl = [documentId]
        else:
            pl.append(documentId)
        pl.sort()
        self.__index[term] = pl


    def get(self, term):
        try:
            return self.__index[term]
        except KeyError as ex:
            return None


    def terms(self):
        return [term for term in self.__index]



class Index(object):

    __index = dict()


    def __init__(self):
        pass


    def saveCsv(self, filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        index = open(filepath, 'w', newline='')
        writer = csv.writer(index)

        # write header
        writer.writerow(["cid", "fileId", "articleId", "articleUrl"])

        # write index
        for record in self.__index:
            writer.writerow([
                str(record["cid"]),
                str(record["fileId"]),
                str(record["articleId"]),
                record["articleUrl"]
            ])


    def saveJson(self, filepath):
        if not os.path.exists(os.path.dirname(filepath)):
            try:
                os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filepath, 'w', newline='') as file:
            file.write(Util.toJsonString(self.__index))


    def loadJson(self, filepath):
        if not os.path.exists(os.path.dirname(filepath)):
                raise Exception("file not found:" + filepath)
        
        with open(filepath, 'r', newline='') as file:
            self.__index = Util.fromJsonString(file.read())


    def insert(self, cid, data):
        self.__index[cid] = data


    def get(self, cid):
        try:
            return self.__index[cid]
        except KeyError as ex:
            print("key " + cid + " not found in Index: " + ex)
            return None


    def listCids(self):
        return [cid for cid in self.__index]



"""
class Dictionary(object):

    __dict = dict()

    def __init__(self):
        pass

    @staticmethod
    def termDescriptorEncode(term, postinglistPointer):
        return {
            "term": term,
            "postinglistPointer": postinglistPointer
        }

    @staticmethod
    def termDescriptorDecode(termDescriptor):
        return (termDescriptor["term"], termDescriptor["postinglistPointer"])

    def load(self):
        pass

    def save(self):
        pass

"""  
