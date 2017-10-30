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

    def buildMoreCommentsRequestPayload(self, assetId, cursor=None, parentId=None):
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
            sort_keys=True, 
            separators=(', ', ': '), 
            indent=None # prettyprinting: indent=2
        )

    def fromJsonString(self, s):
        return json.loads(s)

    def loadComments(self, url):
        payload = self.buildInitialRequstPayload(url)

        response = requests.request("POST", 
            self.apiEndpoint, 
            data = self.toJsonString(payload), 
            headers = {'content-type': 'application/json'}
        )

        data = self.fromJsonString(response.text)
        assetId = data['data']['asset']['id']
        assetUrl = data['data']['asset']['url']
        commentCount = data['data']['asset']['commentCount']
        totalCommentCount = data['data']['asset']['totalCommentCount']
        hasNextPage = data['data']['asset']['comments']['hasNextPage']
        cursor = data['data']['asset']['comments']['endCursor']
        comments = data['data']['asset']['comments']['nodes']

        # check for missing replies
        

        # check for another page
        if(hasNextPage):
            comments = comments + self.loadMoreComments(assetId, cursor, comments)

        return comments

    def loadMoreComments(self, assetId, cursor, comments):
        payload = self.buildMoreCommentsRequestPayload(assetId, cursor=cursor)

        response = requests.request("POST", 
            self.apiEndpoint, 
            data = self.toJsonString(payload), 
            headers = {'content-type': 'application/json'}
        )

        data = self.fromJsonString(response.text)
        hasNextPage = data['data']['comments']['hasNextPage']
        nextCursor = data['data']['comments']['endCursor']
        coms = data['data']['comments']['nodes']

        if(hasNextPage):
            coms = coms + self.loadMoreComments(assetId, nextCursor, comments)

        return comments + coms


# just for testing
if __name__ == "__main__":
    api = WpApiAdapter()
    comments = api.loadComments(url="https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html")
    #print(comments.amount)
    print(len(comments))
    #print(api.loadInitialQuery())
