# 用于爬取雪球网站股票的新闻

* 先运行XueqiuNews.py

	指令为

	```
	python XueqiuNews.py
	```

	会在所在文件夹生成一个NewsLinkText文件夹，每个股票会生成相应的xsl文件，xsl文件包含了这个股票的新闻链接，转发量，评论量，新闻简介，时间，时间戳。大概两个小时运行结束。如果运行中断（比如直接关掉终端），再次运行此程序，将接着上次断掉的地方继续。运行结束后会自动检查空的股票文件，重新爬虫空文件，直到两次爬得得空文件数量一致。停止。日志信息放在log文件夹内。

* 再运行getNewsContent.py

	指令为

	```
	python getNewsContent.py s
	```

	或者

	```
	python getNewsContent.py start
	```

	将会在所在文件夹生成NewsContent文件夹，每个股票将生成一个文件夹，相应的新闻以新闻id的名字命名生成txt文件。

	badlink.txt包含了失败的链接。

	processtime.txt包含了爬过的新闻的时间戳。

	如果运行中断，重新运行，将以此文件作为依据。请不要随意更改。
	如果程序中断，重新运行：

	```
	python getNewsContent.py s
	```

	会根据processtime.txt检测已经爬过的新闻，以便接着上次继续。

	log文件记录的日志信息，可以查询某链接失败的原因。

	每个股票结束后会重新过滤失败的链接，直到两次得到的失败链接数目一致。


	文件结构为：
```
NewsContent
----SH000001
--------2016-01-01-12-23-23.log
--------badlink.txt
--------processTime.txt
--------32432442.txt
--------...
----SZ400002
--------...
----SH900000
--------...
```
运行

```
python getNewsContent.py r
```

或者

```
python getNewsContent.py retry
```

会重新过滤一遍所有股票失败链接。

* [可选]运行

```
python openlink.py arg from-to
```

arg为股票的id
例如

```
python openlink.py SH600001 1-10
```

将在chrome浏览器里打开badlink中1-10，共10条链接，
```
python openlink.py SH600001 20-30
```
将在chrome浏览器里打开badlink中第20-30，共10条链接，

以此检测哪些是真正失败的链接，哪些是漏网之鱼。注意要安装chromedriver[下载地址](http://chromedriver.storage.googleapis.com/index.html?path=2.20/)。并把程序中的路径改为你的chromedriver所在文件夹。
如下所示：

```
driver = webdriver.Chrome("E:/Program Files/chromedriver_win32/chromedriver.exe")
```
官方网站没有windows 64位chromedirver

* countnum.py

功能:

输入
```python countNum.py stockId```
例如 
```python countNum.py SZ000001```

将会自动计算已经爬的新闻加上badlink的新闻数量是否和原xsl文件数量一致

如果一致显示：complete

将会自动计算已经爬的新闻加上badlink的新闻数量是否和原xsl文件数量一致
如果一致显示：complete

如果不一致，将会显示少了哪些

如果直接输入```python countNum.py ```后面不带参数

则会自动计算NewsLinkText里的所有股票。

按理说，爬到本地的新闻加上badlink里的应该等于总和。但有时候不相等。原因是因为多线程没有加锁。导致线程共享变量：计数的index有时会被多个线程使用
导致重复。且多线程共同写一个文件时（这里是badlink.txt文件）会有复写。使得badlink里的链接少了。
如果加了锁可以保证所有股票爬下来都能数量一致。但是速度会是不加锁的速度的三倍。（getNewsContent.py）。


