
# coding=utf-8
"""
功能:从NewsLinkText文件夹中的excel表中读链接，获取相应新闻
pip install requests
pip install lxml
pip install chardet
pip install logging
pip install xlrd
pip install collections
--------------
Author：kenziD
"""

import re
import os
import sys
import time
import xlrd
from lxml import etree
import Queue
import codecs
import chardet
import logging
import requests
import threading
from collections import OrderedDict
import argparse


import datetime
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
# 格式：{"link":["title","text","id","TimeStamp"],}
def read(fileName):
    xl_workbook = xlrd.open_workbook("NewsLinkText/%s.xls"%fileName)
    sheet_names = xl_workbook.sheet_names()
    xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
    nrow = xl_sheet.nrows
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
        idList.append(str(cell_obj.value)[0:8])
    del idList[0:1]
    idTitle_dict = OrderedDict(zip(idList,titleList))
    idText_dict = OrderedDict(zip(idList,textList))
    idTime_dict = OrderedDict(zip(idList,timeList))
    idLink_dict = OrderedDict(zip(idList,linkList))
    id_TitleTextLinkTime = OrderedDict(((key, [idTitle_dict[key], idText_dict[key],idLink_dict[key],idTime_dict[key]]) for key in idLink_dict))
    if len(idLink_dict.keys()) != nrow-1:
        logger.debug("dict may have repeat link")
    return id_TitleTextLinkTime


# 有一些链接是.pdf
def getPdf(url,folderName,message_id):
    r = requests.get(url)
    with open("NewsContent/%s/%s.pdf"%(folderName,message_id),'wb') as f:
        f.write(r.content)


#获取新闻html
def getNewsHtml(url,retry=3):
    userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {
        'User-Agent': userAgent
        # "Accept-Encoding":"gzip,deflate"
    }
    try:
        r = requests.get(url,timeout=6,headers = headers)
        html = r.content
        if r.status_code == 404:
            return None
        if html is None:
            if retry>0:
                logger.debug( "Html:None. Retry %s %s" %(url,4-retry))
                time.sleep(4)
                return getNewsHtml(url,retry-1)
            else:
                return None
        return html
    except requests.ConnectionError,e:
        logger.debug("EXCEPTION! %s"%e)
        return None
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
            FAIL(folderName,link,"sohu content",message_id)
            return
    except Exception,e:
        logger.debug("sohu Exception:%s"%e)
        FAIL(folderName,link,"sohu Exception",message_id)
        return
    n = NewsHtmlAnlyze()
    content = n.getContentInParentDiv(content_node[0])
    if content =="":
        FAIL(folderName,link,"content",message_id)
        return
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,message_id)


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
            FAIL(folderName,link,"10jqka content",message_id)
            return
    except Exception,e:
        logger.debug("10jqka Exception:%s"%e)
        FAIL(folderName,link,"10jqka Exception",message_id)
        return
    n = NewsHtmlAnlyze()
    content = n.getContentInParentDiv(content_node[0])
    if content =="":
        FAIL(folderName,link,"content",message_id)
        return
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,message_id)


# 针对qq财经单独处理 使用正则匹配p标签内的内容
def reforFinanceQQ(link,html,timeStamp,message_id,folderName,method = "1"):
    if method =="2":
        logger.debug("qq method 2")
        pattern = re.compile(ur'<P|p>(.*?)</P|p>')
        content = pattern.findall(html)
        if not content:
            FAIL(folderName,link,"qq content",message_id)
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
        SUCCESS(folderName,link,message_id)
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
        SUCCESS(folderName,link,message_id)


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




# 失败
def FAIL(stockID,link,cause,message_id,oldlink = None):
    global index
    global fail
    global badlinkQueue
    if oldlink:
        link = oldlink
    messageid_stockid={}
    messageid_stockid[message_id]=stockID
    badlinkQueue.put(messageid_stockid)
    
    messageIdQueue.put(messageid_stockid)
    logger.info("Index:%s Fail:%s Fail to get %s %s cause %s is none" %(index,fail,message_id,link,cause))
    # logger.info("Fail get %s"%link)
    index = index+1
    fail  = fail +1


# 成功
def SUCCESS(stockID,link,message_id,oldlink = None):
    global index
    global success
    if oldlink:
        link = oldlink
    messageid_stockid={}
    messageid_stockid[message_id]=stockID
    messageIdQueue.put(messageid_stockid)
    
    logger.info("Index:%s Success:%s Success get news %s" %(index,success,link))
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
        getPdf(link,folderName,message_id)
        SUCCESS(folderName,link,message_id,oldlink)
        return
    newsHtml= getNewsHtml(link)
    if newsHtml is None:
        FAIL(folderName,link,"newsHtml",message_id)
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
            FAIL(folderName,link,"content_node",message_id,oldlink)
            return
        if "finance.sina.com.cn" in link and chardet.detect(newsHtml)["encoding"]=="ascii":
            oldlink = link
            link = getNewLinkforFinanceSina(newsHtml)
            MainProcess(link,text,title,folderName,message_id,timeStamp,oldlink)
            return
        FAIL(folderName,link,"content_node",message_id)
        return
    parent_div =  newsHtmlAnlyze.getParentDiv(content_node)
    logger.debug("parent_div is %s"%parent_div)
    if parent_div is None:
        FAIL(folderName,link,"parent_div",message_id)
        return
    content = newsHtmlAnlyze.getContentInParentDiv(parent_div)
    if content == "":
        FAIL(folderName,link,"content",message_id)
        return
    # title = re.sub('[\/:*?"<>|]','-',title)
    writeNewsContent(folderName,message_id,content,link)
    SUCCESS(folderName,link,message_id,oldlink)


# 多线程
class ParseStockId(object):
    """docstring for getStockId"""
    def __init__(self,fileName,dic):
        self.fileName = fileName
        self.id_TitleTextLinkTime_dict = dic

    def passID(self):
        queue = Queue.Queue()
        for i in range(50):
            t = MyThread(i,"Threading%s"%i,queue,self.id_TitleTextLinkTime_dict,self.fileName)
            t.setDaemon(True)
            t.start()
        for i in self.id_TitleTextLinkTime_dict:
            queue.put(i)
        queue.join()

lock = threading.Lock()
#一个线程
class MyThread(threading.Thread):
    """docstring for MyThread"""

    def __init__(self,thread_id, name,queue,dic,folderName):
        super(MyThread, self).__init__()  #调用父类的构造函数
        self.id_TitleTextLinkTime_dict = dic
        self.folderName = folderName
        self.thread_id = thread_id
        self.name = name
        self.queue = queue

    def run(self) :
        global index
        while True:

            logger.debug( "Starting " + self.name)
            # print "threading number",threading.activeCount()
            try:
                message_id  = self.queue.get(3,True)
            except Queue.Empty:
                logger.debug("queue is empty")
                logger.debug( "Exiting " + self.name)
                break
            else:
                try:
                    text = self.id_TitleTextLinkTime_dict[message_id][1]
                except:
                    raise
                title = self.id_TitleTextLinkTime_dict[message_id][0]
                link = self.id_TitleTextLinkTime_dict[message_id][2]
                timeStamp = self.id_TitleTextLinkTime_dict[message_id][3]
                # if lock.acquire():
                try:
                    MainProcess(link,text,title,self.folderName,message_id,timeStamp)
                    # index = index+1
                except Exception,e:
                    logger.warning("THREADING EXCEPTION!:%s"%e)
                    # index = index+1
                    FAIL(self.folderName,link,"Threading exception",message_id)
                finally:
                    self.queue.task_done()
                    logger.debug( "Exiting " + self.name)
                print " "
                # lock.release()

class BadlinkThread(threading.Thread):
    def __init__(self,queue):
        super(BadlinkThread, self).__init__()
        self.badlinkQueue = queue

    def run(self):
        while True:
            logger.debug( "start badlink queue")
            try:
                messageid_stockid  = self.badlinkQueue.get()
            except Queue.Empty:
                logger.debug("badlink queue is empty")
                break
            else:
                try:
                    messageid = messageid_stockid.keys()[0]
                    stockID = messageid_stockid.get(messageid)
                    with codecs.open("NewsContent/%s/badlink.txt"%stockID, "a","utf-8") as f:
                        f.write(messageid+'\r\n')
                    logger.debug("write %s"%messageid)
                except Exception,e:
                    logger.info("badlink save Exception:%s"%e)
                finally:
                    self.badlinkQueue.task_done()

class MessageIdVisitedThread(threading.Thread):
    def __init__(self,queue):
        super(MessageIdVisitedThread, self).__init__()
        self.messageIdQueue = queue

    def run(self):
        while True:
            logger.debug( "start message_id queue")
            try:
                messageid_stockid = self.messageIdQueue.get()
            except Queue.Empty:
                break
            else:
                try:
                    messageid = messageid_stockid.keys()[0]
                    stockID = messageid_stockid.get(messageid)
                    with codecs.open("NewsContent/%s/processId.txt"%stockID, "a","utf-8") as f:
                        f.write(messageid+'\r\n')
                except Exception,e:
                    logger.info("message_id save Exception:%s"%e)
                finally:
                    self.messageIdQueue.task_done()
                    

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
        # print fn
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

    def getProcessIdList(self,folderName):
        processIdList = []
        with codecs.open("NewsContent/%s/processId.txt"%folderName,'r','utf-8') as f:
            for line in f:
                processIdList.append(line.rstrip())
        processIdList.sort(reverse = True)
        return processIdList

    def getBadLinkList(self,folderName):
        badLinkList = []
        f = codecs.open("NewsContent/%s/badlink.txt"%folderName,'r','utf-8')
        for line in f:
            # logger.debug("line%s"%line)
            badLinkList.append(line.rstrip())
        f.close()
        # print badLinkList
        return badLinkList

    def getContinueDict(self,processIdList,oldDict):
        for k,v in oldDict.items():
            if any(s in k for s in processIdList):
                oldDict.pop(k)
        return oldDict

    def getAllExceptExitNews(self,stockId,oldDict):
        txtList = []
        for i in os.listdir("NewsContent/%s"%stockId):
            if len(i)==12:
                if i[-3:] == "txt":
                    txtList.append(i.replace(".txt",""))
                    
                elif i[-3:] == "pdf":
                    txtList.append(i.replace(".pdf",""))

        for k,v in oldDict.items():
            if any(s in k for s in txtList):
                oldDict.pop(k)
        return oldDict
    # 重新过滤失败链接
    def retry(self,stockIDlist,force=None):
        global index
        global success
        global fail
        global badlinkQueue
        for folderName in stockIDlist:
            dt = time.strftime(format,time.localtime())
            fh = logging.FileHandler('NewsContent'+'/'+folderName+'/'+dt+'.log')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            index = 1
            success = 1
            fail = 1
            badlinkDict = {}
            have = self.checkFile("NewsContent/%s/badlink.txt"%folderName)
            id_TitleTextLinkTime_dict = read(folderName)
            if have:
                
                if force:
                    badlinkDict=self.getAllExceptExitNews(folderName,id_TitleTextLinkTime_dict)
                    logger.info( u"强制重试%s失败链接"%folderName)
                else:
                    badLinkList = self.getBadLinkList(folderName)
                    
                    for message_id in badLinkList:
                        try:
                            badlinkDict[message_id] = id_TitleTextLinkTime_dict[message_id]
                        except Exception,e:
                            logger.info(u"重试失败链接异常：%s"%e)
                            badlinkDict[message_id] = ["None","None","None","None"]
                    logger.info( u"重试%s失败链接"%folderName)
                self.removeFile("NewsContent/%s/badlink.txt"%folderName)
                parseStockId = ParseStockId(folderName,badlinkDict)
                parseStockId.passID()
                badlinkQueue.join()
                logger.debug(u"已经join,队列疏通")
            else:
                logger.info(u"%s没有badlink文件"%folderName)
                if force:
                    badlinkDict=self.getAllExceptExitNews(folderName,id_TitleTextLinkTime_dict)
                    logger.info( u"强制重试%s失败链接"%folderName)
                    parseStockId = ParseStockId(folderName,badlinkDict)
                    parseStockId.passID()
                    badlinkQueue.join()
                    logger.debug(u"已经join,队列疏通")
            logger.removeHandler(fh)


    # 开始程序
    def start(self,stockIDlist):
        global index
        global success
        global fail
        global badlinkQueue
        print
        for folderName in stockIDlist:
            index = 1
            success = 1
            fail = 1
            badlinkDict = {}
            checkDir("NewsContent")
            checkDir("NewsContent/%s"%folderName)
            dt = time.strftime(format,time.localtime())
            fh = logging.FileHandler('NewsContent'+'/'+folderName+'/'+dt+'.log')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            # 字典为读excel的字典
            id_TitleTextLinkTime_dict = read(folderName)
            if len(id_TitleTextLinkTime_dict.keys())==0:
                logger.info( u"%s股票文件为空,检查下一只股票"%folderName)
                logger.removeHandler(fh)
                continue
            have = self.checkFile('NewsContent/%s/processId.txt'%folderName)
            if have:
                restDict = {}
                processIdList = self.getProcessIdList(folderName)
                # processLastTimeStamp = str(processTimeList[len(processTimeList)-1])
                # dictLastTimeStamp = str(id_TitleTextLinkTime_dict.values()[-1][3])
                restDict = self.getContinueDict(processIdList,id_TitleTextLinkTime_dict)
                restDictNum = len(restDict)
                if restDictNum==0:
                    logger.info( u"%s股票已经爬完,检测下一只股票"%folderName)
                    logger.removeHandler(fh)
                    continue
                else:
                    logger.info( u"%s股票未爬完,正在继续..."%folderName)
                    id_TitleTextLinkTime_dict = restDict
            else:
                logger.info(u"%s股票并未爬过 开始爬..."%folderName)
                self.removeFile("NewsContent/%s/badlink.txt"%folderName)

            parseStockId = ParseStockId(folderName,id_TitleTextLinkTime_dict)
            parseStockId.passID()
            badlinkQueue.join()
            logger.debug(u"已经join,队列疏通")
            badLinkList_old = []
            oldindex = 0
            oldfail = 1
            while True:
                index = 1
                success = 1
                fail = 1
                badlinkDict = {}

                have = self.checkFile("NewsContent/%s/badlink.txt"%folderName)
                if have:
                    badLinkList = self.getBadLinkList(folderName)
                    logger.debug(len(badLinkList))
                    logger.debug(len(badLinkList_old))
                    # if len(badLinkList) == len(badLinkList_old):
                    logger.debug(oldindex)
                    logger.debug(oldfail)
                    if oldindex == oldfail:
                        logger.info( u"重试%s结束"%folderName)
                        break
                    self.removeFile("NewsContent/%s/badlink.txt"%folderName)
                    badLinkList_old = badLinkList
                    id_TitleTextLinkTime_dict = read(folderName)
                    for message_id in badLinkList:
                        try:
                            badlinkDict[message_id] = id_TitleTextLinkTime_dict[message_id]
                        except Exception,e:
                            logger.info(u"重试失败链接异常：%s"%e)
                            badlinkDict[message_id] = ["None","None","None","None"]
                    logger.info( u"重试%s失败链接"%folderName)
                    parseStockId = ParseStockId(folderName,badlinkDict)
                    parseStockId.passID()
                    badlinkQueue.join()
                    logger.debug(u"已经join,队列疏通")
                    oldindex = index
                    oldfail = fail
                else:
                    break
            logger.removeHandler(fh)



if __name__ == '__main__':
    badlinkQueue = Queue.Queue()
    messageIdQueue = Queue.Queue()

    ff = BadlinkThread(badlinkQueue)
    ff.setDaemon(True)
    ff.start()

    mt = MessageIdVisitedThread(messageIdQueue)
    mt.setDaemon(True)
    mt.start()
    
    starttime = datetime.datetime.now()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r" ,"--retry", help="retry url in badlink.txt",action="store_true")
    group.add_argument("-rf", help="delete all badlink.txt and retry by what already download",action="store_true")
    parser.add_argument("stockId",help="choose one stock to process",nargs='?',type=str)
    args = parser.parse_args()

    stockIDlist = []
    stockIDlist = getStcokIdNeed('NewsLinkText')
    logger.debug(stockIDlist)
    main = Main()
    if args.retry:
        if args.stockId:
            NewsContentList = [args.stockId]
        else:
            NewsContentList = getStcokIdinNewsContent()
        print NewsContentList
        main.retry(NewsContentList)
    elif args.rf:
        if args.stockId:
            NewsContentList = [args.stockId]
        else:
            print "force retry"
            NewsContentList = getStcokIdinNewsContent()
        main.retry(NewsContentList,"force")
    else:
        if args.stockId:
            
            stockIDlist = [args.stockId]
        main.start(stockIDlist)

    print threading.enumerate()
    badlinkQueue.join()
    messageIdQueue.join()    
    
    endtime = datetime.datetime.now()
    print "seconds",(endtime - starttime).seconds


