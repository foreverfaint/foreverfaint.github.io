---
title: 在Scrapy中使用cookie
date: 2015-12-11T15:27:56+08:00
category:
    - Programming
tags:
    - Python
---

Python有一个很出色的爬虫包[scrapy](http://scrapy.org/)，架构清晰，设计精巧，能想到的爬虫工具需要的定制化点都有对应的扩展机制。 大部分网站都使用cookie来记录访问用户的识别信息。每个请求都会把用户识别信息带回到服务器，帮助后台程序识别独立用户，这样可以进行鉴权，反爬，限流等很多的操作。所以对于爬虫来说，如何模拟和使用cookie“欺骗”服务器，是十分重要的一步。本文就介绍如何在scrapy中使用cookie技术。

<!--more--> 

scrapy的cookie操作通过download middleware插件实现。具体的类名称是[CookisMiddleware](http://doc.scrapy.org/en/latest/topics/downloader-middleware.html#module-scrapy.downloadermiddlewares.cookies)。如果每个request维护一个独立的cookie session，只需按官方文档示例创建request即可（settings文件中要设置COOKIES_ENABLED为True）：

```python
for i, url in enumerate(urls):
    yield scrapy.Request("http://www.example.com", meta={'cookiejar': i}, callback=self.parse_page)
```

如果需要在所有的request间共享cookie，则可以按如下操作：

```python
for url in urls:
    yield scrapy.Request("http://www.example.com", meta={'cookiejar': 0}, callback=self.parse_page)
```
所有request都使用0号cookiejar。启用cookie后，scrapy既会从cookiejar中读取cookie，并设置到request header中。也会将response中，服务器写回的cookie写到cookiejar中。

一种常见情况是:

1.  首先发送一个不带cookie的request到目标url A
2.  目标服务器发现该请求不带cookie，则302该请求到一个授权页面B
3.  授权页面B写会授权cookie给我们，同时再次302我们的请求返回到url A。这次新请求会带着cookie到达服务器，成功获得url A对应的页面

scrapy自动支持redirect，所以一切看上去那么美好，启用cookie后，上述过程自动完成，我们获得需要的url A的内容。可事实上，你会发现第3步并没有执行！这是因为scrapy支持dupfilter机制，在一次运行中已经抓过的url不会再次抓取。虽然第一次抓取url A，我们只是被redirect，但是scrapy也会认为我们访问过url A，不会再次发送带cookie的第三步请求。这部分逻辑的实现请参看[Scrapy RFPDupeFilter](https://github.com/scrapy/scrapy/blob/master/scrapy/dupefilters.py)

```python
def request_seen(self, request):
    fp = self.request_fingerprint(request)
    if fp in self.fingerprints:
        return True
    self.fingerprints.add(fp)
    if self.file:
        self.file.write(fp + os.linesep)

def request_fingerprint(self, request):
    return request_fingerprint(request)
```

fingerprint方法确定一个url的signature，用来去重。查看[request_fingerprint](https://github.com/scrapy/scrapy/blob/master/scrapy/utils/request.py)后发现该方法接受一个include_headers参数（list类型），可以指定header中的哪些key需要计算到fingerprint中。

```python
def request_fingerprint(request, include_headers=None):
    """
    Return the request fingerprint.
    The request fingerprint is a hash that uniquely identifies the resource the
    request points to. For example, take the following two urls:
    http://www.example.com/query?id=111&cat=222
    http://www.example.com/query?cat=222&id=111
    Even though those are two different URLs both point to the same resource
    and are equivalent (ie. they should return the same response).
    Another example are cookies used to store session ids. Suppose the
    following page is only accesible to authenticated users:
    http://www.example.com/members/offers.html
    Lot of sites use a cookie to store the session id, which adds a random
    component to the HTTP Request and thus should be ignored when calculating
    the fingerprint.
    For this reason, request headers are ignored by default when calculating
    the fingeprint. If you want to include specific headers use the
    include_headers argument, which is a list of Request headers to include.
    """
    if include_headers:
        include_headers = tuple(to_bytes(h.lower())
                                for h in sorted(include_headers))
    cache = _fingerprint_cache.setdefault(request, {})
    if include_headers not in cache:
        fp = hashlib.sha1()
        fp.update(to_bytes(request.method))
        fp.update(to_bytes(canonicalize_url(request.url)))
        fp.update(request.body or b'')
        if include_headers:
            for hdr in include_headers:
                if hdr in request.headers:
                    fp.update(hdr)
                    for v in request.headers.getlist(hdr):
                        fp.update(v)
        cache[include_headers] = fp.hexdigest()
    return cache[include_headers]
```

可惜的是scrapy并没有提供一个setting开关用于在配置文件中指定如何计算fingerprint，所以我们要实现一个dupfilter子类完成将cookie加入fingerprint的逻辑

```python
class CookieRFPDupeFilter(RFPDupeFilter):
    def __init__(self, path=None, debug=False):
        super(CookieRFPDupeFilter, self).__init__(path, debug)

    def request_fingerprint(self, request):
        return request_fingerprint(request, include_headers=['Cookie'])
```

最后在setting中添加使用新dupfilter的设置，跳转+cookie的问题得到完美解决。

```python
DUPEFILTER_CLASS = 'scrapy_malong.dupfilters.CookieRFPDupeFilter'
```