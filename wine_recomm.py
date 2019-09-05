from PIL import Image
from pytesseract import image_to_string
import re
import requests
from googlesearch import search as gsearch
from time import sleep
from bs4 import BeautifulSoup


def image_to_text(file):
	img = Image.open(file)
	text = image_to_string(img)
	text = text.strip()
	return text

def process_text(text):
	aList = text.split('\n')
	aList = list(filter(None, aList))

	while ' ' in aList:
		aList.remove(' ')

	wineRegex = re.compile(r'^\d{3}\s\w+')

	newList = []

	for l in aList:
		if wineRegex.search(l):
			newList.append(l)
	return newList


def create_list(_list):
	d = {'code': 0, 'title' : None, 'year' : 0, 'price':0 , 'webpage': None, 'variety': None, 'food': None, 'style': None}
	l = []

	codeRegex = re.compile(r'^\d{3}')
	titleRegex = re.compile(r'\D+')
	yearRegex = re.compile(r'\d{4}')
	priceRegex = re.compile(r'\$\d+(\s\$\d+)*')

	for i in _list:
		if codeRegex.search(i):
			m = codeRegex.search(i)
			d['code'] = m.group()
		if titleRegex.search(i):
			m = titleRegex.search(i)
			d['title'] = m.group().strip()
		if yearRegex.search(i):
			m = yearRegex.search(i)
			d['year'] = m.group()
		if priceRegex.search(i):
			m = priceRegex.search(i)
			d['price'] = m.group()
		
		l.append(d)
		d = {'code': 0, 'title' : None, 'year' : 0, 'price':0 , 'webpage': None, 'variety': None, 'food': None, 'style': None}

	return l
		
def find_best_match(a_list):
	urlRegex = re.compile(r'wine-search')
	count = 0

	for i in a_list:
		query = i.get('title', '')

		for j in gsearch(query, stop = 5):
			if urlRegex.search(j):
				link = j
				break
		i['webpage'] = link + '/' + str(i.get('year', ''))
		count += 1
		print('Found webpage number ' + str(count))
		sleep(0.1)

	return a_list

def find_wine_info(a_list):
	
	headers = {'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0','host': 'www.wine-searcher.com','Accept-Encoding': 'gzip, deflate, br'}
	count = 0

	for l in a_list:
		url = l['webpage']
		res = requests.get(url, headers = headers)
		res.raise_for_status()
		soup = BeautifulSoup(res.text, "html.parser")

		text = soup.select('div .wine-info-panel')
		info = []
		
		for t in text:
			info.append(t.text)
			info = info[0].split('\n')

		while '' in info:
			info.remove('')

		count += 1
		print('Found wine info number ' + str(count))

		grapeRe = re.compile(r'Grape/Blend')
		foodRe = re.compile(r'Food')
		styleRe = re.compile(r'Wine Style')
		
		for i in info:
			if grapeRe.match(i):
				index = info.index(i)+1
				l['variety'] = info[index]
			if foodRe.match(i):
				index = info.index(i)+1
				l['food'] = info[index]
			if styleRe.match(i):
				index = info.index(i)+1
				l['style'] = info[index]
		sleep(1)
	return a_list

def recommendation(_input, a_list):
	for l in a_list:
		if re.search('(.*)'+_input+'(.*)', l['food'],re.IGNORECASE):
			print('The wine recommendation for your meal is ' + l['title'] + '. The style is ' + l['style'] 
				+ '. The price is ' + l['price'] + '.')

text = image_to_text('./bottegalouiswinelist.jpg')
newList = process_text(text)
wineList = create_list(newList)
find_best_match(wineList)
find_wine_info(wineList)

foodList = ['Spicy Food', 'Vegetables', 'Salads', 'Parmesan', 'Mushrooms','Fish','Lamb',
			'Beef','Crab','Lobster', 'Chicken', 'Turkey']

print('What food would you like to have today? Please choose from the list or quit:')
for i in foodList:
	print(i, end = '; ')
print('\n')


while True:
	user_input = input()
	if user_input == 'quit':
		break
	else:
		recommendation(user_input,wineList)



