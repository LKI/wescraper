# WeScraper (WEchat SCRAPER)

本工具使用Python2.7和[scrapy][scrapy]来搜索微信公众号文章。

# 使用教程

## 命令行直接查询

安装Scrapy，直接查询。

```
pip install scrapy
python wescraper/scraper.py account liriansu > liriansu.json # 查询liriansu相关的公众号
python wescraper/scraper.py key-day liriansu > liriansu.json # 查询liriansu相关的文章（一天内）
```

## Web Server查询

安装Scrapy与Tornado，通过本地server查询：

```
pip install scrapy tornado
python wescraper/server.py
```

在server起来以后就可以通过`http://localhost/account/foo/bar/baz...`
来获取微信公众号文章列表了。

或者可以通过`http://localhost/key-year/foo/bar/baz...`
以关键字来查询公众号文章。

## Python Code调用

参见[scraper.py][scraper-py]源码

# 详细说明

* 一些可配置的参数见[config.py][config-py]

* 本工具没有考虑反爬虫的问题，解决方案可以参考[Scrapy: Avoiding getting banned][anti]
（一般而言，换IP就可以解决问题了）

* [cookie.py][cookie-py]内维护了一个Cookie池，会在n个Cookie中随机选取来访问，假如发现被ban了就会换一个Cookie。

* 欢迎在本代码基础上修改，记得跑一下单元测试噢：`python wescraper/test/test.py`

* 本工具完全依赖[搜狗微信搜索][sogou]抓取文章，假如搜狗微信搜索接口什么的变了可能就会抓取失败。

* [Python大法好！][dive-into-python] :wink:

# 版权/免责

代码版权归GitHub原作者 @LKI 所有。
严禁用于商业用途，其它转载/Fork随意。

[scrapy]: https://github.com/scrapy/scrapy
[scraper-py]: /wescraper/scraper.py
[config-py]: /wescraper/config.py
[anti]: http://doc.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned
[cookie-py]: /wescraper/cookie.py
[sogou]:  http://weixin.sogou.com/
[dive-into-python]: http://www.diveintopython.net/
