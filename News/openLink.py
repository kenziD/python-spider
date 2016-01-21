# coding=utf-8
"""
功能：在chrome浏览器中打开NewsContent/stock_id/badlink.txt中的失败链接。

Author:kenziD

"""
from selenium import webdriver
import os
import sys
value = sys.argv[1]
badLinkList = []
if os.path.isfile("NewsContent/%s/badlink.txt"%value):
    with open("NewsContent/%s/badlink.txt"%value,'r') as f:
    	for line in f:
        	badLinkList.append(line.rstrip())
print badLinkList
#这里的路径要改成你安装的chromedriver的路径
driver = webdriver.Chrome("/Users/kenzid/Downloads/chromedriver")
driver.get("http://www.baidu.com")

for i in badLinkList:
    print i
    driver.execute_script("window.open('%s','_blank');"%i)