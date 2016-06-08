import json
import logging
from random import random
from datetime import datetime
from scrapy import Spider, Request
from HTMLParser import HTMLParser as hp
from cookie import Cookie

class AccountSpider(Spider):
    """
    The AccountSpider class will use weixin.sogou.com to search the official
    accounts. And get the first ten article infomation of each official
    account.
    """
    name = 'weixin'
    article_infos = {}
    not_found = "Not Found"
    # Define cookie pool size to 5. At the first 5 queries, we'll use empty
    # cookie to query and save the return cookie in pool.
    cookie_pool_size = 5
    cookie_pool = Cookie()

    def start_requests(self):
        """
        Actually, it's better to use __init__ to pass the attributes. But I've
        tried and failed. So I use scrapy settings for a workaround.
        """
        # Get random start url
        random_start_urls = [
            "http://weixin.sogou.com/weixin?type=1&ie=utf8&_sug_=n&_sug_type_=&query=",
            "http://weixin.sogou.com/weixin?query="
        ]
        self.start_urls = map(lambda x: random_start_urls[int(random() * len(random_start_urls))] + x, self.settings.get('ACCOUNT_LIST'))

        for url in self.start_urls:
            # Get a random cookie
            clist = self.cookie_pool.get_cookies()
            if len(clist) < self.cookie_pool_size:
                self.cookie = {}
            else:
                self.cookie = clist[int(random() * len(clist))]
            yield Request(url, cookies=self.cookie, callback=self.parse)

    def parse(self, response):
        """
        Parse the result from the main search page and crawl into each result.
        """
        logger = logging.getLogger(response.url[-6:])
        logger.debug(str("Using cookie :" + str(self.cookie)))
        if "/antispider/" in response.url:
            self.cookie_pool.remove(self.cookie)   # This cookie is banned, remove it
            clist = self.cookie_pool.get_cookies() # Use a new cookie to query
            if 0 == len(clist):                    # If we run out of cookie, then our IP could be banned
                yield {
                    u"error": u"Seems our IP was banned. Caught by WeChat Antispider: {}".format(response.url),
                    u"date" : unicode(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                }
            else:
                self.cookie = clist[int(random() * len(clist))]
                yield Request(response.url, cookies=self.cookie, callback=self.parse)
        # Parse return cookie
        new_cookie = self.parse_cookie(response.headers.getlist('Set-Cookie'))
        logger.debug(str("New cookie is:" + str(new_cookie)))
        # If we are using empty cookie, then save the new cookie
        if 0 == len(self.cookie):
            logger.debug(str("Adding new cookie"))
            self.cookie_pool.add(new_cookie)
            self.cookie_pool.dump()
        # or the new cookie is different from the old cookie
        elif not self.cookie_pool.has(new_cookie):
            logger.debug(str("Different cookie, old: {}, new: {}, replacing".format(str(self.cookie), str(new_cookie))))
            self.cookie_pool.remove(self.cookie)
            self.cookie_pool.add(new_cookie)
            self.cookie_pool.dump()
        # only query first account
        account_url = response.urljoin(response.xpath('//div[@class="results mt7"]/div[contains(@class, "wx-rb")]/@href').extract_first())
        yield Request(account_url, callback=self.parse_account)

    def parse_account(self, response):
        """
        Parse the account page and crawl into each article.

        It's worth noting that this account page does not render HTML code from
        very beginning. It use JavaScript and a Json string to render the page
        dynamicly. So we use python-json module to parse the Json string.
        """
        nickname = response.xpath('//div/strong[contains(@class, "profile_nickname")]/text()').extract_first(default=self.not_found).strip()
        account  = response.xpath('//div/p[contains(@class, "profile_account")]/text()').extract_first(default=self.not_found).strip()
        msgJson  = response.xpath('//script[@type="text/javascript"]/text()')[2].re(r'var msgList = \'(.*)\'')[0]
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
        title  = response.xpath('//div[@id="page-content"]/div/h2/text()').extract_first(default=self.not_found).strip()
        user   = response.xpath('//*[@id="post-user"]/text()').extract_first(default=self.not_found).strip()
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

    def parse_cookie(self, header_list):
        snuid = ""
        suid = ""
        for header in header_list:
            if 'SNUID' == header.split('=')[0]:
                snuid = header.split('=')[1].split(';')[0]
            if 'SUID' == header.split('=')[0]:
                suid = header.split('=')[1].split(';')[0]
        if "" == snuid:
            return self.cookie
        else:
            return self.cookie_pool.new(snuid, suid)
