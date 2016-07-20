import config
import json
import logging
from HTMLParser import HTMLParser as hp
from cookie import Cookie
from datetime import datetime, timedelta
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
        for i, url in enumerate(self.start_urls):
            cookie = self.cookie_pool.fetch_one()
            if search_type == config.type_acc:
                yield Request(url, cookies=cookie, callback=self.parse,
                        meta={'cookiejar' : i, 'current_cookie' : cookie})
            else:
                yield Request(url, cookies=cookie, callback=self.parse_keyword,
                        meta={'cookiejar' : i, 'current_cookie' : cookie})

    def parse(self, response):
        """
        Parse the result from the main search page and crawl into each result.
        """
        current_cookie = response.meta['current_cookie']
        logger = logging.getLogger(response.url[-10:])
        logger.debug(str("Current cookie: " + str(current_cookie)))
        if "/antispider/" in response.url:
            cookie = self.cookie_pool.get_banned(current_cookie)
            if cookie:
                logger.debug(str("Got banned. Using new cookie: " + str(cookie)));
                yield Request(response.request.meta['redirect_urls'][0], cookies=cookie, callback=self.parse,
                        meta={'cookiejar' : response.meta['cookiejar'], 'current_cookie' : cookie})
            else:
                yield self.error("Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url))
        else:
            if self.no_results(response):
                if config.always_return_in_format:
                    yield self.error_in_format("No article found")
                else:
                    yield self.error(u"No article found")
            else:
                self.cookie_pool.set_return_header(response.headers.getlist('Set-Cookie'), current_cookie)
                yield Request(
                    response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href').extract_first(),
                    callback=self.parse_account
                )

    def parse_keyword(self, response):
        current_cookie = response.meta['current_cookie']
        logger = logging.getLogger(response.url[-10:])
        logger.debug(str("Current cookie: " + str(current_cookie)))
        if "/antispider/" in response.url:
            cookie = self.cookie_pool.get_banned(current_cookie)
            if cookie:
                logger.debug(str("Got banned. Using new cookie: " + str(cookie)));
                yield Request(response.request.meta['redirect_urls'][0], cookies=cookie, callback=self.parse,
                        meta={'cookiejar' : response.meta['cookiejar'], 'current_cookie' : cookie})
            else:
                yield self.error("Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url))
        else:
            self.cookie_pool.set_return_header(response.headers.getlist('Set-Cookie'), current_cookie)
            articles = response.xpath('//div[@class="results"]/div[contains(@class, "wx-rb")]')
            if self.no_results(response) or not len(articles):
                if config.always_return_in_format:
                    yield self.error_in_format("No article found")
                else:
                    yield self.error("No article found")
            else:
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
        for script in response.xpath('//script[@type="text/javascript"]/text()'):
            if 'var msgList = \'' in script.extract():
                articles = json.loads(script.re(r'var msgList = \'(.*)\'')[0])['list']
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
        script = response.xpath('//script[contains(text(), "var msg_link =")]')[0]
        params = ['__biz', 'sn', 'mid', 'idx']
        url    = hp().unescape(script.re('var msg_link = .*"([^"]*)";')[0])
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
        return {u"error" : unicode(msg), u"date" : unicode(datetime.now().strftime(config.date_format))}

    def no_results(self, response):
        if len(response.xpath("///div[@id='smart_hint_container']")):
            smart_hint = response.xpath("///div[@id='smart_hint_container']/text()").extract_first()
            if u'\uff08\u4e0d\u542b\u5f15\u53f7\uff09\u7684\u641c\u7d22\u7ed3\u679c\uff1a' == smart_hint:
                return True
            else:
                return False
        elif len(response.xpath("///div[@class='no-sosuo']")):
            return True
        else:
            return False

    def error_in_format(self, msg):
        date = str(datetime.now().strftime(config.date_format))
        yesterday = str((datetime.now() - timedelta(days=1)).strftime(config.date_format))
        return {
            u'title'   : unicode("{} at {}".format(msg, date)),
            u'account' : unicode(""),
            u'url'     : unicode("http://localhost/{}".format(date)),
            u'date'    : unicode(date),
            u'cover'   : unicode(""),
            u'digest'  : unicode(""),
            u'content' : unicode("{} at {}".format(msg, date))
        }
