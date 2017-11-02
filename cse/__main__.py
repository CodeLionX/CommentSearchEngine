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
    args = parser.parse_args()

    print("This is the main routine.")

    # for now just call the crawler/spider
    crawl(args)


def crawl(args=None):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'ERROR'
    })

    process.crawl(CommentSpider)
    process.start() # the script will block here until the crawling is finished

if __name__ == "__main__":
    main()
