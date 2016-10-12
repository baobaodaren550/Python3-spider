# -*-coding:utf-8 -*-
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json,re,urllib,io,sys,pymysql,requests,time,operator


def get_req(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','Mozilla/5.0')
	return req

def get_json(req):
	html = urlopen(req).read().decode('utf-8')
	response = json.loads(html)
	return response
	
#获取热门评论
def get_comments(url,comm):
	session = requests.Session()
	headers = {'User-Agent':'Mozilla/5.0','Cookie': 'bid=cE4SGsqW3wQ; __utma=30149280.1702577288.1473607314.1476281064.1476285483.19;\
	__utmz=30149280.1476221734.14.11.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1476285481\
	%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3D9CJZY30bII-xMIeFbLbnp7KKmTsiBKdhyf9802ruXIojscRM4BUjA2KapOw73O-3%26wd%3D%26eqid%3D\
	d5589629000259710000000557fd5b1e%22%5D; _pk_id.100001.4cf6=5ffa4fb1f27ce046.1475076127.10.1476286066.1476282375.; __utma=223695111.67\
	0901478.1475076129.1476281064.1476285483.10; __utmz=223695111.1476221734.5.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ll="118282\
	"; ap=1; _vwo_uuid_v2=AEDCB12BBD4EB0F45813CB043EF62DFC|3099cca00070a647ded98638b9684bdc; __utmc=30149280; __utmc=223695111; _pk_ses.10\
	0001.4cf6=*; __utmb=30149280.2.10.1476285483; __utmb=223695111.0.10.1476285483; ps=y; dbcl2=" 145659632:3V6C/zB5DmE"; ck=okM3; push_no\
	ty_num=0; push_doumail_num=0; __utmt=1; __utmv=30149280.14565','Referer': 'https://movie.douban.com/'}
	req = session.get(url,headers=headers)
	
	time.sleep(2)
	
	bsObj = BeautifulSoup(req.text)
	infos = bsObj.find('div',id ='comments')
	comments1 = infos.find_all('p',class_='')
	
	for comment in comments1:
		comm.append(comment.text)
	return comm

#对获取的数据进行清洗
def cleanData(comm):
	Ncomments = ""
	for subcomm in comm:
		if type(subcomm) is str:
			subcomm = re.sub('[^\u4e00-\u9fa5]','',subcomm) #只保留中文，其他去掉
			Ncomments = Ncomments+subcomm
			character = re.findall('[\u4e00-\u9fa5]{1}',Ncomments)#将字符串拆分成单个字
		continue
	output = {}
	for i in range(len(character)-1):
		ngramTemp = ''.join(character[i:i+2])#相邻两个字，两两组合成一个新的字符串
		if ngramTemp not in output:#统计字符串出现的次数
			output[ngramTemp] = 0
		output[ngramTemp] +=1
	return output

def main():
	url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=200&page_start=0' #豆瓣前200热门电影的网址
	a = get_req(url)
	b = get_json(a)
	infos = b['subjects']
	lists = []
	titles = []
	conn = pymysql.connect(host='127.0.0.1',user='root',passwd='password',charset='utf8')
	cur = conn.cursor()
	cur.execute('USE scraping')
	
	for info in infos:
		lists.append(info['id'])
		titles.append(info['title'])
	for i in range(len(lists)):
		a = titles[i]
		comm = []
		
		for j in range(10):
			url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20'.format(lists[i],j*20)#获取目标电影的评论网址
			comm1 = get_comments(url,comm)
			comm.append(comm1)
			j = j+1
			time.sleep(2)
		data = cleanData(comm)	
		sortedData = sorted(data.items(),key=operator.itemgetter(1),reverse=True)#对字符串出现次数进行排序
		
		for x in sortedData:
			if x[1]>2:
				cur.execute('INSERT INTO  douban (title,keyword,frequency) values (\"%s\",\"%s\",\"%s\")',(a,x[0],x[1]))#导入数据库	
				conn.commit()
		i = i+1
	
	cur.close()
	conn.close()
	
if __name__ == '__main__':
	main()