from pprint import pprint
from cse.util import Util

class WpApiParser:

    def __init__(self):
        pass


    def parse(self, comments, url, assetId, parentId):
        data = self.__buildDataSkeleton(url, assetId)
        data["comments"] = self.__iterateComments(comments, parentId)
        return data


    def __buildDataSkeleton(self, url, assetId):
        return {
            "article_url" : url,
            "article_id" : assetId,
            "comments" : []
        }


    def __iterateComments(self, comments, parentId=None):
        commentList = {}
        for comment in comments:
            votes = 0
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
