import json
from pprint import pprint

class WpApiParser:

    def parseSpiderData(self, url, assetId, comments): #ToDo Input should be the raw api output
        commentList = self.iterateComments(comments)
        data = {
            "article_url" : url,
            "article_id" : assetId,
            "comments" : commentList
        }
        return data

    def iterateComments(self, comments, parentId=None):
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
