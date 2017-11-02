import requests
import os

#from cse.WpApiParser import WpApiParser
from cse.util import Util

class WpApiAdapter:

    API_ENDPOINT = "https://www.washingtonpost.com/talk/api/v1/graph/ql"

    __initialQuery = ""
    __moreQuery = ""
    __handlerContext = None

    def __init__(self):
        self.__initialQuery = self.__loadInitialQuery()
        self.__moreQuery = self.__loadMoreQuery()


    @staticmethod
    def __loadInitialQuery():
        with open(os.path.join(os.path.dirname(__file__), "wpCommentsQuery.txt")) as query_file:
            query = query_file.read().strip()
        return query


    @staticmethod
    def __loadMoreQuery():
        with open(os.path.join(os.path.dirname(__file__), "wpMoreCommentsQuery.txt")) as query_file:
            query = query_file.read().strip()
        return query


    @staticmethod
    def countAllComments(comments):
        def countInList(comments, count):
            for comment in comments:
                count = countInNode(comment, count)
            return count

        def countInNode(comment, count):
            if('replies' in comment and 'nodes' in comment['replies']):
                return countInList(comment['replies']['nodes'], count) + 1
            else:
                return count + 1

        return countInList(comments, 0)


    def injectCtx(self, handlerContext):
        self.__handlerContext = handlerContext


    def loadComments(self, url):
        if self.__handlerContext is None:
            raise Exception("WpApiAdapter must be used within a WpApiAdapterHandler to use pipelining functionality!")
        
        payload = self.__buildInitialRequstPayload(url)

        response = requests.request("POST",
            self.API_ENDPOINT,
            data = Util.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = Util.fromJsonString(response.text)
        assetId = data['data']['asset']['id']

        #assetUrl = data['data']['asset']['url']
        #commentCount = data['data']['asset']['commentCount']
        #totalCommentCount = data['data']['asset']['totalCommentCount']
        commentsNode = data['data']['asset']['comments']
        
        comments = self.__processComments(commentsNode, url, assetId)
        return [assetId, comments]


    def __buildInitialRequstPayload(self, url):
        return {
            "query": self.__initialQuery,
            "variables": {
                "assetId": "",
                "assetUrl": url,
                "commentId": "",
                "hasComment": False,
                "excludeIgnored": False,
                "sortBy": "CREATED_AT",
                "sortOrder": "DESC",
                "operationName": "CoralEmbedStream_Embed"
            }
        }
    

    def __buildMoreRequestPayload(self, assetId, cursor=None, parentId=None):
        return {
            "query": self.__moreQuery,
            "variables": {
                "asset_id": assetId,
                "cursor": cursor,
                #"limit": 10,
                "parent_id": parentId,
                "sortOrder": "DESC",
                "sortBy": "CREATED_AT",
                "excludeIgnored": False
            },
            "operationName":"CoralEmbedStream_LoadMoreComments"
        }


    def __processComments(self, commentsNode, url, assetId, parentId=None):
        commentsHasNextPage = commentsNode['hasNextPage']
        commentsCursor = commentsNode['endCursor']
        comments = commentsNode['nodes']

        data={"url": url, "assetId": assetId, "parentId": parentId, "comments": comments}
        self.__handlerContext.write(data)

        # check for replies
        for com in comments:
            repliesParentId = com['id']
            repliesHasNextPage = com['replies']['hasNextPage']
            repliesCursor = com['replies']['endCursor']
            replies = com['replies']['nodes']

            if(repliesHasNextPage):
                com['replies']['nodes'] = replies + self.__loadMoreReplies(url, assetId, repliesCursor, repliesParentId)

        # check for another page
        if(commentsHasNextPage):
            comments = comments + self.__loadMoreComments(url, assetId, commentsCursor)

        return comments


    def __loadMoreComments(self, url, assetId, cursor):
        payload = self.__buildMoreRequestPayload(assetId, cursor=cursor)

        response = requests.request("POST", 
            self.API_ENDPOINT,
            data = Util.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = Util.fromJsonString(response.text)
        commentsNode = data['data']['comments']

        return self.__processComments(commentsNode, url, assetId)


    def __loadMoreReplies(self, url, assetId, cursor, parentId):
        payload = self.__buildMoreRequestPayload(assetId, cursor=cursor, parentId=parentId)

        response = requests.request("POST", 
            self.API_ENDPOINT,
            data = Util.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = Util.fromJsonString(response.text)
        commentsNode = data['data']['comments']

        return self.__processComments(commentsNode, url, assetId, parentId)


# just for testing
if __name__ == "__main__":
    api = WpApiAdapter()
    comments = api.loadComments(url="https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html")
    print(Util.toJsonString(comments))
