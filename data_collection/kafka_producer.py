import pandas as pd
import json
import schedule
import time
import argparse
import datetime

from kafka import KafkaProducer
from alpha_vantage.timeseries import TimeSeries

#alpha vantage stock market API
#https://www.alphavantage.co/documentation/
av_api_key = '8K3SKYS58V6GDVES'
ts = TimeSeries(key = av_api_key, indexing_type='date')

producer = KafkaProducer(bootstrap_servers='localhost:9092',
						value_serializer=lambda v: json.dumps(v).encode('utf-8'),
						retries=5)
	

def get_price(symbol, historic=False):
	'''
	Desc: retrieve closing stock data for a certain company
	@param: ticker - the symbol that the company uses (ex. 'TSLA' for Tesla)
	@param: historic - boolean, send all data from company stock
	'''
	'''
	Data looks like this in json
	{
		'date' : {
			'1. open' : string $,
			'2. high' : string $,
			'3. low' : string $,
			'4. close' : string $,
			'5. volume' : string val
		}
	}
	Meta-data looks like this
	{
		'1. Information': 'Daily Prices (open, high, low, close) 
							and Volumes',
		'2. Symbol': string Ticker,
		'3. Last Refreshed': today's date 'year-month-day',
		'4. Output Size': 'Full size',
		'5. Time Zone': 'US/Eastern'
	}

	'''
	try:
		data, meta_data = ts.get_daily(symbol, outputsize='full')
	except Exception as e:
		#stock doesn't exist, error out
		print('ERROR: %s; symbol: %s'%(e,symbol))
		return {'API_ERROR':[str(e)]}

	#returns today's data as a lsit of tuple(s):
	#  (date, open, high, low, close, volume) for kafka consumer
	# "." in cassandra is for keyspace and table, so we remove it.
	if "." in symbol:
		symbol = symbol.replace(".","")
	return_data = {symbol:[]}
	if not historic:
		todays_date = meta_data['3. Last Refreshed']
		return_data[symbol] = [((todays_date,)+tuple(data[todays_date].values()))]
	else: 
		print('data size: %d\n'%len(data.keys()))
		for date in data.keys():
			
			return_data[symbol].append(((date,)+tuple(data[date].values())))
	return return_data

def send_price_to_kafka(company_symbols, historic=False):
	'''
	Desc: sends stock price to kafka consumer 
	with 5 call/min;500 call/say limit
	@param: company_symbols - tuple of strings; list of stocks to fetch
	@param: historic - boolean, send full stock history
	'''
	for symbol in company_symbols:
		print("sending %s "%symbol)
		producer.send(symbol, get_price(symbol, historic))
		producer.flush()
		time.sleep(15)

if __name__ == "__main__":

	#set args
	parser = argparse.ArgumentParser()
	parser.add_argument('--update', type=bool, default=False, help='send historic time series of each company to kafka')
	parser.add_argument('--csv_file', type=str, help='filename(string) - CSV of companies to send; need column \'Symbol\'')	
	parser.add_argument('--row_start', type=int, default=0, help='fileval_start - (int) start at a particular row in the file')
	#parse args
	args = parser.parse_args()
	update_bool = args.update_bool
	filename = args.csv_file
	start_pt = args.row_start

	print("set: update_bool to %s\nset: filename to %s"%(str(update_bool), filename))

	#reading company list to send
	stocks = pd.read_csv(filename)[['ID','Symbol']]
	stock_symbols = stocks.loc[start_pt:]
	#update check
	if update_bool:
		send_price_to_kafka(stock_symbols['Symbol'], historic=True)

	historic = False
	#schedule append every day at 7:00pm MST
	#TODO: change to UTC
	schedule.every().day.at("19:00").do(send_price_to_kafka, stock_symbols, historic)
	#500 requests per day at 5 calls per minute
	while True:
		schedule.run_pending()
		time.sleep(1)



	




