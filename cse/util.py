import json
import msgpack

class Util(object):

    def __init__(self):
        pass
    
    @staticmethod
    def toJsonString(d):
        return json.dumps(d,
            ensure_ascii=False,
            sort_keys=True,
            separators=(', ', ': '),
            indent=None # prettyprinting: indent=2
        )

    @staticmethod
    def fromJsonString(s):
        return json.loads(s,
            encoding='UTF-8'
        )

    @staticmethod
    def sha256(s):
        import hashlib

        m = hashlib.sha256()
        m.update(s.encode('utf-8'))
        return m.hexdigest()



class PackerUtil(object):

    MSGPACK = 'msgpack'
    JSON = 'json'
    PICKLE = 'pickle'

    @staticmethod
    def packToFile(data, filename, type=MSGPACK):
        switcher = {
            PackerUtil.MSGPACK: PackerUtil._packMsgpack,
            PackerUtil.JSON: PackerUtil._packJson,
            PackerUtil.PICKLE: PackerUtil._packPickle
        }

        func = switcher.get(type, PackerUtil._packMsgpack)
        return func(data, filename)

    @staticmethod
    def unpackFromFile(filename, type=MSGPACK):
        switcher = {
            PackerUtil.MSGPACK: PackerUtil._unpackMsgpack,
            PackerUtil.JSON: PackerUtil._unpackJson,
            PackerUtil.PICKLE: PackerUtil._unpackPickle
        }

        func = switcher.get(type, PackerUtil._unpackMsgpack)
        return func(filename)

    @staticmethod
    def _packJson(data, filename):
        with open(filename, 'wt') as file:
            file.write(json.dumps(data,
                ensure_ascii=False,
                sort_keys=True,
                separators=(', ', ': '),
                indent=None # prettyprinting: indent=2
            ))

    @staticmethod
    def _packMsgpack(data, filename):
        with open(filename, 'wb') as file:
            msgpack.pack(data, file, use_bin_type=True)

    @staticmethod
    def _packPickle(data, filename):
        pass

    @staticmethod
    def _unpackJson(filename):
        with open(filename, 'rt') as file:
            return json.loads(file.read(), encoding='UTF-8')

    @staticmethod
    def _unpackMsgpack(filename):
        with open(filename, 'rb') as file:
            return msgpack.unpack(file, encoding="UTF-8")

    @staticmethod
    def _unpackPickle(filename):
        pass
