import os
import errno


class MainIndex(object):
    """
    Inverted Index (main - on disk)
    Structure: Offset, Size -> index entry

    Reads bytes from an index file. Uses the supplied `decodeFunc` to decode
    the read bytes into a specific object representing the index entry.

    `filename` is a `str` specifying the path to the index file
    `decodeFunc` receives bytes (`list[byte]`) and can return any `object`.
    """


    def __init__(self, filename, decodeFunc):
        self._indexFilename = filename
        self._decode = decodeFunc
        self._indexFile = None
        self._open()


    def _open(self):
        if not os.path.exists(os.path.dirname(self._indexFilename)):
            try:
                os.makedirs(os.path.dirname(self._indexFilename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        if not os.path.exists(self._indexFilename):
            print(self.__class__.__name__ + ":", "main index file not available...creating empty file")
            os.mknod(self._indexFilename)

        self._indexFile = open(self._indexFilename, 'rb')


    def close(self):
        self._indexFile.close()


    def retrieve(self, pointer, size):
        self._indexFile.seek(pointer)
        readBytes = self._indexFile.read(size)
        return self._decode(readBytes)


    def sizeOnDisk(self):
        return os.path.getsize(self._indexFilename)


    def __getitem__(self, key):
        value = self.retrieve(key[0], key[1])
        if value is None:
            raise KeyError
        return value

