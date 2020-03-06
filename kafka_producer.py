import pandas as pd
import numpy as np
import json

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

ticker = 'TSLA'

#TO-DO: time data send every afternoon at 7pm 
data = get_price(ticker)
producer.send(ticker, data)
producer.flush()


