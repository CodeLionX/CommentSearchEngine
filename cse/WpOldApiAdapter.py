import requests
import os
from string import Template

try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse

from cse.pipeline import Handler
from cse.util import Util

class WpOldApiAdapter(Handler):

    API_MUX_ENDPOINT = "https://comments-api.ext.nile.works/v2/mux"
    API_SEARCH_ENDPOINT = "https://comments-api.ext.nile.works/v1/search"

    __handlerContext = None


    def __init__(self):
        super()


    def loadComments(self, url):
        if self.__handlerContext is None:
            raise Exception("WpApiAdapter must be used within a WpApiAdapterHandler to use pipelining functionality!")

        data = self.__loadInitialRootComments(url)
        self.__processComments(data, url)

        while data['hasMoreChildren'] == "true":
            data = self.__loadMoreRootComments(url, data['nextPageAfter'])
            self.__processComments(data, url)


    def __buildDataSkeleton(self, url, assetId=None):
        return {
            "article_url" : url,
            "article_id" : assetId,
            "comments" : []
        }


    def __processComments(self, data, url):
        commentList = {}

        for entry in data["entries"]:
            cid = self.__extractCid(entry["object"]["id"])
            comment_author = entry["actor"]["title"]
            comment_text = entry["object"]["content"]
            timestamp = entry["object"]["published"]

            for target in entry["targets"]:
                try:
                   parent_comment_id = self.__extractCid(target["conversationID"])
                   break
                except KeyError:
                    pass
            if parent_comment_id == cid:
                parent_comment_id = None

            try:
                votes = entry["object"]["accumulators"]["likesCount"]
            except KeyError:
                votes = 0

            commentList[cid] = {
                "comment_author": comment_author,
                "comment_text" : comment_text,
                "timestamp" : timestamp,
                "parent_comment_id" : parent_comment_id,
                "votes" : votes
            }
            try:
                directReplies = self.__loadReplies(entry["object"]["id"], entry["object"]["accumulators"]["repliesCount"], entry["pageAfter"])
                self.__processComments(directReplies, url)
            except KeyError:
                pass

        # write comments to pipeline
        commentsObject = self.__buildDataSkeleton(url)
        commentsObject["comments"] = commentList
        self.__handlerContext.write(commentsObject)


    def __extractCid(self,url):
        path = urlparse(url).path
        return os.path.basename(path)


    def __loadInitialRootComments(self, url):
        qParams = {
            'childrenof': url,
            'source': 'washpost.com',
            'itemsPerPage': '150',
            'children': '0',
            'childrenItemsPerPage': '0'
        }
        t = Template('"((childrenof: $childrenof source:$source (((state:Untouched  AND user.state:ModeratorApproved) OR (state:ModeratorApproved  AND user.state:ModeratorApproved,Untouched) OR (state:CommunityFlagged,ModeratorDeleted AND user.state:ModeratorApproved) ) )   )) itemsPerPage: $itemsPerPage sortOrder:reverseChronological safeHTML:aggressive children: $children childrenSortOrder:chronological childrenItemsPerPage:$childrenItemsPerPage  (((state:Untouched  AND user.state:ModeratorApproved) OR (state:ModeratorApproved  AND user.state:ModeratorApproved,Untouched) OR (state:CommunityFlagged,ModeratorDeleted AND user.state:ModeratorApproved) ) ) "')
        getParams = {
            'appkey':'prod.washpost.com',
            'requests':'[{"id":"allPosts-search","method":"search","q": ' + t.safe_substitute(qParams) + '}]'
        }
        r = requests.get(self.API_MUX_ENDPOINT, params=getParams)
        data = Util.fromJsonString(r.text)["allPosts-search"]

        return data


    def __loadMoreRootComments(self, url, pageAfter):
        t = Template('((childrenof: $childrenof source:$source (((state:Untouched  AND user.state:ModeratorApproved) OR (state:ModeratorApproved  AND user.state:ModeratorApproved,Untouched) OR (state:CommunityFlagged,ModeratorDeleted AND user.state:ModeratorApproved) ) )   )) itemsPerPage: $itemsPerPage sortOrder:reverseChronological safeHTML:aggressive children: $children childrenSortOrder:chronological childrenItemsPerPage:$childrenItemsPerPage  (((state:Untouched  AND user.state:ModeratorApproved) OR (state:ModeratorApproved  AND user.state:ModeratorApproved,Untouched) OR (state:CommunityFlagged,ModeratorDeleted AND user.state:ModeratorApproved) ) )  pageAfter:"$pageAfter"')

        qParams = {
            'childrenof': str(url),
            'source': 'washpost.com',
            'children': '0',
            'childrenItemsPerPage': '0',
            'itemsPerPage': "150",
            'pageAfter': str(pageAfter)
        }
        getParams = {
            'appkey':'prod.washpost.com',
            "q": t.safe_substitute(qParams)
        }
        r = requests.get(self.API_SEARCH_ENDPOINT, params=getParams)
        data = Util.fromJsonString(r.text)
        
        return data


    def __loadReplies(self, parentIdUrl, replyCount, pageAfter):
        t = Template('childrenof:$childrenof children:$children childrenItemsPerPage:$childrenItemsPerPage itemsPerPage:$itemsPerPage sortOrder:chronological childrenSortOrder:chronological pageAfter:"$pageAfter" safeHTML:aggressive')

        qParams = {
            'childrenof': str(parentIdUrl),
            'source': 'washpost.com',
            'children': '0',
            'childrenItemsPerPage': '0',
            'itemsPerPage': str(replyCount), # todo: if there are more than 200 replies (in one layer) we will only receive the first 200
            'pageAfter': str(pageAfter)
        }
        getParams = {
            'appkey':'prod.washpost.com',
            "q": t.safe_substitute(qParams)
        }
        r = requests.get(self.API_SEARCH_ENDPOINT, params=getParams)
        data = Util.fromJsonString(r.text)
        return data


    # inherited from cse.pipeline.Handler
    def registeredAt(self, ctx):
        self.__handlerContext = ctx


    def process(self, ctx, data):
        raise Exception("This Adapter is the starting point of the pipeline, thus should not receive any data!")



if __name__ == "__main__":
    adapter = WpOldApiAdapter()
    adapter.loadComments('https://www.washingtonpost.com/news/morning-mix/wp/2017/11/06/an-unlikely-hero-describes-gun-battle-and-95-mph-chase-with-texas-shooting-suspect/')