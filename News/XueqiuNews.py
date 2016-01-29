# coding=utf-8

import urllib2
import urllib
import cookielib
import json
import re
import time
from lxml import etree 
import chardet
import codecs
import logging
from pyExcelerator import *
import xlrd
import socket
import threading
import Queue
import os
from collections import OrderedDict
"""
Function: 爬取雪球网新闻链接v0.1
Author: KenziD

运行要求：
1. 安装处理工具包(pip install lxml pyExcelerator xlrd chardet)。
2. 本程序路径最好不要有中文。
3. 在控制台中运行 python XueqiuNews.py。
3. 程序运行结束将在输出文件夹NewsLink保存相关股票表格。表格中是此股票包含的新闻链接。
4. 运行过程中的日志信息保存在log文件夹内。级别为DEBUG级别。
5. 如果程序卡了，直接关掉。重新运行，程序会在NewsLink文件夹内自检已经爬过的股票，接着上面断掉的程序爬。
6. 命令行的日志信息为INFO级别，将INFO改为DEBUG可看到更多输出信息，便于调试程序。也可以在程序运行完成后直接在log日志中查看。

7. 修改了获取新闻链接的规则
8. 增加了自动重新获取空文件
"""

# 验证文件夹是否存在 不存在则创建
def checkDir(folder):
    if os.path.isdir(folder):
        pass
    else:
        os.mkdir(folder)

#将新闻链接放在NewsLink文件夹中
checkDir("NewsLinkText")



socket.setdefaulttimeout(10) #设置10秒后连接超时
format = '%Y-%m-%d-%H-%M-%S'
#用时间命名log日志
dt = time.strftime(format,time.localtime())
#使用logging库来Debug替代print
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 将日志放在log文件夹里
checkDir("log")


#写入文件的是DEBUG级别
fh = logging.FileHandler('log/'+dt+'.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

#在命令行的是INFO级别
ch = logging.StreamHandler()
#这里改成INFO就是INFO级别
#这里改成DEBUG就是DEBUG级别
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {
        'User-Agent': userAgent
}


# 时间戳转换函数
def timestamp_datetime(value):
    format = '%Y%m%d %H%M%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt

#获取新闻json
# http://xueqiu.com/statuses/stock_timeline.json?symbol_id=SZ002161&count=15&page=1&source=自选股新闻
class JsonGetter(object):
    """docstring for JsonGetter"""


    #先打开雪球网主页获取并保存cookie，后面的程序都使用这个cookie
    def __init__(self):
        filename = 'cookie.txt'
        cookie = cookielib.MozillaCookieJar(filename)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        urllib2.install_opener(opener)
        url = 'http://xueqiu.com/'
        req = urllib2.Request(url, headers=headers)
        r = urllib2.urlopen(req)
        cookie.save(ignore_discard=True, ignore_expires=True)
        req = urllib2.Request(url, headers=headers)

    #拼接完整的json链接
    def news_url_param(self,url,stockId, count, page):
        param = {}
        param['symbol_id'] = str(stockId)
        param['count'] = str(count)
        param['page'] = str(page)
        param['source'] = '自选股新闻'
        data = urllib.urlencode(param)
        # 得到完整的GET请求urls
        geturl = url + "?" + data
        logger.debug(geturl)
        return geturl

    #通过上面拼接好的链接获取新闻json
    def get_News_json(self,stockId,count, page):
        url = 'http://xueqiu.com/statuses/stock_timeline.json'
        geturl = self.news_url_param(url,stockId,count, page)
        try:
            req = urllib2.Request(geturl, headers=headers)
            response = urllib2.urlopen(req,timeout = 10)
            # raw-html(in this case is json)
            html_json = response.read().decode("utf-8")
            return html_json
        except socket.timeout as e:
            logger.debug(type(e))    #catched 
            return None
        except:
            return None

#写NewsLink xsl
class XslWriter(object):
    """docstring for XslWriter"""  


    #创建表格文件 
    def __init__(self):
        self.w = Workbook() 
        self.ws = self.w.add_sheet('Hey, XueqiuNews')

    #写表头
    def creat(self):
        self.ws.write(0,0,u'StockName')
        self.ws.write(0,1,u'Code')
        self.ws.write(0,2,u'Date')
        self.ws.write(0,3,u'Time')
        self.ws.write(0,4,u'Forward')
        self.ws.write(0,5,u'Comment')
        self.ws.write(0,6,u'Title')
        self.ws.write(0,7,u'NewsLink')
        self.ws.write(0,8,u'Text')
        self.ws.write(0,9,u'MessageId')
        self.ws.write(0,10,u'MessageLink')
        self.ws.write(0,11,u'TimeStamp')

    #写表格前两列
    def writeStockIdName(self,row,stockId,stockName):
        self.ws.write(row,0,stockName)
        self.ws.write(row,1,stockId)

    #写表格主体
    def write(self,row,YMD,TIME,retweet_count,reply_count,title,targetNewsLink,text,message_id,target_url,timeStamp):
    # def write(self,row,YMD,TIME,retweet_count,reply_count,title,targetNewsLink):
        self.ws.write(row,2,YMD)
        self.ws.write(row,3,TIME)
        self.ws.write(row,4,retweet_count)
        self.ws.write(row,5,reply_count)
        self.ws.write(row,6,title)
        self.ws.write(row,7,targetNewsLink)
        self.ws.write(row,8,text)
        self.ws.write(row,9,message_id)
        self.ws.write(row,10,target_url)
        self.ws.write(row,11,timeStamp)

    # 保存表格
    def close(self,name):
        self.w.save('%s/%s.xls'%('NewsLinkText',name))     #保存

#读stock表格
def readXls():
    # Open the workbook
    xl_workbook = xlrd.open_workbook("source.xls")
    sheet_names = xl_workbook.sheet_names()
    xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
    nrows = xl_sheet.nrows
    ncols = xl_sheet.ncols
    stockid_list = []
    stockName_list = []
    #提取第一列ID
    for cell_obj in xl_sheet.col(0):
        stockid_list.append(cell_obj.value)
    #删除前两行
    del stockid_list[0:2]
    #提取第二列中文名字
    for cell_obj in xl_sheet.col(1):
        stockName_list.append(cell_obj.value)
    del stockName_list[0:2]
    #提取第三列辨别深圳还是上海
    code = []
    for cell_obj in xl_sheet.col(2):
        # if u"深圳" in cell_obj.value or u"上海A6" in cell_obj.value:
        #     code.append('SZ')
        # elif u"上海" in cell_obj.value:
        #     code.append('SH')
        if u"深圳A" in cell_obj.value:
            code.append('SZ')
        elif u"上海A" in cell_obj.value:
            code.append('SH')
    stockid_list = [''.join(item) for item in zip(code,stockid_list)]
    # {"大东海B":ZH200613}
    stockNameId_dict = OrderedDict(zip(stockName_list,stockid_list))
    fn = os.listdir('NewsLinkText')
    for k,v in stockNameId_dict.items():
        if any(v in s for s in fn):
                stockNameId_dict.pop(k)
    return stockNameId_dict

class JsonParser():


    # 每一个股票都创建一个表格
    def __init__(self):
        self.xslWriter = XslWriter()
        self.xslWriter.creat()
        self.outsideRetry = 0

    # http://xueqiu.com/S/SZ002161/63362440每个新闻都有一个单独的id页面
    def get_target_url(self,target):
        target_url = "http://xueqiu.com"+str(target)
        return target_url

    # 正则匹配 从json里获取新闻的链接
    def get_news_link(self,newsText):
        pattern = re.compile(r'.*?href="(.*?)"')
        allMatch = pattern.findall(newsText)
        # linkTypePattern = re.compile(r'\.(\w+)')
        afterPattern = re.compile(r'(\.cn|\.com)\/(\w+)')
        logger.debug( "Matching news link.......")
        for link in allMatch:
            # linkType = linkTypePattern.findall(link)
            # if linkType[-1]=="html" or linkType[-1]=="shtml" or linkType[-1]=="htm" or linkType[-1]=="pdf":
            if ".html" in link or ".shtml" in link or ".pdf" in link or ".htm" in link:
                logger.debug( "Matching successful")
                logger.debug(link)
                return link
        for link in allMatch:
            match = afterPattern.search(link)
            if match:
                logger.debug( "No pdf/html/shtml/htm.But something after domain.Matching successful")
                logger.debug(link)
                return link
        logger.debug( "No news link match.")
        return None

    # 主程序
    def parse_process(self,stockId,stockName):
        while True:
            # print("###################BEGIN %s####################" %stockName)
            logger.info(u"###################BEGIN %s####################" %stockName)
            
            # global row
            row=1
            logger.debug("stockName %s" % stockName)
            logger.debug("stockId %s" %stockId)
            self.xslWriter.writeStockIdName(row,stockId,stockName)
            #实例化
            jsonGetter = JsonGetter()
            news_json = jsonGetter.get_News_json(stockId,50,1)
            if news_json is None:
                # print("fail to get %s json" % stockName)
                logger.info(u"fail to get %s json" % stockName)
                if self.outsideRetry>0:
                    # print("outsideRetry %s to get %s json" % (self.outsideRetry,stockName))
                    logger.info(u"outsideRetry %s to get %s json" % (self.outsideRetry,stockName))
                if (self.outsideRetry == 4):
                    self.outsideRetry = 0
                    # print("########################END %s####################" %stockName)
                    logger.info(u"########################END %s####################" %stockName)
                    self.xslWriter.close(stockId)
                    break
                self.outsideRetry = self.outsideRetry + 1
                continue
            decode_news_json = json.loads(news_json)
            max_page = decode_news_json['maxPage']
            if max_page == 0:
                # print("##############max_page==0##########END %s####################" %stockName)
                logger.info(u"##############max_page==0##########END %s####################" %stockName)
                self.xslWriter.close(stockId)
                break
            for pageIndex in range(1,max_page+1):
                retry = 0
                while True:
                    if(retry>0):
                        # print("retry %s to get json %s page %s "%(retry,stockName,pageIndex))
                        logger.info(u"retry %s to get json %s page %s "%(retry,stockName,pageIndex))
                    if (retry == 50):
                        retry = 0
                        # print("########################END %s####################" %stockName)
                        logger.info(u"########################END %s####################" %stockName)
                        self.xslWriter.close(stockId)
                        break
                    news_json = jsonGetter.get_News_json(stockId,50, pageIndex)
                    if news_json is None:
                        # print("fail to get json %s page %s" % (stockName,pageIndex))
                        logger.info(u"fail to get json %s page %s" % (stockName,pageIndex))
                        retry = retry+1
                        continue
                    decode_news_json = json.loads(news_json)
                    # print("success to get json %s page %s" %(stockName,pageIndex))
                    logger.info(u"success to get json %s page %s" %(stockName,pageIndex))
                    for item in decode_news_json['list']:
                        title = item['title']
                        logger.debug( title)
                        if title is None:
                            title = "None"
                        timeStamp = item['created_at']
                        # logger.debug(timeStamp)
                        formateTime = timestamp_datetime(long(str(timeStamp)[0:10]))
                        # logger.debug(formateTime)
                        YMD = formateTime[0:8]
                        # logger.debug(YMD)
                        TIME = formateTime[9:15]

                        # logger.debug(TIME)
                        text = item['text']
                        if text is None:
                            text = "None"
                        targetNewsLink = self.get_news_link(text)
                        if targetNewsLink is None:
                            targetNewsLink = "None"
                        retweet_count = item['retweet_count']
                        # logger.debug(retweet_count)
                        reply_count = item['reply_count']
                        # logger.debug(reply_count)
                        message_id = item['id']
                        target = item['target']
                        target_url = self.get_target_url(target)
                        self.xslWriter.write(row,YMD,TIME,retweet_count,reply_count,title,targetNewsLink,text,message_id,target_url,str(timeStamp))
                        # self.xslWriter.write(row,YMD,TIME,retweet_count,reply_count,title,targetNewsLink,message_id,target_url,timeStamp)
                        row = row+1
                    break
            # print("########################END %s####################" %stockName)
            logger.info(u"########################END %s####################" %stockName)
            self.xslWriter.close(stockId)
            break

class ParseStockId(object):


    """docstring for getStockId"""
    def __init__(self):
        self.stockNameId_dict =  readXls()
        self.tsk = []

    def passID(self):
        queue = Queue.Queue()
        #开启5个线程
        for i in range(5):
            t = MyThread(i,"Threading%s"%i,queue,self.stockNameId_dict)
            #线程守护
            t.setDaemon(True)
            t.start()
        #将股票ID放入队列
        for i in self.stockNameId_dict:
            queue.put(i)
        #队列中的元素要等上一个被取出后才能继续下一个线程
        queue.join()

#继承Threading类
class MyThread(threading.Thread):
    """docstring for MyThread"""


    def __init__(self, thread_id, name,queue,dic) :
        super(MyThread, self).__init__()  #调用父类的构造函数 
        # self.stockNameId_dict =  readXls()
        self.stockNameId_dict = dic
        self.thread_id = thread_id
        self.name = name
        self.queue = queue

    def run(self) :
        while True:
            logging.debug( "Starting " + self.name)
            stockName  = self.queue.get()
            stockId = self.stockNameId_dict[stockName]
            jsonParser = JsonParser()
            jsonParser.parse_process(stockId,stockName)
            self.queue.task_done()
            logging.debug( "Exiting " + self.name)

if __name__ == '__main__':
    new = 0
    old = 0
    fileEmpty = []
    fileEmpty_old = []
    i = 0
    while True:
        parseStockId = ParseStockId()
        parseStockId.passID()
        fileEmpty = []
        fn = os.listdir('.\NewsLinkText')
        for filename in fn:
            if os.stat('NewsLinkText/%s'%filename).st_size/1024.0<7:
                # print ('empty file is %s'%filename)
                logger.info(u'empty file is %s'%filename)
                fileEmpty.append(filename)
        if len(fileEmpty) == len(fileEmpty_old):
            # print( u"与上一次产生的空文件数目一致，程序结束")
            logger.info( u"与上一次产生的空文件数目一致，程序结束")
            break
        for filename in fileEmpty:
            # print( "remove %s"%filename)
            logger.info( u"remove %s"%filename)
            os.remove('NewsLinkText/%s'%filename)
        fileEmpty_old = fileEmpty
        # print( "AGAIN %s"%i)
        logger.info( u"AGAIN %s"%i)
        i = i+1
