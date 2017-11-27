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

class CommentSpider(SitemapSpider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'
    #sitemap_urls = ['https://www.washingtonpost.com/robots.txt']
    sitemap_urls = ['http://www.washingtonpost.com/news-politics-sitemap.xml', 'http://www.washingtonpost.com/news-opinions-sitemap.xml','http://www.washingtonpost.com/news-local-sitemap.xml','http://www.washingtonpost.com/news-national-sitemap.xml']
    other_urls = []

    __pbs = None
    __pbsOld = None
    __writer = None


    def __init__(self):
        super().__init__(self)
        self.__pbs = PipelineBootstrap()
        self.__pbs.setupPipeline()
        self.__pbsOld = PipelineBootstrapOld()
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
        self.__teardownFileWriter()


    def parse(self, response):
        try:
            self.__pbs.crawlComments(response.url)
        except:
            print('fail new API\n')

        try:
            self.__pbsOld.crawlComments(response.url)
        except:
            print('fail old API\n')
