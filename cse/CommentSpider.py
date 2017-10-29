import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import re

class CommentSpider(scrapy.Spider):
    # this spider scrapes a single article within the domain washingtonpost.com (https://www.washingtonpost.com/)
    name = 'washingtonpost.com'
    urls = [['https://www.washingtonpost.com/news/post-politics/wp/2017/10/29/frustrated-with-the-russia-investigation-trump-demands-democrats-and-hillary-clinton-face-more-scrutiny/?hpid=hp_hp-top-table-main_pp-trump-tweet-1145am%3Ahomepage%2Fstory&utm_term=.2b448898a5be']]

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
        url = response.meta['url']
        sel = Selector(response)
        print(response.body)

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

        comments_scope = sel.xpath("//div[contains(@class, 'talk-stream-comment-level-0')]").extract()
        for comment in comments_scope:
            print("found: " + comment)
            self.parse_comment(comment, url)

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
