import json
from datetime import datetime
from scrapy import Spider, Request
from HTMLParser import HTMLParser as hp

class WeixinSpider(Spider):
    """
    The WeixinSpider class will use weixin.sogou.com to search the official
    accounts. And get the first ten article infomation of each official
    account.
    """
    name = 'weixin'
    article_infos = {}

    def start_requests(self):
        """
        Actually, it's better to use __init__ to pass the attributes. But I've
        tried and failed. So I use scrapy settings for a workaround.
        """
        self.start_urls = map(lambda x: "http://weixin.sogou.com/weixin?query=" + x, self.settings.get('ACCOUNT_LIST'))
        for url in self.start_urls:
            yield self.make_requests_from_url(url)


    def parse(self, response):
        """
        Parse the result from the main search page and crawl into each result.
        """
        for href in response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href'):
            account_url = response.urljoin(href.extract())
            yield Request(account_url, callback=self.parse_account)

    def parse_account(self, response):
        """
        Parse the account page and crawl into each article.

        It's worth noting that this account page does not render HTML code from
        very beginning. It use JavaScript and a Json string to render the page
        dynamicly. So we use python-json module to parse the Json string.
        """
        nickname = response.xpath('//div/strong[contains(@class, "profile_nickname")]/text()')[0].extract().strip().encode('utf-8')
        account  = response.xpath('//div/p[contains(@class, "profile_account")]/text()')[0].extract().strip().encode('utf-8')
        msgJson  = response.xpath('//script[@type="text/javascript"]/text()')[2].re(r'var msgList = \'(.*)\'')[0].encode('utf-8')
        articles = json.loads(msgJson)['list']
        for article in articles:
            appinfo = article['app_msg_ext_info']
            cominfo = article['comm_msg_info']
            # Unescape the HTML tags twice
            url  = "http://mp.weixin.qq.com/s?" + hp().unescape(hp().unescape(appinfo['content_url'][4:]))
            self.article_infos[url] = {
                'cover'  : hp().unescape(hp().unescape(appinfo['cover'])).replace('\\/', '/'),
                'date'   : datetime.fromtimestamp(int(cominfo['datetime'])).strftime('%Y-%m-%d %H:%M:%S'),
                'digest' : appinfo['digest']
            }
            yield Request(url, callback=self.parse_article)

    def parse_article(self, response):
        """
        Finally we've got into the article page. Since response.url is generated
        dynamically, we need to get the permenant URL of the article.
        """
        title  = response.xpath('//div[@id="page-content"]/div/h2/text()')[0].extract().strip().encode('utf-8')
        script = response.xpath('//script[contains(text(), "var biz =")]')[0]
        params = ['biz', 'sn', 'mid']
        values = map(lambda x:x + '=' + script.re('var ' + x + ' = .*"([^"]*)";')[0], params)
        url    = "http://mp.weixin.qq.com/s?" + reduce(lambda x,y:x+'&'+y, values)
        date   = response.xpath('//*[@id="post-date"]')[0].extract()
        html   = str.join("\n", response.xpath('//*[@id="js_content"]').extract()).encode('utf-8').strip()
        info   = self.article_infos[response.url]
        yield {
            'title'   : title,
            'url'     : url,
            'date'    : info['date'],
            'cover'   : info['cover'],
            'digest'  : info['digest'],
            'content' : html
        }
