# Weixin Scraper

本工具使用Python2.7和[scrapy][scrapy]来搜索微信公众号文章。

# 使用教程

```
pip install tornado
pip install scrapy
python weixinscraper/weixinscraper.py liriansu
```

前两条命令安装tornado和scrapy，然后最后一条命令查询和`liriansu`相关的公众号。

或者你也可以跑`python weixinscraper/server.py`
然后通过`http://localhost/account1/account2/account3...`
来获取微信公众号文章列表了。

假如希望通过Python Code内部调用可以参见[wxscraper.py][scraper-py]源码

（代码很短，应该比较好懂）

# 详细说明

* 本工具没有考虑反爬虫的问题，解决方案可以参考[Scrapy: Avoiding getting banned][anti]

* 本工具完全依赖[搜狗微信搜索][sogou]抓取文章，假如搜狗微信搜索接口什么的变了可能就会抓取失败。

* [Python大法好！][dive-into-python] :wink:

# 版权/免责

代码版权归GitHub原作者 @LKI 所有。
严禁用于商业用途，其它转载/Fork随意。

[scrapy]: https://github.com/scrapy/scrapy
[scraper-py]: /weixinscraper/wxscraper.py
[anti]: http://doc.scrapy.org/en/latest/topics/practices.html#avoiding-getting-banned
[sogou]:  http://weixin.sogou.com/
[dive-into-python]: http://www.diveintopython.net/
