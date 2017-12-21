from urllib import urlopen
from bs4 import BeautifulSoup
import json
import datetime

def get_cur_price(currency_name, verbose=True):
	if currency_name == "cash":
		return 1.0
	url = 'https://coinmarketcap.com/currencies/{}/'.format(currency_name)
	html = urlopen(url).read()
	soup = BeautifulSoup(html, 'html.parser')
	price = soup.find("span", {"class": "text-large2"}).string.strip()
	if verbose:
		print "Price for {} is currently ${}".format(currency_name, price)
	return float(price)


def log_wallet_value(wallet_sum, file_name="wallet_log.txt"):
	now = datetime.datetime.now()
	f = open(file_name,"a+")
	f.write("{} ---- {}\n".format(now, wallet_sum))


def main(log=True):
	# load the current holdings
	data = json.load(open('hodl.json'))

	# initialize the wallet sum
	wallet_sum = 0.0
	
	# get current price * holdings for each currency and add to wallet sum
	for c in data.keys():
		wallet_sum = wallet_sum + data[c] * get_cur_price(c)

	print "\nWallet Value is ${}".format(wallet_sum)
	
	if log:
		log_wallet_value(wallet_sum)


if __name__ == "__main__":
    main()



