import os
import csv
import pandas as pd
from pandas.io import pickle
from cse.util import Util


class InvertedIndex(object):

    """
    Dictionary (in memory)
    Structure: Term -> Postinglist Line Number
    """
    __dictionary = None
    """
    Inverted Index (on disk)
    Structure: Line Number in File -> Posting List
    """
    __postingList = None
    __postingListFilename = ""
    __indexFilename = ""


    def __init__(self, filepath):
        self.__indexFilename = os.path.join(filepath, "dictionary.index")
        self.__postingListFilename = os.path.join(filepath, "pl.index")


    def open(self):
        if not os.path.exists(os.path.dirname(self.__indexFilename)) or not os.path.exists(os.path.dirname(self.__postingListFilename)):
            try:
                os.makedirs(os.path.dirname(self.__indexFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__indexFilename):
            print("dictionary file not available...creating new dictionary")
            self.__dictionary = dict()
        else:
            with open(self.__indexFilename, 'r', newline='', encoding="utf-8") as file:
                self.__dictionary = Util.fromJsonString(file.read())

        if not os.path.exists(self.__postingListFilename):
            print("postinglist file not available...creating file")
            os.mknod(self.__postingListFilename)
        self.__postingList = open(self.__postingListFilename, 'r+', newline='', encoding="utf-8")


    def save(self):
        if not os.path.exists(os.path.dirname(self.__indexFilename)):
            try:
                os.makedirs(os.path.dirname(self.__indexFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise


        with open(self.__indexFilename, 'w', newline='', encoding="utf-8") as file:
            file.write(Util.toJsonString(self.__dictionary))


    def close(self):
        self.save()
        self.__postingList.close()


    def insert(self, term, documentId):
        if term in self.__dictionary:
            pointer = self.__dictionary[term]
            self.__addToPl(pointer, documentId)
        else:
            pointer = self.__insertPl([documentId])
            self.__dictionary[term] = pointer


    def get(self, term):
        try:
            return self.__lookupPl(self.__dictionary[term])
        except KeyError:
            return None


    def terms(self):
        return [term for term in self.__dictionary]


    def __lookupPl(self, line):
        self.__postingList.seek(0)
        for i, pl in enumerate(self.__postingList):
            if i == line:
                return list(pl.split(","))


    def __addToPl(self, line, cid):
        """
        self.__postingList.seek(0)
        for i, pl in enumerate(self.__postingList):
            if i == line:
                # unsorted!!
                self.__postingList.write(",".join([pl, cid])) # i guess this will overwrite existing postinglist in the following line
        """
        
        from tempfile import mkstemp
        from shutil import move
        from os import remove

        self.__postingList.close()
        sh, targetPath = mkstemp()
        with open(targetPath, 'w') as target_file:
            with open(self.__postingListFilename, 'r') as source_file:
                for i, pl in enumerate(source_file):
                    if i == line:
                        target_file.write(",".join([pl, cid]) + "\n")
                    else:
                        target_file.write(pl)
        remove(self.__postingListFilename)
        move(targetPath, self.__postingListFilename)
        self.__postingList = open(self.__postingListFilename, 'r+', newline='', encoding="utf-8")


    def __insertPl(self, cidList):
        self.__postingList.seek(0)
        line = 0
        for i, pl in enumerate(self.__postingList):
            line = i
        self.__postingList.write(",".join(cidList) + "\n")
        return line + 1



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
