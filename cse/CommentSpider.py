import os
import re
import scrapy
from scrapy.selector import Selector
from scrapy import signals
from scrapy.spiders import SitemapSpider
from scrapy.crawler import CrawlerProcess
from cse.WpApiDataPipelineBootstrap import WpApiDataPipelineBootstrap as PipelineBootstrap
from cse.WpOldApiDataPipelineBootstrap import WpOldApiDataPipelineBootstrap as PipelineBootstrapOld
from cse.CommentWriter import CommentWriter
from cse.CommentIdWriter import CommentIdWriter
from cse.ArticleIdWriter import ArticleIdWriter

class CommentSpider(SitemapSpider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'
    sitemap_urls = []
    other_urls = []

    __pbs = None
    __pbsOld = None
    __writer = None
    __commentIdWriter = None
    __visitedURLs = []
    __nextArcticleId = 0


    def __init__(self, sitemaps=[], urls=[], *args, **kwargs):
        super().__init__(self)

        self.sitemap_urls = sitemaps
        self.other_urls = urls

        self.__pbs = PipelineBootstrap()
        self.__pbs.setupPipeline()
        self.__pbsOld = PipelineBootstrapOld()
        self.__pbsOld.setupPipeline()
        self.__setupCommentIdWriter("commentIdMap.csv")
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
        writer = CommentIdWriter(os.path.join("data", filename))
        self.__pbs.registerDataListener(writer.processCommentIds)
        self.__pbsOld.registerDataListener(writer.processCommentIds)
        self.__commentIdWriter = writer
    

    def __teardownCommentIdWriter(self):
        self.__pbs.unregisterDataListener(self.__commentIdWriter.processCommentIds)
        self.__pbsOld.unregisterDataListener(self.__commentIdWriter.processCommentIds)
        self.__commentIdWriter.close()


    def __setupFileWriter(self, filename):
        writer = CommentWriter(os.path.join("data", filename))
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
        self.__teardownCommentIdWriter()
        self.__teardownFileWriter()
        self.__writeArcticleIds()

    def __writeArcticleIds(self):
        writer = ArticleIdWriter(os.path.join("data", 'articleIds.csv'))
        writer.open()
        writer.printHeader()
        writer.printData(self.__visitedURLs)
        writer.close()


    def parse(self, response):
        try:
            self.__pbs.crawlComments(response.url, self.__nextArcticleId)
        except:
            print('fail new API\n')

        try:
            self.__pbsOld.crawlComments(response.url, self.__nextArcticleId)
        except:
            print('fail old API\n')
        
        self.__visitedURLs.append(response.url)
        self.__nextArcticleId = self.__nextArcticleId + 1
