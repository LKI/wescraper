# Weixin Scraper

本工具使用Python库[scrapy][scrapy]以搜索微信公众号文章。

# 使用教程

首先，你得有Python和[scrapy][scrapy]

Linux:

```
    git clone https://github.com/LKI/weixinscraper.git && cd weixinscraper && ./run
```

Windows:

```
    git clone https://github.com/LKI/weixinscraper.git
    cd weixinscraper
    scrapy runspider spider/spider.py -o weixin.json
```

# 详细说明

* 本工具完全依赖[搜狗微信搜索][sougou]抓取文章，所以万一以后搜狗微信改了的话…

* 把你想搜的公众号添加到[accounts.list](accounts.list)就可以搜到它们的最新十篇文章。

* [Python大法好！][dive-into-python] :wink:

![Python is Great][python]

# 版权/免责

代码版权归GitHub原作者 @LKI 所有。
严禁用于商业用途，其它转载/Fork随意。

[scrapy]: https://github.com/scrapy/scrapy
[sougou]: http://weixin.sogou.com/
[dive-into-python]: http://www.diveintopython.net/
[python]: http://3.im.guokr.com/_mdg6v4MaUReoxYx0i0viv8HfkFRHtvLIOM_D4rfeqtAAgAAjQEAAEpQ.jpg
