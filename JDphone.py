from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.PhantomJS()
for i in range(0,10):
	i+=1
	url = 'http://list.jd.com/list.html?cat=9987,653,655&page={}'.format(i)
	driver.get(url)
	bs = BeautifulSoup(driver.page_source)
	lists = bs.find_all('li',class_='gl-item')

	with open('G://na1.txt','a') as f:
	
		for list in lists:
			s = {}
			name = list.find('div',class_='p-name').find('em').text
			price = list.find('div',class_='p-price').find('i').text
			s['name'] = name
			s['price'] = price
			f.write(str(s)+'\n')
		
		f.closed
driver.quit()