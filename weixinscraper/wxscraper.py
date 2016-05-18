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
            'ITEM_PIPELINES' : {'__main__.WeixinScraper': 1},
            'ACCOUNT_LIST'   : accounts
        })
        spider = WeixinSpider(accounts=accounts)
        crawler.crawl(spider)
        crawler.start()
        return self.results
