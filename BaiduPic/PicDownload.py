from urllib import request
import urllib
import re
import chardet
import sys
import io
import socket

socket.setdefaulttimeout(5)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
# headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"}
# req = request.Request(url,headers = headers)
f = open("html-body.html",'r',encoding='utf8')
html = f.read()
f.close()
imgs = re.findall('data-objurl="(.*?\.(jpeg|jpg))".*?data-width="(.*?)" data-height="(.*?)"', html)
# 获取图片长宽
#width = re.findall('data-width="(.*?)"',html)
#print(width)
#height = re.findall('data-height="(.*?)"',html)
#print(height)
#socket.setdefaulttimeout(5)
f = open("img-url.txt",'w')
i = 0
for img in imgs:
	f.write(img[0]+'\n')
	# 可以设置爬取图片的代码
	#if(int(img[2])>1900 and int(img[3])>1000):
	try:
		request.urlretrieve(img[0], '%s.jpg' % i)
	# 如果是http错误 返回错误代码
	#except urllib.error.URLError as e:
	#	print(e.code,"url:",img[0])
	#	print(e.reason,"url:",img[0])
	#	continue
	# 超时
	#except socket.timeout as e:
	#	print('timeout',img[0])
	#	continue
	except :
		print("hell know what the exception is?url:",img[0])
		continue
	i=i+1
f.close()