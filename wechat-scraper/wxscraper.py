from wxspider import WeChatSpider
from scrapy.crawler import CrawlerProcess

class WeChatScraper:
    """
    WeChatScraper can search official articles and return data in Json format
    """
    results = []

    def process_item(self, item, spider):
        self.results.append(dict(item))

    def crawl(self, accounts):
        crawler = CrawlerProcess({
            'ITEM_PIPELINES'           : {'__main__.WeChatScraper' : 1},
            'LOG_ENABLED'              : False,
            'COOKIES_ENABLED'          : True,
            'RANDOMIZE_DOWNLOAD_DELAY' : True,
            'ACCOUNT_LIST'             : accounts
        })
        spider = WeChatSpider(accounts=accounts)
        crawler.crawl(spider)
        crawler.start()
        return sorted(self.results, key=lambda x:x[u'date'])

if __name__ == '__main__':
    import sys
    datas = WeChatScraper().crawl(sys.argv[1:])
    import json
    print json.dumps(datas, ensure_ascii=False).encode("utf8")
