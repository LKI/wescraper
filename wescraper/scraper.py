# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from scrapy.crawler import CrawlerProcess

import config
from wespider import WeSpider


class WeScraper:
    """
    WeScraper can search official articles and return data in Json format
    """

    def __init__(self):
        pass

    results = []

    def process_item(self, item):
        self.results.append(dict(item))

    def crawl_key(self, search_type, accounts):
        crawler = CrawlerProcess({
            'ITEM_PIPELINES': {'__main__.WeScraper': 1},
            'COOKIES_ENABLED': True,
            'RANDOMIZE_DOWNLOAD_DELAY': True,
            'DUPEFILTER_CLASS': 'scrapy.dupefilter.BaseDupeFilter',
            'ACCOUNT_LIST': accounts,
            'SEARCH_TYPE': search_type
        })
        spider = WeSpider()
        crawler.crawl(spider)
        crawler.start()
        return sorted(self.results, key=lambda x: x[u'date'], reverse=True)


if __name__ == '__main__':
    import sys

    data = []
    if len(sys.argv) > 1 and sys.argv[1] in config.types:
        data = WeScraper().crawl_key(sys.argv[1], sys.argv[2:])
        import json

        print json.dumps(data, ensure_ascii=False).encode('utf8')
    else:
        print 'Search type can only be {}'.format(str(config.types))
