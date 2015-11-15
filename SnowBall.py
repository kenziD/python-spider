import urllib2
import urllib
import cookielib
import json
import time
from pyExcelerator import *

w = Workbook()     #创建一个工作簿
ws = w.add_sheet('Hey, Xueqiu')     #创建一个工作表

# 表头
ws.write(0,0,u'Name')
ws.write(0,1,u'Screen Name')
ws.write(0,2,u'Follower')
ws.write(0,3,u'Daily Gain')
ws.write(0,4,u'Monthly Gain')
ws.write(0,5,u'Total gain')
ws.write(0,6,u'Net value')
ws.write(0,7,u'industry')
ws.write(0,8,u'Time')
ws.write(0,9,u'Stock Name')
ws.write(0,10,u'Stock ID')
ws.write(0,11,u'From')
ws.write(0,12,u'To')

count=50
row = 1
row_for_stock_name = 1

# 获得最具人气的url链接
def GET_hot_url_param(url,count,page):
	param = {}
	param['market'] = 'cn'
	param['category'] = '10'
	param['count'] = str(count)
	param['page'] = str(page)
	data = urllib.urlencode(param)
	# 得到完整的GET请求url
	geturl = url + "?"+data
	return geturl

def get_hot_json(count,page):
	url = 'http://xueqiu.com/cubes/discover/rank/cube/list.json'
	geturl = GET_hot_url_param(url,count,page)
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	cookie = 's=uol12jm3bh; xq_a_token=f860bbbc3cbfcd5d573ac2dd2aeaf4187fec480b; xqat=f860bbbc3cbfcd5d573ac2dd2aeaf4187fec480b; xq_r_token=829131d4b4c68a17602bdaa8b2ff675dd6b6db81; xq_token_expire=Fri%20Dec%2004%202015%2014%3A52%3A18%20GMT%2B0800%20(CST); xq_is_login=1; snbim_minify=true; bid=f6aaa1833b723e0ada45b5116ec0545e_igrld6nh; __utma=1.653547628.1447051964.1447051964.1447054602.2; __utmc=1; __utmz=1.1447051964.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
	headers = {
	'User-Agent' : user_agent,
	'Cookie': cookie}
	req = urllib2.Request(geturl,headers = headers)
	response = urllib2.urlopen(req)
	# raw-html(json here)
	html_json = response.read().decode("utf-8")
	return html_json

def write_xsl():
	hot_json = get_hot_json(20,1)
	decode_hot_json = json.loads(hot_json)
	total_count = decode_hot_json['totalCount']
	max_page = decode_hot_json['maxPage']
	i = 1
	for page_index in range(max_page):
		try:
			hot_json = get_hot_json(count,page_index+1)
			decode_hot_json = json.loads(hot_json)
		except:
			print "Exception!!!!!!!!!!!!!!!!!!!!!!!!!!"
			continue
		stock_row = 1
		for item in decode_hot_json['list']:
			name = item['name']
			ws.write(stock_row,0,name)
			# 变量
			screen_name = item['owner']['screen_name']
			ws.write(stock_row,1,screen_name)
			# 变量
			follower = item['follower_count']
			ws.write(stock_row,2,follower)
			# 变量
			daily_gain = item['daily_gain']
			ws.write(stock_row,3,daily_gain)
			# 变量
			monthly_gain = item['monthly_gain']
			ws.write(stock_row,4,monthly_gain)
			# 变量
			total_gain = item['total_gain']
			ws.write(stock_row,5,total_gain)
			# 变量
			net_value = item['net_value']
			ws.write(stock_row,6,net_value)
			# 变量
			tag = item['tag']
			if(tag == None):
				Str_tag = 'None'
			else:
				Str_tag = ' '.join(tag)
			ws.write(stock_row,7,Str_tag)			
			cube_symbol = item['symbol']
			print i,cube_symbol
			stock_row = write_history(cube_symbol)
			i = i+1


# 时间戳转换函数
def timestamp_datetime(value):
	format = '%Y-%m-%d %H:%M:%S'
	# value为传入的值为时间戳(整形)，如：1332888820
	value = time.localtime(value)
	## 经过localtime转换后变成
	## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
	# 最后再经过strftime函数转换为正常日期格式。
	dt = time.strftime(format, value)
	return dt

def GET_history_url_param(url,cube_symbol,count,page):
	param = {}
	param['cube_symbol'] = str(cube_symbol)
	param['count'] = str(count)
	param['page'] = str(page)
	data = urllib.urlencode(param)
	# 得到完整的GET请求url
	geturl = url + "?"+data
	return geturl

def get_history_json(cube_symbol,count,page):
	url = 'http://xueqiu.com/cubes/rebalancing/history.json'
	geturl = GET_history_url_param(url,cube_symbol,count,page)
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	cookie = 's=1li917ztof; xq_a_token=f860bbbc3cbfcd5d573ac2dd2aeaf4187fec480b; xq_is_login=1; bid=f6aaa1833b723e0ada45b5116ec0545e_ignqeaxq; __utma=1.811282952.1446818164.1446818164.1446818164.1; __utmc=1; __utmz=1.1446818164.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic'
	headers = {
	'User-Agent' : user_agent,
	'Cookie': cookie}
	try:
		req = urllib2.Request(geturl,headers = headers)
		response = urllib2.urlopen(req)
		# raw-html(json here)
		html_json = response.read().decode("utf-8")
		return html_json
	except Exception, e:
		print "get history Exception"


# cookie = cookielib.CookieJar()
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
# urllib2.install_opener(opener)

def write_history(cube_symbol):
	print cube_symbol,'loading'
	global row
	global row_for_stock_name
	global count
	decode_history_json = json.loads(get_history_json(cube_symbol,40,1))
	total_count = decode_history_json['totalCount']
	page = decode_history_json['maxPage']
	for page_index in range(page):
		try:
			# print 'page',page_index+1,"load...."
			# print count
			decode_history_json = json.loads(get_history_json(cube_symbol,count,page_index+1))
			# print 'page',page_index+1,"json_done"
		except :
			print('there is an Exception')
			continue
		# print "start parse"
		for item1 in decode_history_json['list']:
			update_time_stamp = long(str(item1['created_at'])[0:10])
			update_time = timestamp_datetime(update_time_stamp)
			ws.write(row,8,update_time)
			row = row+len(item1['rebalancing_histories'])
			for element in item1['rebalancing_histories']:
				ws.write(row_for_stock_name,9,element['stock_name'])
				ws.write(row_for_stock_name,10,element['stock_symbol'])
				# 返回值可能为none 其type也为nonetype 要处理成0，否则表格写不进去
				if(element['prev_weight'] is None):
					element['prev_weight'] = 0
				ws.write(row_for_stock_name,11,element['prev_weight'])
				ws.write(row_for_stock_name,12,element['target_weight'])
				row_for_stock_name = row_for_stock_name+1
	return row_for_stock_name

w.save('Xueqiu.xls')     #保存
