import json
import csv
from datetime import date
import os.path
import alpaca_trade_api as tradeapi
from configparser import ConfigParser
import pandas as pd

#  Alpaca connection settings
config = ConfigParser()
config.read('config.ini')
api = tradeapi.REST(config.get('alpaca', 'KEY'), config.get('alpaca', 'SECRET'))

#  Add CSV headers
header = ['Date', 'Symbol', 'Name', 'Price', 'Previous_Price', 'PriceChgPct', 'TotalVolumeStr', 'MarketCapStr',
          'PriceVsVwap', 'Sector', 'Industry', 'PrItems', 'Today_Open', 'Today_Close']
file_exists = os.path.exists('premarket.csv')
if not file_exists:
    with open('premarket.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)

today = date.today()
today_date = today.strftime("%d/%m/%Y")

premarket_stocks = json.load(open('pre-market.json'))['PRE_MARKET_GAINERS']

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
                else:
                    data.append(0)
                continue
            if header_val == 'Today_Close':
                if bars:
                    data.append(bars[-1].c)
                else:
                    data.append(0)
                continue
            if header_val in stocks:
                data.append(stocks[header_val])
            else:
                data.append("NA")
        print(data)
        writer.writerow(data)
