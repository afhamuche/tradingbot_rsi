#!/usr/bin/env python3

import requests
import json
import time
import numpy as np

def extract(trades, a_key):
    extract = []
    for trade in trades:
        extract.append(trade[a_key])
    return extract

def get_trades(seconds):
    time_now = int(time.time())
    time_then = time_now - seconds
    trades = requests.get('https://www.mercadobitcoin.net/api/BTC/trades/{0}/{1}'.format(time_then, time_now))
    return trades.json()

def get_ticker_price():
    price = requests.get('https://www.mercadobitcoin.net/api/BTC/ticker/')
    price = json.loads(price.text)
    return float(price['ticker']['last'])

# Define the RSI function
def calc_rsi(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1. + rs)

    return rsi

quantity = 0.0001
walletbtc = 0
walletbrl = 1000
buy_list = []

while True:
    # Define the time stamps and Bitcoin prices
    trades = get_trades(600)
    timestamps = extract(trades, 'date')
    prices = extract(trades, 'price')
    current_price = get_ticker_price()

    # Calculate the RSI
    rsi = calc_rsi(prices, n=len(timestamps))

    # Determine the buy/hold/sell signal based on the RSI value
    last_rsi = int(rsi[-1])
    if last_rsi > 70 and walletbtc > 0:
        trade_type = "sell"
        walletbtc -= quantity
        walletbrl += quantity * current_price
        buy_list.remove(min(buy_list))
    elif last_rsi < 30 and walletbrl > quantity * current_price:
        trade_type = "buy"
        walletbtc += quantity
        walletbrl -= quantity * current_price
        buy_list.append(current_price)
    else:
        trade_type = "hold"

    data = [int(time.time()), trade_type, current_price, last_rsi, round(walletbtc, 4), walletbrl]
    print(data)

    time.sleep(30)
