import scrapy

class WeixinSpider(scrapy.Spider):
    name = 'weixin'
    accounts = open('accounts.list', 'r').readlines()
    start_urls = map(lambda x: "http://weixin.sogou.com/weixin?type=1&query=" + x, accounts)

    def parse(self, response):
        for href in response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href'):
            yield {
                'href': href.extract()
            }
