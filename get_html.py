#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import io
import sys
import time
from urllib import request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

driver = webdriver.Chrome('E:\Program Files\chromedriver_win32\chromedriver.exe')
# 利用PhantomsJS爬比较快
#driver = webdriver.PhantomJS('E:/Program Files/phantomjs-2.0.0-windows/bin/PhantomJS')

driver.set_window_size(1920, 1080)

# 关键词：纯色 by URL编码
driver.get("http://image.baidu.com/search/index?tn=baiduimage&word=%e5%a3%81%e7%ba%b8+%e7%ba%af%e8%89%b2")

time.sleep(5)
# 通过Xpath找到More button
loadmore = driver.find_element_by_xpath('//*[@id="pageMore"]')#baidupic

a = 0
while(a<3):
	while (loadmore.get_attribute('style')!="visibility: visible;"):
		driver.execute_script("scrollTo(0,document.body.scrollHeight);")
		time.sleep(2)
	# 模拟用户行为点击加载更多按键
	actions = ActionChains(driver)
	actions.move_to_element(loadmore)
	actions.click(loadmore)
	actions.perform()

	driver.execute_script("scrollTo(0,document.body.scrollHeight);")
	time.sleep(5)
	print(loadmore.get_attribute('style'))
	a+=1

html = driver.execute_script("return document.getElementsByTagName('body')[0].innerHTML")
driver.close()

# 将爬到的html写入文件
f = open("html-body.html",'w',encoding='utf8')
f.write(html)
f.close
print("end")