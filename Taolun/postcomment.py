import requests
import json
import re
# url = 'http://xueqiu.com/service/comments?filtered=true&id=65304808&callback=jQuery183006020978232845664_1456557735936'
# url = 'http://xueqiu.com/service/comments?filtered=true&id=65168631'
# url = 'http://xueqiu.com/service/comments?id=65160680'

def getCommentUrl(discussId):
    url = 'http://xueqiu.com/service/comments?id='+discussId+''
    return url 
url = getCommentUrl('65168631')
userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
HEADERS = {
    'User-Agent': userAgent
}

r = requests.post(url,headers=HEADERS)
# print r.content

html = r.content
reply = json.loads(html)

for i in xrange(len(reply['comments'])):
    comment = reply['comments'][i]['text']
    pattern = re.compile(r'<img.*?alt="\[(.*?)\]".*?>')
    img = pattern.findall(comment)
    face = []
    if img:
        for feel in img:
            face.append(feel)
    pattern = re.compile(r'<.*?>')
    comment = pattern.sub('',comment)
    usr = reply['comments'][i]['user']['screen_name']
    replyTo =  reply['comments'][i]['reply_screenName']
    comment_dict = {"comment":comment,"usr":usr}
    if replyTo:
        comment_dict.update({"replyTo":replyTo})
    if img:
        comment_dict.update({"img":face})
    print comment_dict
    # print comment



