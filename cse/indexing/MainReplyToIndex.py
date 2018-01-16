import os
import errno
import msgpack


"""
MainReplyToIndex (main - on disk)
Structure: Offest, Size -> ReplyTo CID List
--> ReplyTo List: [cid1, cid2, cid3, ...]
"""
class MainReplyToIndex(object):

    __replyToLists = None
    __replyToListsFilename = ""


    def __init__(self, filename):
        self.__replyToListsFilename = filename
        self.__open()


    def __open(self):
        if not os.path.exists(os.path.dirname(self.__replyToListsFilename)):
            try:
                os.makedirs(os.path.dirname(self.__replyToListsFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self.__replyToListsFilename):
            print(self.__class__.__name__ + ":", "postinglist file not available...creating file")
            os.mknod(self.__replyToListsFilename)
        #self.__replyToLists = open(self.__replyToListsFilename, 'r', newline='', encoding="utf-8")
        self.__replyToLists = open(self.__replyToListsFilename, 'rb')


    def close(self):
        self.__replyToLists.close()


    def retrieve(self, pointer, size):
        self.__replyToLists.seek(pointer)
        readBytes = self.__replyToLists.read(size)
        return msgpack.unpackb(readBytes)


    def sizeOnDisk(self):
        return os.path.getsize(self.__replyToListsFilename)


    def __getitem__(self, key):
        value = self.retrieve(key[0], key[1])
        if value is None:
            raise KeyError
        return value
