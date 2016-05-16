import scrapy
import json

class WeixinSpider(scrapy.Spider):
    name = 'weixin'
    accounts = open('accounts.list', 'r').readlines()
    start_urls = map(lambda x: "http://weixin.sogou.com/weixin?type=1&query=" + x, accounts)

    def parse(self, response):
        for href in response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href'):
            account_url = response.urljoin(href.extract())
            yield scrapy.Request(account_url, callback=self.parse_account)

    def parse_account(self, response):
        nickname = response.xpath('//div/strong[contains(@class, "profile_nickname")]/text()')[0].extract().strip().encode('utf-8')
        account  = response.xpath('//div/p[contains(@class, "profile_account")]/text()')[0].extract().strip().encode('utf-8')
        msgJson  = response.xpath('//script[@type="text/javascript"]/text()')[2].re(r'var msgList = \'(.*)\'')[0]
        articles = json.loads(msgJson)[u'list']
        for article in articles:
            info = article[u'app_msg_ext_info']
            yield {
                'nickname': nickname,
                'account':  account,
                'title':    info[u'title'],
                'cover':    info[u'cover'],
                'url':      info[u'content_url'],
                'digest':   info[u'digest']
            }
