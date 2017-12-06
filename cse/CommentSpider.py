import os

import scrapy
from scrapy.selector import Selector
from scrapy import signals
from scrapy.spiders import SitemapSpider

from cse.WpApiDataPipelineBootstrap import WpApiDataPipelineBootstrap as PipelineBootstrap
from cse.WpOldApiDataPipelineBootstrap import WpOldApiDataPipelineBootstrap as PipelineBootstrapOld
from cse.writer import CommentWriter



class CommentSpider(SitemapSpider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'

    directoryPath            = "data"
    commentsFilepath         = os.path.join(directoryPath, "comments.csv")
    commentIdMappingFilepath = os.path.join(directoryPath, "commentIdMapping.csv")
    articleMappingFilepath   = os.path.join(directoryPath, "articleMapping.csv")
    authorMappingFilepath    = os.path.join(directoryPath, "authorMapping.csv")

    __writer = None
    __commentIdHandler = None


    def __init__(self, sitemaps=[], urls=[], *args, **kwargs):
        super(CommentSpider, self).__init__(self)

        self.sitemap_urls = sitemaps
        self.other_urls = urls

        self.__setupCommentIdWriter("commentIdMap.csv")
        self.__pbs = PipelineBootstrap(self.__commentIdHandler)
        self.__pbs.setupPipeline()
        self.__pbsOld = PipelineBootstrapOld(self.__commentIdHandler)
        self.__pbsOld.setupPipeline()
        self.__setupFileWriter("comments.csv")


    def start_requests(self):
        requests = list(super(CommentSpider, self).start_requests())
        requests += [scrapy.Request(x, self.parse) for x in self.other_urls]
        return requests


    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CommentSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider


    def __setupCommentIdWriter(self, filename):
        writer = CommentIdHandler(os.path.join("data", filename))
        self.__commentIdHandler = writer


    def __teardownCommentIdWriter(self):
        self.__commentIdHandler.close()


    def __setupFileWriter(self, filename):
        writer = CommentWriter(
            CommentSpider.commentsFilepath, 
            CommentSpider.commentIdMappingFilepath, 
            CommentSpider.articleMappingFilepath, 
            CommentSpider.authorMappingFilepath
        )
        writer.open()
        writer.printHeader()
        self.__pbs.registerDataListener(writer.printData)
        self.__pbsOld.registerDataListener(writer.printData)
        self.__writer = writer


    def __teardownFileWriter(self):
        self.__pbs.unregisterDataListener(self.__writer.printData)
        self.__pbsOld.unregisterDataListener(self.__writer.printData)
        self.__writer.close()


    def spider_closed(self, spider):
        self.__teardownFileWriter()
        self.__teardownCommentIdWriter()


    def parse(self, response):
        try:
            self.__pbs.crawlComments(response.url, 0) #FIXME remove id
        except:
            print('fail new API\n')

        try:
            self.__pbsOld.crawlComments(response.url, 0) #FIXME remove id
        except:
            print('fail old API\n')
