from cse.util import Util
from cse.pipeline import Handler

class WpApiParser(Handler):

    def __init__(self):
        super()


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
                "upvotes" : votes,
                "downvotes": 0
            }

            try:
                commentReplies = self.__iterateComments(comment["replies"]["nodes"], comment["id"])
            except KeyError: # There may be a limit of the nesting level of comments on wp
                commentReplies = {}
            commentList.update(commentReplies)
        return commentList


    # inherited from cse.pipeline.Handler
    def registeredAt(self, ctx):
        pass


    def process(self, ctx, data):
        result = self.parse(
            comments=data["comments"],
            url=data["url"],
            assetId=data["assetId"],
            parentId=data["parentId"]
        )
        ctx.write(result)