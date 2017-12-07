import argparse
from scrapy.crawler import CrawlerProcess
from cse.CommentSpider import CommentSpider
from cse.__init__ import __version__
from cse.__init__ import __title__

def main(args=None):
    """The main routine."""

    # parse args
    parser = argparse.ArgumentParser(description='Crawl a specific news website for comments')
    parser.add_argument('--version', action='version', version=__title__ + __version__)
    parser.add_argument('-s','--sitemap', action='append', dest='sitemaps', default=[], help='sitemaps that should be crawled. can be used multiple times.')
    parser.add_argument('-u','--url', action='append', dest='urls', default=[],  help='specific URLs that should be crawled. can be used multiple times.')
    args = parser.parse_args()

    print("This is the main routine.")

    # for now just call the crawler/spider
    crawl(args)


def crawl(args=None):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'LOG_LEVEL': 'DEBUG',
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    })

    process.crawl(CommentSpider, sitemaps=args.sitemaps, urls=args.urls)
    process.start() # the script will block here until the crawling is finished



if __name__ == "__main__":
    main()
