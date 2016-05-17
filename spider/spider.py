import scrapy
import json
import os
import shutil
from HTMLParser import HTMLParser as hp

class WeixinSpider(scrapy.Spider):
    result_folder = 'result'

    # Scrapy related variables
    name = 'weixin'
    accounts = open('accounts.list', 'r').readlines()
    start_urls = map(lambda x: "http://weixin.sogou.com/weixin?type=1&query=" + x, accounts)

    # Re-create result folder
    if os.path.exists(result_folder):
        shutil.rmtree(result_folder)
    os.makedirs(result_folder)

    def parse(self, response):
        for href in response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href'):
            account_url = response.urljoin(href.extract())
            yield scrapy.Request(account_url, callback=self.parse_account)

    def parse_account(self, response):
        nickname = response.xpath('//div/strong[contains(@class, "profile_nickname")]/text()')[0].extract().strip().encode('utf-8')
        account  = response.xpath('//div/p[contains(@class, "profile_account")]/text()')[0].extract().strip().encode('utf-8')
        msgJson  = response.xpath('//script[@type="text/javascript"]/text()')[2].re(r'var msgList = \'(.*)\'')[0].encode('utf-8')
        articles = json.loads(msgJson)[u'list']
        for article in articles:
            info = article[u'app_msg_ext_info']
            url  = "http://mp.weixin.qq.com/s?" + hp().unescape(hp().unescape(info[u'content_url'][4:]))
            yield scrapy.Request(url, callback=self.parse_article)

    def parse_article(self, response):
        title  = response.xpath('//div[@id="page-content"]/div/h2/text()')[0].extract().strip().encode('utf-8')
        script = response.xpath('//script[contains(text(), "var biz =")]')[0]
        params = ['biz', 'sn', 'mid', 'idx']
        values = map(lambda x:x + '=' + script.re('var ' + x + ' = .*"([^"]*)";')[0], params)
        url    = "http://mp.weixin.qq.com/s?" + reduce(lambda x,y:x+'&'+y, values)
        content = str.join("\n", response.xpath('//*[@id="js_content"]//text()').extract()).encode('utf-8').strip()
        with open(os.path.join(self.result_folder, title), 'w') as article:
            article.write("[" + title + "]")
            article.write("(" + url + ")")
            article.write("\n")
            article.write(content)
        yield {
            'title': title,
            'url'  : url,
            'content': content
        }
