# 用于爬取雪球网站股票的新闻

* 先运行XueqiuNews.py

	指令为

	```
	python XueqiuNews.py
	```

	会在所在文件夹生成NewsLinkText文件夹，每个股票会生成相应的xsl文件，xsl文件包含了这个股票的新闻链接，转发量，评论量，新闻简介，时间，时间戳。大概1个小时运行结束。如果运行中断（比如直接关掉终端），再次运行此程序，将接着上次断掉的地方继续。

	运行结束后会自动检查空的股票文件，重新爬虫空文件，直到两次爬得得空文件数量一致。停止。日志信息放在log文件夹内。

	完整运行过XueqiuNews.py一遍后，以后再次运行，将会在已生成的文件基础上进行更新。更新部分追加在xls文件的后面。

	具体的更新方法是，如果本地已经有这个股票的xls文件，那么需要判断此xls文件是否是最新的：先去得到网页端的第一条新闻的时间戳（网页端的新闻排序是从最新往后）与xls表格里的最新的时间戳进行对比，如果网页端的第一条新闻的时间戳就和表格里的时间戳相等，则判定本地已经更新到最新。如果不相等则将这条新闻追加到原有的xls里（无法插入到第一行，只能往后追加）直到遇到相等的时间戳，更新完毕，跳出这个股票，进行下一只股票的判定。

	如果本地没有这个股票的xls文件，则重新爬取。

* 再运行getNewsContent.py

	可以运行
	```
	python getNewsContent.py -h
	```

	查看帮助信息

	指令详解

	```
	python getNewsContent.py
	```

	或者

	```	
	python getNewsContent.py ［stockid]
	```
	即

	```
	python getNewsContent.py SH600000
	```

	将爬去某个指定id的新闻，如果没有指定id，则爬去NewsLinkText文件夹内的新闻

	程序运行过程中，
	将会在所在文件夹生成NewsContent文件夹，每个股票将生成一个文件夹，相应的新闻以新闻id的名字命名生成txt文件。

	badlink.txt包含了失败的链接id。

	processId.txt包含了爬过的新闻的id。

	如果程序中断，重新运行：

	```
	python getNewsContent.py
	```

	会根据processId.txt检测已经爬过的新闻，以便接着上次继续。

	log文件记录的日志信息，可以查询某链接失败的原因。

	每个股票结束后会重新过滤失败的链接，直到两次得到的失败链接数目一致。


	文件结构为：
```
NewsContent
----SH000001
--------2016-01-01-12-23-23.log
--------badlink.txt
--------processid.txt
--------32432442.txt
--------...
----SZ400002
--------...
----SH900000
--------...
```
* 运行

```
python getNewsContent.py r [stockid]
```

或者

```
python getNewsContent.py retry [stockid]
```

如果不加stockid参数，会重新过滤一遍所有股票失败链接。

如果加了stockid参数，过滤指定id的失败链接。

其中的失败链接是从badlink中读取的。

* 运行

```
python getNewsContent.py -rf [stockid]
```


如果不加stockid参数，会重新过滤一遍所有股票失败链接。

如果加了stockid参数，过滤指定id的失败链接。

其中的失败链接是（全部链接－本地已经下载下来的链接）不从badlink中读取。

*[可选] countnum.py

功能:

输入
```python countNum.py stockId```
例如 
```python countNum.py SZ000001```

将会自动计算已经爬的新闻加上badlink的新闻数量是否和原xsl文件数量一致

如果一致显示：complete

如果不一致，将会显示少了的新闻的message_id。

如果直接输入```python countNum.py ```后面不带参数

则会自动计算NewsContent文件夹里的所有股票。


* 更新流程

重复运行一遍上述步骤。

先```python XueqiuNews.py```再 ```python getNewsContent.py s```

