import json

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