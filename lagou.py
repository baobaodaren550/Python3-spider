from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import *
import json,urllib,re,pymysql,collections,string

#解析Json数据
def get_Json(url):
	req = urllib.request.Request(url)
	req.add_header('User-Agent','Mozilla/5.0')
	response = urlopen(req).read().decode('utf-8')
	responseJson = json.loads(response)
	return responseJson

#获取招聘的详细信息
def get_infos(responseJson):
	infos = responseJson['content']['positionResult']['result']
	details = []
	for info in infos:
		detail = {}
		detail['company'] = info['companyFullName']
		detail['salary'] = info['salary']
		detail['positionName'] = info['positionName']
		detail['education'] = info['education']
		detail['financeStage'] = info['financeStage']
		detail['jobNature'] = info['jobNature']
		detail['workYear'] = info['workYear']
		linkNum = info['positionId']
		detail['url'] = 'http://www.lagou.com/jobs/{i}.html'.format(i=linkNum)
		details.append(detail)
		
	return details

#再原有信息基础上添加详细的地址信息
def get_adress(details):
	c_address = {}
	details1 = []
	for detail in details:
		detail = collections.OrderedDict(detail)
		url = detail['url']
		req = urllib.request.Request(url)
		req.add_header('User-Agent','Mozilla/5.0')
		html = urlopen(req)
		bsObj = BeautifulSoup(html)
		address = bsObj.find('div',class_='work_addr').text
		address = re.sub('\n+','',address)
		address = re.sub(' +','',address)
		address = re.sub('-','',address)
		detail['address'] = address
		details1.append(detail)
		
	return details1

#利用百度地图api将地址转化为坐标，并获取家到公司的距离及时间，并将所有信息输出到mysql	
def home_work(c_address):
	for c_addr in c_address:
		place = c_addr['address']
		url2 = 'http://api.map.baidu.com/place/v2/search?q={i}&region=深圳&output=json&ak=[百度地图api秘钥]'.format(i=place)#秘钥去官网申请一个就好了
		url2 = change_url(url2)#处理含有中文的url
		coordinate2 = get_Json(url2)
		lat2 = coordinate2['results'][0]['location']['lat']#获取纬度
		lng2 = coordinate2['results'][0]['location']['lng']#获取经度
		url1 = 'http://api.map.baidu.com/place/v2/search?q={i}&region=深圳&output=json&ak=[百度地图api秘钥]'.format(i=home)
		url1 = change_url(url1)
		coordinate1 = get_Json(url1)
		lat1 = coordinate1['results'][0]['location']['lat']
		lng1 = coordinate1['results'][0]['location']['lng']
		url3 = 'http://api.map.baidu.com/direction/v2/transit?origin={},{}&destination={},{}&ak=[百度地图api秘钥]'.format(lat1,lng1,lat2,lng2)
		coordinate3 = get_Json(url3)
		pathTime = coordinate3['result']['routes'][0]['duration']#获取家到公司时间
		pathTime = str(pathTime//60)+'分钟'
		pathDistance = str(coordinate3['result']['routes'][0]['distance']/1000)+'公里'#获取家到公司距离
		cur.execute('INSERT INTO hj(company,salary,time,distance,workYear,positionName,jobNature,education,financeStage) \
		values (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")',(c_addr['company'],c_addr['salary'],pathTime,pathDistance,c_addr['workYear'],c_addr['positionName'],c_addr['jobNature'],c_addr['education'],c_addr['financeStage'],))
		cur.connection.commit()
	
				
#对含有中文url进行处理
def change_url(url):
		url = quote(url,safe=string.printable)
		return url


def main():
	pn = 1
	for pn in range(1,6):#抓取前5页数据
		url = 'http://www.lagou.com/jobs/positionAjax.json?&city=深圳&first=true&pn={i}&kd={j}'.format(i=pn,j=job)
		url = change_url(url)
		rJson = get_Json(url)
		geturl = get_infos(rJson)
		c_adress = get_adress(geturl)
		home_work(c_adress)
		pn = pn + 1
	cur.close()
	conn.close()	
		
if __name__ == '__main__':
	home = '白石洲'	#家的位置
	job = '爬虫'#什么工作
	conn = pymysql.connect(host='127.0.0.1',user='root',passwd='password',charset='utf8')#连接数据库
	cur = conn.cursor()
	cur.execute('USE scraping')#使用数据库，当前scraping
	main()	
	