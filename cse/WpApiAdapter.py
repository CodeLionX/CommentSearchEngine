import requests
import json
import os

class WpApiAdapter:

    apiEndpoint = "https://www.washingtonpost.com/talk/api/v1/graph/ql"

    def loadInitialQuery(self):
        with open(os.path.join(os.path.dirname(__file__), "wpCommentsQuery.txt")) as query_file:
            query = query_file.read().strip()
        return query

    def loadMoreQuery(self):
        with open(os.path.join(os.path.dirname(__file__), "wpMoreCommentsQuery.txt")) as query_file:
            query = query_file.read().strip()
        return query

    def buildInitialRequstPayload(self, url):
        return {
            "query": self.loadInitialQuery(),
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

    def buildMoreRequestPayload(self, assetId, cursor=None, parentId=None):
        return {
            "query": self.loadMoreQuery(),
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

    def toJsonString(self, d):
        return json.dumps(d,
            ensure_ascii=False,
            sort_keys=True, 
            separators=(', ', ': '), 
            indent=None # prettyprinting: indent=2
        )

    def fromJsonString(self, s):
        return json.loads(s,
            encoding='UTF-8'
        )

    def loadComments(self, url):
        payload = self.buildInitialRequstPayload(url)

        response = requests.request("POST", 
            self.apiEndpoint,
            data = self.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = self.fromJsonString(response.text)
        assetId = data['data']['asset']['id']
        #assetUrl = data['data']['asset']['url']
        #commentCount = data['data']['asset']['commentCount']
        #totalCommentCount = data['data']['asset']['totalCommentCount']
        commentsNode = data['data']['asset']['comments']
        
        return self.processComments(commentsNode, assetId)


    def processComments(self, commentsNode, assetId):
        commentsHasNextPage = commentsNode['hasNextPage']
        commentsCursor = commentsNode['endCursor']
        comments = commentsNode['nodes']

        # check for replies
        for com in comments:
            parentId = com['id']
            repliesHasNextPage = com['replies']['hasNextPage']
            repliesCursor = com['replies']['endCursor']
            replies = com['replies']['nodes']

            if(repliesHasNextPage):
                com['replies']['nodes'] = replies + self.loadMoreReplies(assetId, repliesCursor, parentId)

        # check for another page
        if(commentsHasNextPage):
            comments = comments + self.loadMoreComments(assetId, commentsCursor)

        return comments


    def loadMoreComments(self, assetId, cursor):
        payload = self.buildMoreRequestPayload(assetId, cursor=cursor)

        response = requests.request("POST", 
            self.apiEndpoint,
            data = self.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = self.fromJsonString(response.text)
        commentsNode = data['data']['comments']

        return self.processComments(commentsNode, assetId)


    def loadMoreReplies(self, assetId, cursor, parentId):
        payload = self.buildMoreRequestPayload(assetId, cursor=cursor, parentId=parentId)

        response = requests.request("POST", 
            self.apiEndpoint,
            data = self.toJsonString(payload),
            headers = {'content-type': 'application/json'}
        )

        data = self.fromJsonString(response.text)
        commentsNode = data['data']['comments']

        return self.processComments(commentsNode, assetId)


    def countAllComments(self, comments):
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


# just for testing
if __name__ == "__main__":
    api = WpApiAdapter()
    comments = api.loadComments(url="https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html")
    print(str(api.countAllComments(comments)))
