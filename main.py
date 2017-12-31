import urllib2
from bs4 import BeautifulSoup
import json
import datetime
import psycopg2
import argparse
import time

def create_db_connection():
	print "creating db connection"
	config = json.load(open('config.json'))
	print "CONFIG", config

	try:
	    return psycopg2.connect("dbname={} user={} host={} password={}".format(config['dbname'], config['user'], config['host'], config['password']))
	except:
	    print "Unable to connect to the database"

def save_cur_price(currency, price, cursor=None):
	print "adding {} price to queue".format(currency)
	query = "insert into crypto_counter.cc_current_price (currency, price) values ('{}',{});"
	cursor.execute(query.format(currency, price))


def save_wallet_balance(balance, cursor=None):
	print "wallet balance to queue"
	query = "insert into crypto_counter.cc_wallet_balance (balance) values ({});"
	cursor.execute(query.format(balance))


def get_cur_price(currency, verbose=True, cursor=None):
	if currency == "cash":
		return 1.0
	url = 'https://coinmarketcap.com/currencies/{}/'.format(currency)
	request_headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }

	request = urllib2.Request(url, headers=request_headers)
	html = urllib2.urlopen(request).read()

	soup = BeautifulSoup(html, 'html.parser')
	price = soup.find("span", {"class": "text-large2"}).string.strip()
	if verbose:
		print "Price for {} is currently ${}".format(currency, price)
	if cursor is not None:
		save_cur_price(currency, price, cursor=cursor)

	return float(price)


def log_wallet_value(wallet_sum, file_name="wallet_log.txt"):
	now = datetime.datetime.now()
	f = open(file_name,"a+")
	f.write("{} ---- {}\n".format(now, wallet_sum))

def get_holdings(cursor):
	cursor.execute("SELECT * FROM crypto_counter.holdings;")
	return cursor.fetchall()

def process_run():
	conn = create_db_connection()
	cursor = conn.cursor()

	while True:
		# load the current holdings
		data = get_holdings(cursor)

		# initialize the wallet sum
		wallet_sum = 0.0
		# get current price * holdings for each currency and add to wallet sum
		for c in data:
			currency = c[1]
			holdings = float(c[2])
			print "collecting data for {}".format(currency)
			wallet_sum = wallet_sum + holdings * get_cur_price(currency,cursor=cursor)
			time.sleep(5)

		print "Wallet Value is ${}".format(wallet_sum)

		save_wallet_balance(wallet_sum, cursor=cursor)

		print "SAVING TO DATABASE"
		conn.commit()
		time.sleep(600)

def single_run(log=True, save=False):

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
	parser = argparse.ArgumentParser()

	parser.add_argument('-p', '--process', dest='process', help='Should the app run as a background process?', type=bool, default=False)
	parser.add_argument('-q', '--quiet', dest='quiet', help='Stop the app from print whats going on', type=bool, default=True)

	op = parser.parse_args()

	run_as_process = op.process
	verbose = not op.quiet

	if run_as_process:
		process_run()
	else:
		single_run()



