
import requests
import json 
import pandas as pd 
import numpy as np 
import datetime as dt 
from binance.client import Client
import time
from datetime import timedelta, datetime
import math
from dateutil import parser
import os.path
import config



binsizes = {"1m": 1, "15m": 15, "1h": 60, "1d": 1440}
pd.DataFrame(binsizes,index=[0])
batch_size = 750



binance_client = Client(api_key=config.API_KEY_BINANCE, 
                        api_secret=config.API_SECRET_BINANCE)
 
## FUNCTIONS
def minutes_of_new_data(symbol, kline_size, data, source):
    if len(data) > 0:  old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance": old = datetime.strptime('1 Jan 2017', '%d %b %Y')
    # elif source == "bitmex": old = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=False).result()[0][0]['timestamp']
    if source == "binance": new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    # if source == "bitmex": new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
    return old, new

def get_all_binance(symbol, kline_size, save = False):

    filename = '%s-%s-data.csv' % (symbol, kline_size)
    if os.path.isfile(filename): data_df = pd.read_csv(filename)

    else: data_df = pd.DataFrame()
    oldest_point, newest_point = minutes_of_new_data(symbol, 
                                                     kline_size, 
                                                     data_df, 
                                                     source = "binance")

    delta_min = (newest_point - oldest_point).total_seconds()/60
    available_data = math.ceil(delta_min/binsizes[kline_size])

    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'): 
        print(f'Downloading all available {kline_size} data for {symbol}. Be patient..!')
    else: 
        print(f'Downloading {delta_min} minutes of new data available for {symbol}, i.e. {available_data} instances of {kline_size} data.')
    klines =( binance_client.get_historical_klines(symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), newest_point.strftime("%d %b %Y %H:%M:%S")))
    data = pd.DataFrame(klines, columns = ['timestamp', 
                                           'open', 'high', 'low', 
                                           'close', 'volume', 'close_time', 
                                           'quote_av', 'trades', 
                                           'tb_base_av', 
                                           'tb_quote_av', 'ignore' ])

    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    if len(data_df) > 0:
        temp_df = pd.DataFrame(data)
        data_df = data_df.append(temp_df)
    else: 
        data_df = data
    data_df.set_index('timestamp', inplace=True)
    if save: 
        data_df.to_csv(f'data/{filename}')
    print('All caught up..!')
    return data_df

tickers = requests.get('https://www.binance.com/api/v1/ticker/allPrices').text
tickers = pd.DataFrame(json.loads(tickers))['symbol'].values
tickers = tickers[[tk.find('USDT') not in [0,-1] for  tk in tickers]]

tickers=['ETHUSDT']
for symbol in tickers:
    get_all_binance(symbol, '15m', save = True)


