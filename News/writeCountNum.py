# -*- coding: utf-8 -*-
import xlwt
from datetime import datetime
import os
import sys
import xlrd
import codecs
wb = xlwt.Workbook()
ws = wb.add_sheet('A Test Sheet')

ws.write(0, 0, u"stockId")
ws.write(0, 1, u"原股票长度")
ws.write(0, 2, u"程序运行结果")
ws.write(0, 3, u"本地下载结果")
ws.write(0, 4, u"badlink内结果")
ws.write(0, 5, u"完成度")

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
            elif i[-3:] == "pdf":
                txtList.append(i.replace(".pdf",""))

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
    row = 1
    for stockId in stockIdList:
        txtList = getExitNewsTXT(stockId)
        badLinkList= getBadLink(stockId)
        processList = []
        processList = badLinkList+txtList
        processList.sort(reverse = True)
        

        message_idList = read(stockId)
        
        ws.write(row, 0, stockId)
        ws.write(row, 1, len(message_idList))
        ws.write(row, 2, len(processList))
        ws.write(row, 3, len(txtList))
        ws.write(row, 4, len(badLinkList))
        if len(message_idList) == len(processList):
            ws.write(row, 5, "complete")
        else:
            ws.write(row, 5, "not complete")
        row = row +1

diffNum()

wb.save('countNum.xls')