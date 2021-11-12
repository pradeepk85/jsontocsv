import json
import csv
from datetime import date
import os.path
import alpaca_trade_api as tradeapi
from configparser import ConfigParser
import requests
import pandas as pd

#  Alpaca connection settings
config = ConfigParser()
config.read('config.ini')
api = tradeapi.REST(config.get('alpaca', 'KEY'), config.get('alpaca', 'SECRET'))

# FMP
fmp_url = "https://financialmodelingprep.com"
fmp_rating = "/api/v3/rating/"
fmp_financial_growth = "/api/v3/financial-growth/"
stock_rating = {}
stock_open = {}
stock_close = {}

def get_fmp_rating():
    for fmp_stocks in premarket_stocks:
        query = {'apikey': config.get('fmp', 'KEY')}
        response = requests.get(fmp_url + fmp_rating + fmp_stocks['Symbol'], params=query).json()
        # response = requests.get(fmp_url + fmp_rating + 'AAPLL', params=query).json()
        if not response:
            stock_rating[fmp_stocks['Symbol']] = 'NA'
        else:
            stock_rating[fmp_stocks['Symbol']] = response[0]['rating']


#  Add CSV headers
header = ['Date', 'Symbol', 'Name', 'Price', 'Previous_Price', 'PriceChgPct', 'TotalVolumeStr', 'MarketCapStr',
          'PriceVsVwap', 'Sector', 'Industry', 'PrItems', 'Today_Open', 'Today_Close', 'Gain', 'Gain %', 'Rating']
file_exists = os.path.exists('premarket.csv')
if not file_exists:
    with open('premarket.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

today = date.today()
today_date = today.strftime("%d/%m/%Y")

premarket_stocks = json.load(open('pre-market.json'))['PRE_MARKET_GAINERS']
get_fmp_rating()

with open('premarket.csv', 'a', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    for stocks in premarket_stocks:
        data = []
        barset = api.get_barset(stocks['Symbol'], 'day', limit=1)
        bars = barset[stocks['Symbol']]
        for header_val in header:
            if header_val == 'Date':
                data.append(today_date)
                continue
            if header_val == 'PrItems':
                data.append(len(stocks[header_val]))
                continue
            if header_val == 'Today_Open':
                if bars:
                    data.append(bars[0].o)
                    stock_open[stocks['Symbol']] = bars[0].o
                else:
                    data.append(0)
                    stock_open[stocks['Symbol']] = 0
                continue
            if header_val == 'Today_Close':
                if bars:
                    data.append(bars[-1].c)
                    stock_close[stocks['Symbol']] = bars[-1].c
                else:
                    data.append(0)
                    stock_close[stocks['Symbol']] = 0
                continue
            if header_val == 'Gain':
                data.append(stock_close[stocks['Symbol']] - stock_open[stocks['Symbol']])
                continue
            if header_val == 'Gain %':
                if (stock_close[stocks['Symbol']] - stock_open[stocks['Symbol']]) == 0:
                    data.append(0)
                else:
                    data.append((stock_close[stocks['Symbol']] - stock_open[stocks['Symbol']])/stock_open[stocks['Symbol']])
                continue
            if header_val == 'Rating':
                data.append(stock_rating[stocks['Symbol']])
                continue
            if header_val in stocks:
                data.append(stocks[header_val])
            else:
                data.append("NA")
        print(data)
        writer.writerow(data)
