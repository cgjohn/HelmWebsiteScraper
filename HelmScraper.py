# Checks the helm sale page for any changes and if there are 
# changes, emails them to me
# https://helmboots.com/collections/sale
import requests
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import json
import re


# caching
CACHE_FNAME = 'helm_sale_page.json'
formatted_key = "Helm_Site"
sale_items = "sale_items"

try:
	cache_file = open(CACHE_FNAME, 'r', encoding = 'utf-8')
	cache_contents = cache_file.read()
	CACHE_DICTION = json.loads(cache_contents)
	cache_file.close()
except:
	CACHE_DICTION = {}
	CACHE_DICTION[formatted_key] = ""
	CACHE_DICTION[sale_items] = ""

def get_content(text):
	items = []
	prices_before = []
	prices_after = []

	response_tuples = []

	soup = BeautifulSoup(text,"html.parser")

	items = soup.find_all("div",{"class":"grid-view-item__title"})
	prices_before = soup.find_all("s", {"class": "product-price__price"})
	p_after = soup.find_all("span", {"class": "product-price__sale"})

	# getting just sale price from p_after item 
	for p in p_after:
		price = re.findall('\$\d+.\d+', p.text)
		for each in price:
			prices_after.append(each)

	#creating a tuple for each sale item (name, og price, sale price) 
	for i in range(len(items)):
		r = (items[i].text, prices_before[i].text, prices_after[i])
		response_tuples.append(r)
	return response_tuples

# get web page
url = "https://helmboots.com/collections/sale"
# set the headers like we are a browser,
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# download the homepage
response = requests.get(url, headers=headers)
responseText = response.text
# parse the downloaded homepage and grab all text, then,

if CACHE_DICTION[formatted_key] != responseText:
	response_tup = get_content(responseText)

	# creating new sale section,
	new_msg = "--Shoe Name --- OG Price --- Sale Price\n"
	for r in response_tup:
		t = ' '.join(r)
		new_msg += "   "
		new_msg += t
		new_msg += '\n'
	# No new items on sale so do nothing
	if new_msg == CACHE_DICTION[sale_items]:
		print("no changes to sale items")
	# creating a new email message since cale items changed
	else:
		print("sale items changed")
		# creating entire email msg - old sale + new sale items
		msg = "----Previous Sale Items----\n"
		msg += "\n"
		if sale_items in CACHE_DICTION:
			msg += CACHE_DICTION[sale_items]
		
		msg += "\n"
		msg += "----Current Sale Items----\n"
		msg += "\n"
		msg += new_msg
		msg += "\n"
		msg += "check them out here -> "
		msg += url

		# Storing vals into Cache file
		CACHE_DICTION[formatted_key] = responseText
		CACHE_DICTION[sale_items] = new_msg
		cache_file = open(CACHE_FNAME, 'w', encoding = 'utf-8')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()

		# set the 'from' address,
		fromaddr = 'conjohn37@gmail.com'
		# set the 'to' addresses,
		toaddrs  = ['cjohnston1496@gmail.com']

		# setup the email server,
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		# add my account login name and password,
		server.login("conjohn37@gmail.com", "-password-")
		# send the email
		server.sendmail(fromaddr, toaddrs, msg)
		# disconnect from the server
		server.quit()
		print("email sent")

else:
	print("no changes to the site")


