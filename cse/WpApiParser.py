from pprint import pprint
from cse.util import Util

class WpApiParser:

    __url = ""
    __assetId = ""
    __consumer = None

    DEFAULT_CONSUMER = lambda data: print(str(data), "\n")

    def __init__(self, url, assetId):
        self.__url = url
        self.__assetId = assetId
        self.__consumer = self.DEFAULT_CONSUMER


    def setConsumer(self, consumer):
        self.__consumer = consumer


    def removeConsumer(self):
        self.__consumer = self.DEFAULT_CONSUMER

    def parseAndAdd(self, comments):
        pass

    def parseAndAdd(self, comments, parentId):
        pass

    def __buildDataSkeleton(self):
        return {
            "article_url" : self.__url,
            "article_id" : self.__assetId,
            "comments" : []
        }

    
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
                commentReplies = self.__iterateComments(comment["replies"]["nodes"], comment["id"])
            except KeyError: # There may be a limit of the nesting level of comments on wp
                commentReplies = {}
            commentList.update(commentReplies)
        return commentList
