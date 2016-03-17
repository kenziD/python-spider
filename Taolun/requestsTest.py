#coding=utf-8
import requests
userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {
    'User-Agent': userAgent
    # "Accept-Encoding":"gzip,deflate"
}

url = "http://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SZ002161&hl=0&source=user&sort=time&page=1"
# class myrequests(object):
#     """docstring for requests"""
#     @staticmethod
#     def get(url,timeout,headers,retry=10):
#         for i in xrange(retry):
#             r = requests.get(url,timeout=timeout,headers = headers)
#             html = r.content
#             print r.status_code
#             if r.status_code != 404:
#                 return r
#         return None
class Myrequests(object):
    """docstring for requests"""
    def __init__(self):
        url = 'http://xueqiu.com/'
        s = requests.Session()
        r = s.get(url,headers = headers)
        print s
        #s 中含有cookie
        self.s = s
    # @staticmethod
    def get(self,url,timeout,headers,retry=10):
        for i in xrange(retry):
            r = self.s.get(url,timeout=timeout,headers = headers)
            html = r.content
            print r.status_code
            if r.status_code == 404:
                return r
        return None
myrequests = Myrequests()
r=myrequests.get(url,timeout=6,headers = headers)
if r:
    html = r.content
    # print html


