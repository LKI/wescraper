from wxspider import WeixinSpider
from scrapy.crawler import CrawlerProcess

class WeixinScraper:
    """
    WeixinScraper can search official articles and return data in Json format
    """
    results = []

    def process_item(self, item, spider):
        self.results.append(dict(item))

    def crawl(self, accounts):
        crawler = CrawlerProcess({
            'ITEM_PIPELINES'           : {'__main__.WeixinScraper' : 1},
            'LOG_ENABLED'              : False,
            'COOKIES_ENABLED'          : True,
            'RANDOMIZE_DOWNLOAD_DELAY' : True,
            'ACCOUNT_LIST'             : accounts
        })
        spider = WeixinSpider(accounts=accounts)
        crawler.crawl(spider)
        crawler.start()
        return self.results

if __name__ == '__main__':
    import sys
    datas = WeixinScraper().crawl(sys.argv[1:])
    print (u"[" + u', '.join(map(lambda data: u'{' + u', '.join(map(lambda key: u"\"{}\": \"{}\"".format(key, data[key].replace(u"\"", u"\\\"")), data.keys())) + u'}', datas)) + u"]").encode('utf8')
