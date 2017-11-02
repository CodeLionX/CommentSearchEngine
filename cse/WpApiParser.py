from pprint import pprint
from cse.util import Util

class WpApiParser:

    __url = ""
    __assetId = ""
    __data = {}
    __consumer = None

    DEFAULT_CONSUMER = lambda (row) => {print(str(row), "\n")}

    def __init__(self, url, assetId):
        self.__url = url
        self.__assetId = assetId
        data = {
            "article_url" : url,
            "article_id" : assetId,
            "comments" : []
        }
        self.__consumer = self.DEFAULT_CONSUMER


    def setConsumer(self, consumer):
        self.__consumer = consumer


    def removeConsumer(self):
        self.__consumer = self.DEFAULT_CONSUMER

    def parseAndAdd(self, comments):
        pass

    def parseAndAdd(self, comments, parentId):
        pass

    def __iterateComments(self, comments, parentId=None):
        commentList = {}
        for comment in comments:
            votes = 0
            if(not 'action_summaries' in comment):
                print(comment)
            else:
                for action_summary in comment["action_summaries"]:
                    if action_summary["__typename"] == "LikeActionSummary":
                        votes = action_summary["count"]

                commentList[comment["id"]] = {
                    "comment_author": comment["user"]["username"],
                    "comment_text" : comment["body"],
                    "timestamp" : comment["created_at"],
                    "parent_comment_id" : parentId,
                    "votes" : votes
                }

            try:
                commentReplies = self.iterateComments(comment["replies"]["nodes"], comment["id"])
            except KeyError: # There may be a limit of the nesting level of comments on wp
                commentReplies = {}
            commentList.update(commentReplies)
        return commentList
