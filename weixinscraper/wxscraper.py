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
        return sorted(self.results, key=lambda x:x[u'date'])

if __name__ == '__main__':
    import sys
    datas = WeixinScraper().crawl(sys.argv[1:])
    import json
    print json.dumps(datas, ensure_ascii=False).encode("utf8")
