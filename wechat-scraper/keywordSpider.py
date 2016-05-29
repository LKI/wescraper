import json
from random import random
from datetime import datetime
from scrapy import Spider, Request
from HTMLParser import HTMLParser as hp

class KeywordSpider(Spider):
    name = 'weixin'
    article_infos = {}

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
            yield self.make_requests_from_url(url)

    def parse(self, response):
        if "/antispider/" in response.url:
            yield {
                u"error": u"Caught by WeChat Antispider: {}".format(response.url),
                u"date" : unicode(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            }
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
