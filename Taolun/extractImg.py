#coding=utf-8
# text = u'"<a href=\"http://xueqiu.com/S/SZ002163\" target=\"_blank\">$中航三鑫(SZ002163)$</a> <img src=\"//assets.imedao.com/images/face/25weep.png\" title=\"[哭泣]\" alt=\"[哭泣]\" height=\"24\" />果然高风险，装死了"'
# text = u'2016.2.24----1.井神股份竞价开的太弱，所以竞价直接出了万里石，万幸还赚半个点<img src=\"//assets.imedao.com/images/face/09lose.png\" title=\"[亏大了]\" alt=\"[亏大了]\" height=\"24\" />。2.如意集团妖到家了，假机构砸不死，承接力太强，妖气十足，有强庄在里面兴风作雨，16号就关注了，不过即便买了真心拿不住，强者恒强，为嘛不敢追着买，强庄换手率不高不低，吾日三省吾身噫<img src=\"//assets.imedao.com/images/face/25weep.png\" title=\"[哭泣]\" alt=\"[哭泣]\" height=\"24\" />3.浙江富润与中航三鑫，差别咋这么大呢，好吧，以后能上三板不上两板<img src=\"//assets.imedao.com/images/face/12hand.png\" title=\"[摊手]\" alt=\"[摊手]\" height=\"24\" />。4.上了开板新股东方时尚，作死的节奏吗<img src=\"//assets.imedao.com/images/face/25weep.png\" title=\"[哭泣]\" alt=\"[哭泣]\" height=\"24\" />5.如意集团上海普天强庄股，浙江金科人气股，强者恒强，不怕人不接盘！！！5.国企改什么鬼'
text = u'【2016.02.23】【大爷打板笔记】<br /><br />① 先说昨天看好的几只票：<a href=\"http://xueqiu.com/S/SZ002226\" target=\"_blank\">$江南化工(SZ002226)$</a>真是亮瞎了我的狗眼，居然封得最死，不愧是VR/AI新贵；<a href=\"http://xueqiu.com/S/SZ000020\" target=\"_blank\">$深华发A(SZ000020)$</a>早盘看样子要开板，没敢排，开板后又快速回封，然后我才反应过来：它相对于<a href=\"http://xueqiu.com/S/SZ000019\" target=\"_blank\">$深深宝A(SZ000019)$</a>的近期涨幅还差得多，理应还有上涨空间，于是赶紧排板，可惜一直到收盘剩2万手封单我都没有排到；<a href=\"http://xueqiu.com/S/SZ002163\" target=\"_blank\">$中航三鑫(SZ002163)$</a>今天高位放量，无视了。<br />② <a href=\"http://xueqiu.com/S/SZ002348\" target=\"_blank\">$高乐股份(SZ002348)$</a>真是个好板，可惜也不给排到的机会，郁闷。明天继续关注。<br />③ 今天这么多涨停票我都能踏空，尤其错过早盘<a href=\"http://xueqiu.com/S/SZ000020\" target=\"_blank\">$深华发A(SZ000020)$</a>的买入契机，难免有点自乱阵脚了，于是，下午跟随d6大神追了<a href=\"http://xueqiu.com/S/SZ000019\" target=\"_blank\">$深深宝A(SZ000019)$</a>，结果被浅埋，明天再看了。'
import re
pattern = re.compile(r'<img.*?alt="\[(.*?)\]".*?>')
img = pattern.findall(text)
if img:
	print "have"
	for i in img:
		print i
else:
	print "no"
feel = ["fa"]
if feel:
	print "hah"