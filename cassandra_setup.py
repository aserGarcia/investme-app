#import cassandra

#dictionary of {'ticker_name' : {'name': company_name, 'sector': sector}}
sp500 = {}
with open('SP500.csv', 'r') as spFile:
	for row in spFile:
		row_list = row.strip('\n').split(',')
		sp500[row_list[0]] = {'name':row_list[1], 'sector':row_list[2]}

		
print(sp500['WLTW']['name'])
