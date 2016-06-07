import json
import logging
from random import random
from datetime import datetime
from scrapy import Spider, Request
from HTMLParser import HTMLParser as hp
from cookie import Cookie


class KeywordSpider(Spider):
    name = 'weixin'
    article_infos = {}
    cookie_pool_size = 5
    cookie_pool = Cookie()

    def start_requests(self):
        start_urls = {
            "all"   : "http://weixin.sogou.com/weixin?type=2&query=",
            "day"   : "http://weixin.sogou.com/weixin?type=2&sourceid=inttime_day&tsn=1&query=",
            "week"  : "http://weixin.sogou.com/weixin?type=2&sourceid=inttime_week&tsn=2&query=",
            "month" : "http://weixin.sogou.com/weixin?type=2&sourceid=inttime_month&tsn=3&query=",
            "year"  : "http://weixin.sogou.com/weixin?type=2&sourceid=inttime_year&tsn=4&query="
        }
        account_list = self.settings.get("ACCOUNT_LIST")
        search_type = self.settings.get("SEARCH_TYPE")
        self.start_urls = map(lambda x: start_urls[search_type] + x, account_list)
        for url in self.start_urls:
            # Get a random cookie
            clist = self.cookie_pool.get_cookies()
            if len(clist) < self.cookie_pool_size:
                self.cookie = {}
            else:
                self.cookie = clist[int(random() * len(clist))]
            yield Request(url, cookies=self.cookie, callback=self.parse)

    def parse(self, response):
        logger = logging.getLogger(response.url[-6:])
        logger.debug(str("Using cookie :" + str(self.cookie)))
        if "/antispider/" in response.url:
            self.cookie_pool.remove(self.cookie)   # This cookie is banned, remove it
            clist = self.cookie_pool.get_cookies() # Use a new cookie to query
            if 0 == len(clist):                    # If we run out of cookie, then our IP could be banned
                yield {
                    u"error": u"Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url),
                    u"date" : unicode(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                }
            else:
                self.cookie = clist[int(random() * len(clist))]
                yield Request(response.url, cookies=self.cookie, callback=self.parse)
        # Parse return cookie
        new_cookie = self.parse_cookie(response.headers.getlist('Set-Cookie'))
        logger.debug(str("New cookie is:" + str(new_cookie)))
        # If we are using empty cookie, then save the new cookie
        if 0 == len(self.cookie):
            logger.debug(str("Adding new cookie"))
            self.cookie_pool.add(new_cookie)
            self.cookie_pool.dump()
        # or the new cookie is different from the old cookie
        elif not self.cookie_pool.has(new_cookie):
            logger.debug(str("Different cookie, old: {}, new: {}, replacing".format(str(self.cookie), str(new_cookie))))
            self.cookie_pool.remove(self.cookie)
            self.cookie_pool.add(new_cookie)
            self.cookie_pool.dump()
        articles = response.xpath('//div[@class="results"]/div[contains(@class, "wx-rb")]')
        for i in range(0, len(articles) - 1):
            url = response.urljoin(articles.xpath('//div/h4/a/@href')[i].extract())
            cover = hp().unescape(hp().unescape(articles.xpath('//div/a/img/@src')[i].extract())).replace('\\/', '/')
            date = datetime.fromtimestamp(int(articles.xpath('//div/div/span/script/text()')[i].extract()[22:-2])).strftime('%Y-%m-%d %H:%M:%S')
            digest = articles.xpath('//div[@class="txt-box"]/p')[i].extract()
            self.article_infos[url] = {
                'cover'  : cover,
                'date'   : date,
                'digest' : digest
            }
            yield Request(url, callback=self.parse_article)

    def parse_article(self, response):
        title  = response.xpath('//div[@id="page-content"]/div/h2/text()')[0].extract().strip()
        user   = response.xpath('//*[@id="post-user"]/text()')[0].extract()
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

    def parse_cookie(self, header_list):
        snuid = ""
        suid = ""
        for header in header_list:
            if 'SNUID' == header.split('=')[0]:
                snuid = header.split('=')[1].split(';')[0]
            if 'SUID' == header.split('=')[0]:
                suid = header.split('=')[1].split(';')[0]
        if "" == snuid:
            return self.cookie
        else:
            return self.cookie_pool.new(snuid, suid)
