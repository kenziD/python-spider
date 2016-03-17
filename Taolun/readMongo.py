#coding=utf-8
'''
function:读取所有表情的个数；
		 计算讨论text文字数。

运行完taolun.py后，后台mongod不要关闭
'''

positive = [u"笑 ",
			u"大笑",
			u"鼓鼓掌",
			u"俏皮",
			u"加油",
			u"赚大了",
			u"牛",
			u"害羞",
			u"干杯",
			u"赞成",
			u"很赞",
			u"傲",
			u"心心 ",
			u"献花花"]
negative = [u"怒了",
			u"哭泣",
			u"好逊",
			u"跪了",
			u"不屑",
			u"摊手",
			u"为什么",
			u"滴汗",
			u"好失望",
			u"困顿",
			u"亏大了",
			u"好困惑",
			u"关灯吃面",
			u"呵呵傻逼",
			u"割肉",
			u"卖身",
			u"吐血",
			u"可怜",
			u"抠鼻",
			u"囧",
			u"不赞",
			u"围观",
			u"不说了",
			u"想一下",
			u"好困惑",
			u"心碎了",
			u"一坨屎"]
positiveindex = 0
negativeindex = 0
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client['taolun']
collection = db['discuss']

ALL = db.withtime.find({})
newlist = []
print ALL
for i in ALL:
	print type(i)
	
	
	for item in i["list"]:
		newdict = {}
		# newdict["img"] = []
		if "img" in item.keys():
			for one in item["img"]:
				newdict["img"] = []

				newdict["img"].append(one)
			newdict["time"] = item["time"][0:9]
		if "comment" in item.keys():
			for comment in item["comment"]:
				if "img" in comment.keys():
					newdict["time"] = item["time"][0:9]
					if "img" in newdict.keys():
						for one in comment["img"]:
							newdict["img"].append(one)
					else:
						newdict["img"] = []
						for one in comment["img"]:
							newdict["img"].append(one)
		if newdict:
			newlist.append(newdict)
# print newlist
count = 0
negativeall = 0
positiveall = 0
for i in newlist:
	negativeindex = 0
	positiveindex = 0
	for item in i["img"]:
		print item
		count = count+1
		if item in positive:
			positiveindex = positiveindex + 1
			positiveall = positiveall+1
		if item in negative:
			negativeindex = negativeindex + 1
			negativeall = negativeall+1
	# if float((positiveindex+negativeindex)):
	i["positive"] = positiveindex
	i["negative"] = negativeindex	
import json
print count
print positiveall
print negativeall
# with open("feel.json", "w") as outfile:
#     json.dump(newlist, outfile, indent=4)

			# if k == "img":
			# 	print v
# imgintext = db.discuss.aggregate([{ "$project":{"list.img":1,"_id":0}},{"$unwind":"$list"},{"$match":{"list.img":{"$exists":"true"}}}])
# count = 0
# for i in imgintext:
# 	for face in i["list"]["img"]:
# 		if face in positive:
# 			print face
# 			positiveindex = positiveindex + 1
# 		if face in negative:
# 			negativeindex = negativeindex + 1
# 		count= count+1
# print "讨论内容含表情的总个数",count

# count2 = 0
# imgincomment = db.discuss.aggregate([{ "$project":{"list.comment":1,"_id":0}},{"$unwind":"$list"},{"$unwind":"$list.comment"},{"$match":{"list.comment.img":{"$exists":"true"}}}])
# for i in imgincomment:
# 	for face in i["list"]["comment"]["img"]:
# 		# print face
# 		if face in positive:
# 			print face
# 			positiveindex = positiveindex + 1
# 		if face in negative:
# 			negativeindex = negativeindex + 1
# 		count2 = count2+1

# print "评论内容含表情的总个数",count2
# print "共计",count2+count

# print "积极",positiveindex
# print "消极",negativeindex
# text = db.discuss.aggregate([{"$project":{"list.text":1,"_id":0}},{"$unwind":"$list"},{"$match":{"list.text":{"$exists":"true"}}}])
# lengthall =0
# for i in text:
# 	# print i
# 	length =  len(i["list"]["text"])
# 	lengthall += length
# print "text内的总字数",lengthall
