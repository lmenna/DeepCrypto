
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web
import time

# Market data comes from Yahoo finance.
# This will load the daily data elements (Date, High, Low, Open, Close, Volume, Adj Close)
def get_data_from_yahoo(tickers, verbose=False):

  start = dt.datetime(2015, 8, 7)
  end = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%Y-%m-%d')

  print("Loading data from YAHOO finance from", start, "to", end)
  all_data = {}
  for idx, ticker in enumerate(tickers):
    try:
      if verbose:
        print(idx, "   --> Loading ticker:", ticker)
      df = web.DataReader(ticker, 'yahoo', start, end)
      all_data[ticker] = df
      # df.to_csv('{}/{}.csv'.format(market_data_dir, ticker))
      # Throttle the loading
      time.sleep(0.025)
    except:
      if verbose:
        print("Got an error.")
        print("Unexpected error:", sys.exc_info()[0])  

  print("Done - Loading from YAHOO finance.")
  return all_data



