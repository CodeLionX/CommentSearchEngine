import os
import csv

from cse.util import Util



class FileIndex(object):


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
