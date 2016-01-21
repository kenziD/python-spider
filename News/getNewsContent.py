# coding=utf-8
import urllib2
import requests
import re
import time
from lxml import etree
import chardet
import codecs
import logging
import xlrd
import socket
import threading
import Queue
import os
import sys
from collections import OrderedDict

# 验证文件夹是否存在 不存在则创建
def checkDir(folder):
    if os.path.isdir(folder):
        pass
    else:
        os.mkdir(folder)

format = '%Y-%m-%d-%H-%M-%S'

# 使用logging库来Debug替代print
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
checkDir('log')

# 在命令行的是INFO级别
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
#如果使用了reqeusts库
logging.getLogger("requests").setLevel(logging.WARNING)

index = 1
fail = 1
success = 1


# 读某股票的xls文件 把xls整合成字典
# 格式：{"link":["title","text"],}
def read(fileName):
    xl_workbook = xlrd.open_workbook("NewsLinkText/%s.xls"%fileName)
    sheet_names = xl_workbook.sheet_names()
    xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
    linkList=[]
    titleList = []
    textList = []
    timeList = []
    idList = []
    for cell_obj in xl_sheet.col(6):
        titleList.append(cell_obj.value)
    del titleList[0:1]
    for cell_obj in xl_sheet.col(7):
        linkList.append(cell_obj.value)
    del linkList[0:1]
    for cell_obj in xl_sheet.col(8):
        textList.append(cell_obj.value)
    del textList[0:1]
    for cell_obj in xl_sheet.col(11):
        timeList.append(cell_obj.value)
    del timeList[0:1]
    for cell_obj in xl_sheet.col(9):
        idList.append(cell_obj.value)
    del idList[0:1]
    linkTitle_dict = OrderedDict(zip(linkList,titleList))
    linkText_dict = OrderedDict(zip(linkList,textList))
    linkTime_dict = OrderedDict(zip(linkList,timeList))
    linkId_dict = OrderedDict(zip(linkList,idList))
    link_TitleTextIdTime = OrderedDict(((key, [linkTitle_dict[key], linkText_dict[key],linkId_dict[key],linkTime_dict[key]]) for key in linkText_dict))
    return link_TitleTextIdTime


# def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
#   try:               # so on top of all there's this workaround:
#     return zlib.decompress(data, -zlib.MAX_WBITS)
#   except zlib.error:
#     return zlib.decompress(data)


# 有一些链接是.pdf
def getPdf(url,folderName,timeStamp):
    r = requests.get(url)
    with open("NewsContent/%s/%s.pdf"%(folderName,timeStamp),'wb') as f:
        f.write(r.content)


#获取新闻html
def getNewsHtml(url,retry=3):
    userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {
        'User-Agent': userAgent
        # "Accept-Encoding":"gzip,deflate"
    }
    try:
        # req = urllib2.Request(url, headers=headers)
        # response = urllib2.urlopen(req,timeout = 10)
        # html = response.read()
        r = requests.get(url,timeout=6,headers = headers)
        html = r.content
        # encode = response.headers.get("content-encoding")
        # if encode== "gzip":
        #     html=zlib.decompress(html, 16+zlib.MAX_WBITS)
        # if encode == "deflate":
        #     html = deflate(html)
        if html is None:
            if retry>0:
                logger.debug( "Html:None. Retry %s %s" %(url,4-retry))
                time.sleep(4)
                return getNewsHtml(url,retry-1)
            else:
                return None
        return html
    except Exception,e:
        if retry>0:
            logger.debug( "EXCEPTION!:%s. Retry %s %s" %(e,url,4-retry))
            time.sleep(4)
            getNewsHtml(url,retry-1)
        else:
            return None


# 根据搜证券单独处理xpath节点
def xpathforSohu(link,newsHtml,timeStamp,message_id,folderName):
    try:
        tree = etree.HTML(newsHtml)
        content_node = tree.xpath(u'//*[@id="contentText"]')
        if len(content_node) == 0:
            FAIL(folderName,link,"sohu content",timeStamp)
            return
    except Exception,e:
        logger.debug("sohu Exception:%s"%e)
        FAIL(folderName,link,"sohu Exception",timeStamp)
        return
    n = NewsHtmlAnlyze()
    content = n.getContentInParentDiv(content_node[0])
    if content =="":
        FAIL(folderName,link,"content",timeStamp)
        return
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,timeStamp)


#根据10jqka网站单独处理xpath节点
def xpathfor10jqka(link,newsHtml,timeStamp,message_id,folderName):
    try:
        logger.debug("xpathfor10jqka.....")
        tree = etree.HTML(newsHtml)
        content_node = tree.xpath(u'//div[@class="atc-content"]')
        logger.debug("atc-content:%s"%content_node)
        if len(content_node)==0:
            content_node = tree.xpath(u'//div[@class="art_main"]')
            logger.debug("art_main:%s"%content_node)
        if len(content_node) == 0:
            FAIL(folderName,link,"10jqka content",timeStamp)
            return
    except Exception,e:
        logger.debug("10jqka Exception:%s"%e)
        FAIL(folderName,link,"10jqka Exception",timeStamp)
        return
    n = NewsHtmlAnlyze()
    content = n.getContentInParentDiv(content_node[0])
    if content =="":
        FAIL(folderName,link,"content",timeStamp)
        return
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,timeStamp)


# 针对qq财经单独处理 使用正则匹配p标签内的内容
def reforFinanceQQ(link,html,timeStamp,message_id,folderName,method = "1"):
    if method =="2":
        logger.debug("qq method 2")
        pattern = re.compile(ur'<P|p>(.*?)</P|p>')
        content = pattern.findall(html)
        if not content:
            FAIL(folderName,link,"qq content",timeStamp)
            return
        text = ""
        for i in content:
            text = text+i
        pattern = re.compile(r'<.*?>')
        content = pattern.sub('',text)
        # title = re.sub('[\/:*?"<>|]','-',title)
        with open("NewsContent/%s/%s.txt"%(folderName,message_id), "w") as myfile:
            myfile.write(content+'\n')
        # writeNewsContent(folderName,message_id,content,link)
        SUCCESS(folderName,link,timeStamp)
    if method == "1":
        logger.debug("qq method 1")
        pattern = re.compile(ur'<P style="TEXT-INDENT: 2em">(.*?)</P>')
        content = pattern.findall(html)
        if not content:
            reforFinanceQQ(link,html,timeStamp,message_id,folderName,method = "2")
            return
        text = ""
        for i in content:
            text = text + i
        pattern = re.compile(r'<.*?>')
        content = pattern.sub('',text)
        # title = re.sub('[\/:*?"<>|]','-',title)
        with open("NewsContent/%s/%s.txt"%(folderName,message_id), "w") as myfile:
            myfile.write(content+'\n')
        # writeNewsContent(folderName,message_id,content,link)
        SUCCESS(folderName,link,timeStamp)


# 针对新浪财经单独处理
def getNewLinkforFinanceSina(html):
    # logger.debug(html)
    pattern = re.compile(r'URL=(.*?)">')
    match = pattern.search(html)
    if match:
        link = match.group(1)
        logger.debug("sina new link %s"%link)
        return link


# 从text中获取连续的汉字 并对其从字符串多至少排列 以增加xpath匹配html标签的准确性
def continueTen(text,i):
    try:
        pattern = re.compile(ur"[\u4E00-\u9FFF]+")
        match = pattern.findall(text)
        match = sorted(match,key=len,reverse = True)
        return match[i]
    except Exception,e:
        logger.debug("continueTen Exception:%s"%e)
        return None


#处理新闻网页div标签
class NewsHtmlAnlyze():
    #获取匹配的标签的list树 html/body/div/div/p
    def getNodeList(self,newsHtml,text):
        retry = 0
        method = 0
        while True:
            re_string = continueTen(text,retry)
            logger.debug("re_string is %s"%re_string)
            if method ==0:
                logger.debug("method 0")
                tree = etree.HTML(newsHtml)
            if method ==1:
                logger.debug("method 1")
                newsHtml = newsHtml.decode("gb2312",'ignore').encode('utf-8')
                tree = etree.HTML(newsHtml,parser=etree.HTMLParser(encoding='utf-8'))
            content_node = tree.xpath(u'/html/body//*[contains(.,"%s")]'% re_string)
            if len(content_node) == 0:
                if retry == 4 and method==0:
                    retry = 0
                    method = 1
                    logger.debug("method 0 retry 3.to method 1")
                    continue
                if retry ==4 and method==1:
                    logger.debug( "6 really none")
                    content_node = None
                    break
                else:
                    retry = retry + 1
                    logger.debug( "content_node is None.Retry %s" %retry)
                    continue
            else:
                break
        return content_node


    #获取匹配内容标签的父级第一个div标签作为提取新闻的容器。
    def getParentDiv(self,content_node):
        for i in range(0,len(content_node))[::-1]:
            if content_node[i].tag == 'div':
                logger.debug( "the news content div class name is:%s"%content_node[i].get('class'))
                return content_node[i]
            if content_node[i].tag == 'table':
                logger.debug( "the news content div class name is:%s"%content_node[i].get('class'))
                return content_node[i]
        return None


    def getContentInParentDiv(self,parent_div):
        child = parent_div.xpath(u'descendant::*')
        content = ""
        for i in range(0,len(child)):
            tail = child[i].tail
            text = child[i].text
            if tail==None:
                tail = ''
            if text ==None:
                text = ''
            child_content = text+tail
            if '{' in child_content:
                child_content = ''
            content = content +child_content
        return content


# 写新闻内容txt
def writeNewsContent(folderName,message_id,content,link):
    pattern = re.compile(r'<.*?>')
    content = pattern.sub('',content)
    try:
        f = codecs.open("NewsContent/%s/%s.txt"%(folderName,message_id),"w",'utf-8')
        f.write(link+"\r\n")
        f.write(content)
    except Exception,e:
        logger.debug( "write news content exception!%s"%e)
    finally:
        f.close()

# 保存失败的链接 
def badLinkSave(stockID,link):
    try:
        f = codecs.open("NewsContent/%s/badlink.txt"%stockID, "a","utf-8")
        f.write(link+'\r\n')
    except Exception,e:
        logger.debug("badlink save Exception:%s"%e)
    finally:
        f.close()
def processTimeSave(stockID,timeStamp):
    logger.debug("process link save index:%s"%index)
    try:
        f = codecs.open("NewsContent/%s/processTime.txt"%stockID, "a","utf-8")
        f.write(str(timeStamp)+'\r\n')
    except Exception,e:
        logger.debug("process save Exception:%s"%e)
    finally:
        f.close()
        logger.debug("process link save over:%s"%index)
# 获取失败
def FAIL(stockID,link,cause,timeStamp,oldlink=None):
    global index
    global fail
    if oldlink:
        link = oldlink
    badLinkSave(stockID,link)
    processTimeSave(stockID,timeStamp)
    logger.info("Index:%s Fail:%s Fail to get %s cause %s is none" %(index,fail,link,cause))
    # logger.info("Fail get %s"%link)
    index = index+1
    fail  = fail +1


# 获取成功 每成功5个 更新process字典 
# process字典用于断点续传 程序断掉后 执行continue,将从process字典中得到未执行的那些链接
def SUCCESS(stockID,link,timeStamp,oldlink = None):
    global index
    global success
    if oldlink:
        link = oldlink
    processTimeSave(stockID,timeStamp)
    logger.info("Index:%s Success:%s Success get news %s" %(index,success,link))
    # logger.info("Success get %s"%link)
    index = index+1
    success  = success +1

# 主程序
# 1.获取新闻html文件
# 2.在html文件内匹配text对应的标签
#   程序思想是：text内是新闻的简介。在html内寻找包含简介文字，比如“你好”，的标签，得到一个p标签，再上一级得
#   到包含此p标签的父级div。新闻的全部内容就在这个div标签内。
#   一般新闻的格式是：
#  <div>
#       <p>你好</p>
#       <p>吃了吗</p>
#       <p>再见</p>
#  </div>
# 3.提取此div下全部后代的内容
# 4.写文件
# tip:个别主要网站单独处理以便更精确的提取
def MainProcess(link,text,title,folderName,message_id,timeStamp,oldlink=None):
    logger.debug("link is %s" %link)
    if ".pdf" in link:
        getPdf(link,folderName,timeStamp)
        SUCCESS(folderName,link,timeStamp,oldlink)
        return
    newsHtml= getNewsHtml(link)
    if newsHtml is None:
        FAIL(folderName,link,"newsHtml",timeStamp)
        return
    if "stock.sohu.com" in link:
        xpathforSohu(link,newsHtml,timeStamp,message_id,folderName)
        return
    if "stock.10jqka.com.cn" in link:
        xpathfor10jqka(link,newsHtml,timeStamp,message_id,folderName)
        return
    if "finance.qq.com" in link:
        reforFinanceQQ(link,newsHtml,timeStamp,message_id,folderName)
        return
    newsHtmlAnlyze = NewsHtmlAnlyze()
    content_node = newsHtmlAnlyze.getNodeList(newsHtml,text)
    logger.debug("final content_node is %s"%content_node)
    if content_node is None:
        if oldlink:
            FAIL(folderName,link,"content_node",timeStamp,oldlink)
            return
        if "finance.sina.com.cn" in link and chardet.detect(newsHtml)["encoding"]=="ascii":
            oldlink = link
            link = getNewLinkforFinanceSina(newsHtml)
            MainProcess(link,text,title,folderName,message_id,timeStamp,oldlink)
            return
        FAIL(folderName,link,"content_node",timeStamp)
        return
    parent_div =  newsHtmlAnlyze.getParentDiv(content_node)
    logger.debug("parent_div is %s"%parent_div)
    if parent_div is None:
        FAIL(folderName,link,"parent_div",timeStamp)
        return
    content = newsHtmlAnlyze.getContentInParentDiv(parent_div)
    if content == "":
        FAIL(folderName,link,"content",timeStamp)
        return
    # title = re.sub('[\/:*?"<>|]','-',title)
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,timeStamp,oldlink)


# 多线程
class ParseStockId(object):
    """docstring for getStockId"""
    def __init__(self,fileName,dic):
        self.fileName = fileName
        self.link_TitleTextIdTime_dict = dic

    def passID(self):
        queue = Queue.Queue()
        for i in range(50):
            t = MyThread(i,"Threading%s"%i,queue,self.link_TitleTextIdTime_dict,self.fileName)
            t.setDaemon(True)
            t.start()
        for i in self.link_TitleTextIdTime_dict:
            queue.put(i)
        queue.join()


#一个线程
class MyThread(threading.Thread):
    """docstring for MyThread"""

    def __init__(self,thread_id, name,queue,dic,folderName):
        super(MyThread, self).__init__()  #调用父类的构造函数
        self.link_TitleTextIdTime_dict = dic
        self.folderName = folderName
        self.thread_id = thread_id
        self.name = name
        self.queue = queue

    def run(self) :
        while True:
            logging.debug( "Starting " + self.name)
            link  = self.queue.get()
            text = self.link_TitleTextIdTime_dict[link][1]
            title = self.link_TitleTextIdTime_dict[link][0]
            message_id = self.link_TitleTextIdTime_dict[link][2]
            timeStamp = self.link_TitleTextIdTime_dict[link][3]
            try:
                MainProcess(link,text,title,self.folderName,message_id,timeStamp)
            except Exception,e:
                logger.warning("THREADING EXCEPTION!:%s"%e)
                FAIL(self.folderName,link,"Threading exception",timeStamp)
            finally:       
                self.queue.task_done()
                logging.debug( "Exiting " + self.name)
            print " "

def getStcokIdNeed(fileName):
    for i in os.listdir(fileName):
        fn = i[0:8]
        if not fn.startswith('.'):
            stockIDlist.append(fn)
    return stockIDlist
def getStcokIdinNewsContent():
    NewsContentList = []
    for i in os.listdir('NewsContent'):
        fn = i[0:8]
        print fn
        if not fn.startswith('.'):
            NewsContentList.append(fn)
    return NewsContentList

class Main():
    def checkFile(self,fileName):
        if os.path.isfile(fileName):
            return "have"

    def removeFile(self,fileName):
        if os.path.isfile(fileName):
            os.remove(fileName)

    def getProcessTimeList(self,folderName):
        processTimeList = []
        f= codecs.open("NewsContent/%s/processTime.txt"%folderName,'r','utf-8')
        for line in f:
            processTimeList.append(line.rstrip())
        f.close()
        processTimeList.sort(reverse = True)
        return processTimeList
    def getBadLinkList(self,folderName):
        badLinkList = []
        f = open("NewsContent/%s/badlink.txt"%folderName,'r')
        for line in f:
            badLinkList.append(line.rstrip())
        f.close()
        return badLinkList
    # def getContinueDict(self,processLastTimeStamp,oldDict):
    #     for index,value in enumerate(oldDict.values()):
    #         if processLastTimeStamp in value:
    #             LastIndex = index
    #     keysList = []
    #     for i in xrange(0,LastIndex+1):
    #         keysList.append(oldDict.keys()[i])
    #     for key in keysList:
    #         oldDict.pop(key)
    #     return oldDict
    
    def getContinueDict(self,processTimeList,oldDict):
        for k,v in oldDict.items():
            if any(s in v for s in processTimeList):
                oldDict.pop(k)
        return oldDict
    def retry(self,stockIDlist):
        for folderName in stockIDlist:
            index = 1
            success = 1
            fail = 1
            badlinkDict = {}
            have = self.checkFile("NewsContent/%s/badlink.txt"%folderName)
            if have:
                badLinkList = self.getBadLinkList(folderName)
                self.removeFile("NewsContent/%s/badlink.txt"%folderName)
                link_TitleTextIdTime_dict = read(folderName)
                for link in badLinkList:
                    badlinkDict[link] = link_TitleTextIdTime_dict[link]
                logger.info( u"重试%s失败链接"%folderName)
                parseStockId = ParseStockId(folderName,badlinkDict)
                parseStockId.passID()
            else:
                logger.info("%s没有badlink文件"%folderName)
                return

# 全新开始
    def start(self,stockIDlist):
        global index
        global success
        global fail
        for folderName in stockIDlist:
            index = 1
            success = 1
            fail = 1
            badlinkDict = {}
            checkDir("NewsContent/%s"%folderName)
            dt = time.strftime(format,time.localtime())
            fh = logging.FileHandler('NewsContent'+'/'+folderName+'/'+dt+'.log')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            # 字典为读excel的字典
            link_TitleTextIdTime_dict = read(folderName)
            have = self.checkFile('NewsContent/%s/processTime.txt'%folderName)
            if have:
                restDict = {}
                processTimeList = self.getProcessTimeList(folderName)
                # processLastTimeStamp = str(processTimeList[len(processTimeList)-1])
                # dictLastTimeStamp = str(link_TitleTextIdTime_dict.values()[-1][3])
                restDict = self.getContinueDict(processTimeList,link_TitleTextIdTime_dict)
                restDictNum = len(restDict)
                if restDictNum==0:
                    logger.info( u"%s股票已经爬完,检测下一只股票"%folderName)
                    continue
                else:
                    logger.info( u"%s股票未爬完,正在继续..."%folderName)
                    link_TitleTextIdTime_dict = restDict
            else:
                logger.info(u"%s股票并未爬过 开始爬..."%folderName)
                self.removeFile("NewsContent/%s/badlink.txt"%folderName)
            parseStockId = ParseStockId(folderName,link_TitleTextIdTime_dict)
            parseStockId.passID()
            badLinkList_old = []
            while True:
                index = 1
                success = 1
                fail = 1
                badlinkDict = {}
                have = self.checkFile("NewsContent/%s/badlink.txt"%folderName)
                if have:
                    badLinkList = self.getBadLinkList(folderName)
                    if len(badLinkList) == len(badLinkList_old):
                        logger.info( u"重试%s结束"%folderName)
                        break
                    self.removeFile("NewsContent/%s/badlink.txt"%folderName)
                    badLinkList_old = badLinkList
                    link_TitleTextIdTime_dict = read(folderName)
                    for link in badLinkList:
                        badlinkDict[link] = link_TitleTextIdTime_dict[link]
                    logger.info( u"重试%s失败链接"%folderName)
                    parseStockId = ParseStockId(folderName,badlinkDict)
                    parseStockId.passID()
                else:
                    break


# 1.初次 执行python getNewsContent.py start 或者 python getNewsContent.py s
# 2.如果中间断掉了 执行 python getNewsContent.py continue 或者  python getNewsContent.py c
#   会接着上面断掉的执行
# 3. 执行一遍可能会有很多链接因为封ip被墙 执行 python getNewsContent.py retry 或者python getNewsContent.py r
#   程序将只提取失败的链接重新尝试。
if __name__ == '__main__':
    value = sys.argv[1]
    stockIDlist = []
    stockIDlist = getStcokIdNeed('NewsLinkText')
    logger.debug(stockIDlist)
    main = Main()
    if value == "start" or value == "s":
        main.start(stockIDlist)
    if value == "retry" or value == "r":
        NewsContentList = getStcokIdinNewsContent()
        main.retry(NewsContentList)

    