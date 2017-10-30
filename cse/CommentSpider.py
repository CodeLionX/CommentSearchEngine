import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from cse.WpApiAdapter import WpApiAdapter
import re
import json
from pprint import pprint
from cse.WpApiParser import WpApiParser
import csv
import os

class CommentSpider(scrapy.Spider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'
    urls = [['https://www.washingtonpost.com/politics/courts_law/supreme-court-to-consider-major-digital-privacy-case-on-microsoft-email-storage/2017/10/16/b1e74936-b278-11e7-be94-fabb0f1e9ffb_story.html']]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(
                url=str(url[0]),
                callback=self.parse,
                method='GET',
                meta={'url': url[0]}
            )

    def parse(self, response):
        # parse an article page and watch out for comments on this page and for linked pages
        sel = Selector(response)
        url = sel.xpath('//meta[@property="og:url"]/@content').extract() #ToDo: Check if url has an value

        api = WpApiAdapter()

        #ToDo This should return the final spiderdata
        reply = api.loadComments(url=url[0])
        data = WpApiParser().parseSpiderData(url[0],reply[0],reply[1])

        #ToDo Write data to a csv file
        #print(type(comments))
        self.printcsv(data)
        pprint(data)
        #print(json.loads(comments))#.dump(sort_keys=False, indent=4))

        """
        nextLinks = sel.xpath("//div[@class='comment-section__item']//a[@class='pager__button pager__button--next']/@href").extract()
        if len(nextLinks) == 0:
            nextLinks = sel.xpath("//a[contains(@class, 'zb-pager__btn-rel-next')]/@href").extract()

        # scrape linked pages
        if (len(nextLinks) > 0):
            nextLink = nextLinks[0]
            request = scrapy.Request(nextLink, callback = self.parse)
            print("Paging:", nextLinks[0])
            request.meta['url'] = nextLinks[0]
            yield request

        replyLinks = sel.xpath("//div[contains(@class, 'comment__container')]//*[@data-url]/@data-url").extract()
        for reply in replyLinks:
            request = scrapy.Request(reply, callback = self.parse_replies)
            request.meta['url'] = url
            yield request
        """
        """
        comments_scope = sel.xpath("//div[contains(@class, 'talk-stream-comment-level-0')]").extract()
        for comment in comments_scope:
            print("found: " + comment)
            self.parse_comment(comment, url)
        """
    # scrape comments that are hidden on the current page
    def parse_replies(self, response):
        sel = Selector(response)
        url = response.meta['url']
        comments_scope = sel.xpath("//article[contains(@class, 'comment')]").extract()
        for comment in comments_scope:
            self.parse_comment(comment, url)

    # scrape comments
    def parse_comment(self, comment, url):
        comment_selector = Selector(text=comment)
        extracted_comment = {
            'url': re.sub('\?.*', '', url)
        }

        #user_url = comment_selector.xpath("//div[contains(@class, 'comment-meta__name')]/a/@href").extract()
        #extracted_comment['user_url'] = user_url[0] if len(user_url) > 0 else ''
        extracted_comment['user_url'] = "tbd"

        user_name = comment_selector.xpath("//span[contains(@class, 'AuthorName__name___3O4jF')]/text()").extract()
        extracted_comment['user_name'] = user_name

        """
        comment_text = comment_selector.xpath("//div[contains(@class, 'comment__body')]//text()").extract()
        extracted_comment['comment_text'] = '\n'.join([x.strip() for x in comment_text]).strip() if len(comment_text) > 0 else ''

        comment_recommendations = comment_selector.xpath("//*[@class='js-comment-recommendations']//text()").extract()
        extracted_comment['recommendations'] = int(comment_recommendations[0]) if len(comment_recommendations) > 0 else 0

        nth_comment_in_article = comment_selector.xpath("//*[contains(@class, 'comment-meta__date')]//text()").extract()
        extracted_comment['nth_comment_in_article'] = re.sub('#', '', re.sub('\xa0.*', '', nth_comment_in_article[0])).strip() if len(nth_comment_in_article) > 0 else ''

        respond_to = comment_selector.xpath("//div[@class='comment__reactions']/a[@class='comment__origin js-jump-to-comment']/strong[2]/text()").extract()
        extracted_comment['respond_to'] = respond_to[0].strip() if len(respond_to) > 0 else None

        comment_cid = comment_selector.xpath("//*[contains(@class, 'comment-meta__date')]/@href").extract()
        if len(comment_cid) > 0:
            cid = re.sub('.*cid-', '', comment_cid[0])
        else:
            cid = None
        extracted_comment['cid'] = cid

        parent_comment = comment_selector.xpath("//a[contains(@class,'comment__origin')]/@href").extract()
        if len(parent_comment) > 0:
            pid = re.sub('.*cid-', '', parent_comment[0])
        else:
            pid = None
        extracted_comment['pid'] = pid
        """

        print(extracted_comment)
        print("\n\nFINISHED")

    def printcsv(self, data):
        article_url = data["article_url"]
        article_id = data["article_id"]

        filename = "data/data.csv"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)#, delimiter=', ')
            writer.writerow(["cid", "url", "author", "text", "time", "parent", "votes", "article_id"])
            for commentId in data["comments"]:
                writer.writerow([
                commentId,
                article_url,
                data["comments"][commentId]["comment_author"],#.encode('ascii'),
                data["comments"][commentId]["comment_text"],#.encode('utf-8'),
                data["comments"][commentId]["timestamp"],
                data["comments"][commentId]["parent_comment_id"],
                data["comments"][commentId]["votes"],
                article_id
                ])
