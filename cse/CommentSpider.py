import scrapy
from scrapy.spiders import SitemapSpider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import re
import json
from pprint import pprint
import hashlib

from cse.WpApiDataPipelineBootstrap import WpApiDataPipelineBootstrap as PipelineBootstrap
from cse.CSVWriter import CSVWriter

class CommentSpider(SitemapSpider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'
    #sitemap_urls = ['https://www.washingtonpost.com/robots.txt']
    sitemap_urls = ['http://www.washingtonpost.com/news-politics-sitemap.xml', 'http://www.washingtonpost.com/news-opinions-sitemap.xml','http://www.washingtonpost.com/news-local-sitemap.xml','http://www.washingtonpost.com/news-national-sitemap.xml']
    
    #sitemap_follow = ['/web-sitemap-index','/news-sitemap-index','/real-estate/sitemap']#news-sitemap-index']
    __pbs = None


    def __init__(self):
        super().__init__(self)
        self.__pbs = PipelineBootstrap()
        self.__pbs.setupPipeline()


    def __setupFileWriter(self, url):
        m = hashlib.sha256()
        m.update(url.encode('utf-8'))
        filename = m.hexdigest()

        writer = CSVWriter("data/" + filename)
        writer.open()
        writer.printHeader()
        self.__pbs.registerDataListener(writer.printData)
        return writer


    def __teardownFileWriter(self, writer):
        self.__pbs.unregisterDataListener(writer.printData)
        writer.close()

    def parse(self, response): #TODO check if the current page needs to be crawled for comments (there will also be some sites without a comment section)
        # parse an article page and watch out for comments on this page and for linked pages
        sel = Selector(response)
        url = sel.xpath('//meta[@property="og:url"]/@content').extract() #ToDo: Check if url has an value
        try:
            url = url[0]
            writer = self.__setupFileWriter(url)
            self.__pbs.crawlComments(url)
            self.__teardownFileWriter(writer)
        except:
            print('fail\n')



if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'ERROR'
    })

    process.crawl(CommentSpider)
    process.start() # the script will block here until the crawling is finished