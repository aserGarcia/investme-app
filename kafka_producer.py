import pandas as pd
import numpy as np
import json
import schedule
import time

from kafka import KafkaProducer
from alpha_vantage.timeseries import TimeSeries


av_api_key = '8K3SKYS58V6GDVES'
ts = TimeSeries(key = av_api_key, indexing_type='date')

producer = KafkaProducer(bootstrap_servers='localhost:9092',
						value_serializer=lambda v: json.dumps(v).encode('utf-8'),
						retries=5)
	

def get_price(ticker):
	'''
	desc: retrieve closing stock data for a certain company
	@param: ticker - the symbol that the company uses (ex. 'TSLA' for Tesla)
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
	data, meta_data = ts.get_daily(ticker)
	#returns today's data
	todays_date = meta_data['3. Last Refreshed']
	return data[todays_date]

def send_price_to_kafka(tickers):
	'''
	Desc: sends stock price to kafka consumer 
	with 5 call/sec;500 call/say limit
	@param: tickers - tuple of strings; list of stocks to fetch
	'''
	for ticker in tickers:
		producer.send(ticker, get_price(ticker))
		producer.flush()
		time.sleep(15)

def test_send(ticker):
	producer.send(ticker, {'name':ticker, 'data':555.3})
	producer.flush()

if __name__ == "__main__":
	#TODO: read file of S&P 500 data
	stock_list =['TSLA', 'GOOGL']
	#schedule.every(10).seconds.do(send_price_to_kafka, ticker[0])
	#schedule.every(10).seconds.do(send_price_to_kafka, ticker[1])
	#schedule.every.day.at("19:00").do(send_price_to_kafka, ticker)
	schedule.every(1).seconds.do(test_send, stock_list)

	#500 requests per day at 5 calls per minute
	while True:
		schedule.run_pending()
		#sleep a minute and 5 seconds
		time.sleep(1)






