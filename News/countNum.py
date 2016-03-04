#coding=utf-8
"""
function:
输入python countNum.py stockId
例如 python countNum.py SZ000001

将会自动计算已经爬的新闻加上badlink的新闻数量是否和原xsl文件数量一致
如果一致显示：complete
如果不一致，将会显示少了哪些

如果直接输入python countNum.py 
则会自动计算NewsLinkText里的所有股票。

按理说，爬到本地的新闻加上badlink里的应该等于总和。但有时候不相等。原因是因为多线程没有加锁。导致线程共享变量：计数的index有时会被多个线程使用
导致重复。且多线程共同写一个文件时（这里是badlink.txt文件）会有复写。使得badlink里的链接少了。
如果加了锁可以保证所有股票爬下来都能数量一致。但是速度会是不加锁的速度的三倍。所以最后选择没有加锁（getNewsContent.py）。

"""
import os
import sys
import xlrd
import codecs
def read(stockId):
    xl_workbook = xlrd.open_workbook("NewsLinkText/%s.xls"%stockId)
    sheet_names = xl_workbook.sheet_names()
    xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
    message_idList = []
    linkList = []
    for cell_obj in xl_sheet.col(9):
        message_idList.append(str(cell_obj.value).replace(".0",""))
    del message_idList[0:1]    
    message_idList.sort(reverse=True)
    return message_idList


def defineStockIdListbyCmdArgv():
    sysList = []
    stockIdList = []   
    for i in sys.argv:
        sysList.append(i)
    if len(sysList)==2:
        stockIdList.append(sys.argv[1])
    elif len(sysList)==1:
        for i in os.listdir("NewsContent/"):
            if not i.startswith('.'):
                stockIdList.append(i)
    return stockIdList

def getExitNewsTXT(stockId):
    txtList = []
    for i in os.listdir("NewsContent/%s"%stockId):
        if len(i)==12:
            if i[-3:] == "txt":
                txtList.append(i.replace(".txt",""))
                # print i
            elif i[-3:] == "pdf":
                txtList.append(i.replace(".pdf",""))
                # print i

    return txtList

def getBadLink(stockId):
    badLinkList = []
    message_idList = read(stockId)
    if os.path.isfile("NewsContent/%s/badlink.txt"%stockId):
        with codecs.open("NewsContent/%s/badlink.txt"%stockId,'r','utf-8') as f:
            for line in f:
                line = line.rstrip()
                badLinkList.append(line)
    else:
        badLinkList = []
    return badLinkList

def diffNum():
    stockIdList = defineStockIdListbyCmdArgv()
    for stockId in stockIdList:
        txtList = getExitNewsTXT(stockId)
        badLinkList= getBadLink(stockId)
        processList = []
        processList = badLinkList+txtList
        processList.sort(reverse = True)
        

        message_idList = read(stockId)
        print "origin %s.xsl length:%s"%(stockId,len(message_idList))
        print "program %s.xsl length:%s"%(stockId,len(processList))
        print "     %s already download:%s"%(stockId,len(txtList))
        print "     %s badlink:%s"%(stockId,len(badLinkList))
        if len(message_idList) == len(processList):
            print u"complete"
            print " "
        else:
            # print message_idList
            # print processList
            # print badLinkList
            # print txtList
            print list(set(message_idList) - set(processList))
            # with open("%s.diff"%stockId,"w") as f:
            #     for i in processList:
            #         f.write(i+'\n')
            # with open("%sorigin.diff"%stockId,"w") as f:
            #     for i in message_idList:
            #         f.write(str(i)+'\n')
            print u"Not complete"
            print " "

diffNum()