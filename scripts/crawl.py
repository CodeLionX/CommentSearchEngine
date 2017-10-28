import sys
import argparse
from scrapy.crawler import CrawlerProcess
from cse import CommentSpider
from cse import __version__
from cse import __title__

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    # TODO: parse args
    parser = argparse.ArgumentParser(description='Crawl a specific news website for comments')
    parser.add_argument('--version', action='version', version=__title__ + ': %(prog)s ' + __version__ )
    args = parser.parse_args()

    print("This is the main routine.")

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'ERROR'
    })

    process.crawl(CommentSpider)
    process.start() # the script will block here until the crawling is finished


if __name__ == "__main__":
    main()