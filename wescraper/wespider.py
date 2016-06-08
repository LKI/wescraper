import config
import json
import logging
from HTMLParser import HTMLParser as hp
from cookie import Cookie
from datetime import datetime
from random import random
from scrapy import Spider, Request

class WeSpider(Spider):
    """
    The WeSpider class will use weixin.sogou.com to search the official
    accounts. And get the first ten article infomation of each official
    account.
    """
    article_infos = {}
    cookie_pool   = Cookie()
    name          = 'wespider'

    def start_requests(self):
        """
        Actually, it's better to use __init__ to pass the attributes. But I've
        tried and failed. So I use scrapy settings for a workaround.
        """
        start_point = {
            config.type_acc  : [
                                "http://weixin.sogou.com/weixin?type=1&ie=utf8&_sug_=n&_sug_type_=&query=",
                                "http://weixin.sogou.com/weixin?query="
                               ],
            config.type_all  : ["http://weixin.sogou.com/weixin?type=2&query="],
            config.type_day  : ["http://weixin.sogou.com/weixin?type=2&sourceid=inttime_day&tsn=1&query="],
            config.type_week : ["http://weixin.sogou.com/weixin?type=2&sourceid=inttime_week&tsn=2&query="],
            config.type_mon  : ["http://weixin.sogou.com/weixin?type=2&sourceid=inttime_month&tsn=3&query="],
            config.type_year : ["http://weixin.sogou.com/weixin?type=2&sourceid=inttime_year&tsn=4&query="]
        }
        account_list = self.settings.get("ACCOUNT_LIST", [])
        search_type = self.settings.get("SEARCH_TYPE", config.type_acc)
        random_urls = start_point[search_type]
        self.start_urls = map(lambda x: random_urls[int(random() * len(random_urls))] + x, account_list)
        for url in self.start_urls:
            if search_type == config.type_acc:
                yield Request(url, cookies=self.cookie_pool.fetch_one(), callback=self.parse)
            else:
                yield Request(url, cookies=self.cookie_pool.fetch_one(), callback=self.parse_keyword)

    def parse(self, response):
        """
        Parse the result from the main search page and crawl into each result.
        """
        logger = logging.getLogger(response.url[-10:])
        logger.debug(str("Current cookie: " + str(self.cookie_pool.current())))
        if "/antispider/" in response.url:
            cookie = self.cookie_pool.get_banned()
            if cookie:
                logger.debug(str("Got banned. Using new cookie: " + str(cookie)));
                yield Request(response.url, cookies=cookie, callback=self.parse)
            else:
                yield self.error(u"Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url))
        else:
            self.cookie_pool.set_return_header(response.headers.getlist('Set-Cookie'))
            yield Request(
                response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href').extract_first(),
                callback=self.parse_account
            )

    def parse_keyword(self, response):
        logger = logging.getLogger(response.url[-10:])
        logger.debug(str("Current cookie: " + str(self.cookie_pool.current())))
        if "/antispider/" in response.url:
            cookie = self.cookie_pool.get_banned()
            if cookie:
                logger.debug(str("Got banned. Using new cookie: " + str(cookie)));
                yield Request(response.url, cookies=cookie, callback=self.parse)
            else:
                yield self.error(u"Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url))
        else:
            self.cookie_pool.set_return_header(response.headers.getlist('Set-Cookie'))
            articles = response.xpath('//div[@class="results"]/div[contains(@class, "wx-rb")]')
            for i in range(0, len(articles)):
                url = response.urljoin(articles.xpath('//div/h4/a/@href')[i].extract())
                cover = hp().unescape(hp().unescape(articles.xpath('//div/a/img/@src')[i].extract())).replace('\\/', '/')
                date = datetime.fromtimestamp(int(articles.xpath('//div/div/span/script/text()')[i].extract()[22:-2])).strftime(config.date_format)
                digest = articles.xpath('//div[@class="txt-box"]/p')[i].extract()
                self.article_infos[url] = {
                    'cover'  : cover,
                    'date'   : date,
                    'digest' : digest
                }
                yield Request(url, callback=self.parse_article)

    def parse_account(self, response):
        """
        Parse the account page and crawl into each article.

        Note: this account page does not render HTML code from very beginning.
        It use JavaScript and a Json string to render the page dynamicly. So we
        use python-json module to parse the Json string.
        """
        articles = json.loads(response.xpath('//script[@type="text/javascript"]/text()')[2].re(r'var msgList = \'(.*)\'')[0])['list']
        for article in articles:
            appinfo = article['app_msg_ext_info']
            allinfo = [appinfo] + (appinfo[u'multi_app_msg_item_list'] if u'multi_app_msg_item_list' in appinfo else [])
            cominfo = article['comm_msg_info']
            for info in allinfo:
                # Unescape the HTML tags twice
                url  = "http://mp.weixin.qq.com/s?" + hp().unescape(hp().unescape(info['content_url'][4:]))
                self.article_infos[url] = {
                    'cover'  : hp().unescape(hp().unescape(info['cover'])).replace('\\/', '/'),
                    'date'   : datetime.fromtimestamp(int(cominfo['datetime'])).strftime(config.date_format),
                    'digest' : info['digest']
                }
                yield Request(url, callback=self.parse_article)

    def parse_article(self, response):
        """
        Finally we've got into the article page. Since response.url is generated
        dynamically, we need to get the permenant URL of the article.
        """
        title  = response.xpath('//div[@id="page-content"]/div/h2/text()').extract_first(default=config.not_found_hint).strip()
        user   = response.xpath('//*[@id="post-user"]/text()').extract_first(default=config.not_found_hint).strip()
        script = response.xpath('//script[contains(text(), "var biz =")]')[0]
        params = ['biz', 'sn', 'mid', 'idx']
        values = map(lambda x:x + '=' + script.re('var ' + x + ' = .*"([^"]*)";')[0], params)
        url    = "http://mp.weixin.qq.com/s?" + reduce(lambda x,y:x+'&'+y, values)
        html   = str.join("\n", response.xpath('//*[@id="js_content"]').extract()).strip()
        info   = self.article_infos[response.url]
        yield {
            u'title'   : unicode(title),
            u'account' : unicode(user),
            u'url'     : unicode(url),
            u'date'    : unicode(info['date']),
            u'cover'   : unicode(info['cover']),
            u'digest'  : unicode(info['digest']),
            u'content' : unicode(html)
        }

    def error(self, msg):
        return {u"error" : msg, u"date" : unicode(datetime.now().strftime(config.date_format))}
