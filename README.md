# Weixin Scraper

本工具使用Python2.7和[scrapy][scrapy]来搜索微信公众号文章。

# 使用教程

```
pip install tornado
pip install scrapy
python weixinscraper/server.py
```

前两条命令安装tornado和scrapy，然后最后一条命令跑一个本地server

然后你就可以通过`http://localhost/account1/account2/account3...`
来获取微信公众号文章列表了。

假如希望通过Python Code内部调用可以参见[server.py][server-py]源码

（代码很短，应该比较好懂）

# 详细说明

* 因为Python2的默认Encoding是ASCII，所以抓取中文会被转译。但是不影响JSON数据本身。

* 本工具完全依赖[搜狗微信搜索][sogou]抓取文章，假如搜狗微信搜索接口什么的变了可能就会抓取失败。

* [Python大法好！][dive-into-python] :wink:

# 已知问题

* [server.py][server-py]只能查询一次公众号，后续出现500错误。
这是因为scrapy中某一项服务在首次查询中被关闭了，正在修复中。

# 版权/免责

代码版权归GitHub原作者 @LKI 所有。
严禁用于商业用途，其它转载/Fork随意。

[scrapy]: https://github.com/scrapy/scrapy
[server-py]: /weixinscraper/server.py
[sogou]:  http://weixin.sogou.com/
[dive-into-python]: http://www.diveintopython.net/
