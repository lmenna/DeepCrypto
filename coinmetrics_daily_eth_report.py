##############################################################################################
# coinmetrics_daily_eth_report.py
#
# Loads crypto market data from Coin Metrics and formats it into a daily report focused on
# Ethereum volume and crypto price anaysis.
#
# The Coin Metrics data contains daily data.  It has prices and trading volumes but 
# also includes blockchain transaction counts.  Many more coins are also included in
# the coin metrics data set. (79 coins as of 02/17/2020)
#
###############################################################################################

import datetime
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib import gridspec
import numpy as np
import ntpath
import os
import pandas as pd
from sklearn import preprocessing
import sys

style.use('seaborn-bright')

# Start data for crypto data load
start_date = "2016-06-01"
# Days in moving average
days = 14

# Set path for imports.  Assumes current directory is the one where this file is in.  Usually "/user/dataloaders/"
sys.path.insert(0, os.path.join(os.getcwd(), "dataloaders" ) )
print("Path:", sys.path)

from coinmetrics import download_coinmetrics_curl
from coinmetrics import load_crypto_datadict

reload_data = False

if reload_data:
  download_coinmetrics_curl()

cryptoccy_list = ['btc', 'dash', 'dgb', 'eth', 'ltc', 'xem', 'xlm', 'xmr', 'xrp']
datacolumn_list = ['date', 'PriceUSD', 'TxCnt']
all_cryptodata = load_crypto_datadict(cryptoccy_list)

merged_data_s = pd.DataFrame()
max_values = {}
date_max_value = {}
for ticker in all_cryptodata:
  print("Scaled: ", ticker)
  df_trimmed = all_cryptodata[ticker][datacolumn_list]
  df_trimmed.rename(columns = {'PriceUSD': 'PriceUSD_' + ticker, 'TxCnt': 'TxCnt_' + ticker}, inplace=True)
  df_trimmed['date'] = pd.to_datetime(df_trimmed['date'])
  df_trimmed.set_index("date", inplace=True)
  # Find the position for the maximum values
  max_values['PriceUSD_' + ticker] = df_trimmed['PriceUSD_' + ticker].max()
  max_values['TxCnt_' + ticker] = df_trimmed['TxCnt_' + ticker].max()
  idx_max = df_trimmed.idxmax(axis = 0)
  date_max_value['PriceUSD_' + ticker] = idx_max['PriceUSD_' + ticker]
  date_max_value['TxCnt_' + ticker] = idx_max['TxCnt_' + ticker]
  # Create scaled dataframe
  df_trimmed['PriceUSD_' + ticker] = df_trimmed['PriceUSD_' + ticker] / df_trimmed['PriceUSD_' + ticker].max()
  df_trimmed['TxCnt_' + ticker] = df_trimmed['TxCnt_' + ticker] / df_trimmed['TxCnt_' + ticker].max()
  # Simple moving average for transaction counts      
  df_trimmed[f'TxCnt_{ticker}_{days}_SMA'] = df_trimmed.loc[:,f'TxCnt_{ticker}'].rolling(window=days).mean()      
  # Keep only the most recent data
  df_trimmed = df_trimmed.loc[start_date:]
  if merged_data_s.empty:
    merged_data_s = df_trimmed
  else:
    merged_data_s = merged_data_s.join(df_trimmed, how='outer')  


def create_price_transaction_report(merged_data, days):
  fig = plt.figure()
  fig.suptitle(f"Scaled Prices and Transaction Counts ({days} Day Moving Avg)")
  spec = gridspec.GridSpec(ncols=1, nrows=2,
                         height_ratios=[3, 1])
  ax0 = fig.add_subplot(spec[0])
  ax1 = fig.add_subplot(spec[1])
  ax0.plot(merged_data["PriceUSD_btc"], linewidth=1)
  ax0.plot(merged_data["PriceUSD_eth"], linewidth=1)
  ax0.plot(merged_data["TxCnt_eth"], linewidth=1, ls='--')
  ax0.plot(merged_data["TxCnt_ltc"], linewidth=1, ls='--')
  ax0.plot(merged_data[f"TxCnt_eth_{days}_SMA"], linewidth=1, color='black')
  ax0.plot(merged_data[f"TxCnt_ltc_{days}_SMA"], linewidth=1, color='black')
  ax0.legend(["Price BTC", "Price ETH", "TXCnt ETH", "TXCnt LTC"], loc="upper left")
  # Add some text to the graph showing max values and current values
  max_str = "ETH Max: {:.1f}".format(max_values["PriceUSD_eth"])
  ax0.text(date_max_value['PriceUSD_eth'], 1, max_str)
  max_str = "ETH: {:.1f}".format(max_values["PriceUSD_eth"]*merged_data["PriceUSD_eth"][-1])
  ax0.text(merged_data.index[-1] + datetime.timedelta(days=1), merged_data["PriceUSD_eth"][-1], max_str)
  max_str = "BTC: {:.1f}".format(max_values["PriceUSD_btc"]*merged_data["PriceUSD_btc"][-1])
  ax0.text(merged_data.index[-1] + datetime.timedelta(days=1), merged_data["PriceUSD_btc"][-1], max_str)
  # Get last rows from dataframe
  last_rows = merged_data.tail(5)
  last_rows = last_rows.sort_index(ascending=False, axis=0)
  clust_data = []
  for index, row in last_rows.iterrows():
    clust_data.append([ index.strftime("%b %d, %Y"), 
      "{:.1f}".format(max_values["PriceUSD_eth"]*row["PriceUSD_eth"]), 
      "{:.0f}".format(max_values["TxCnt_eth"]*row["TxCnt_eth"]), 
      "{:.0f}".format(max_values["TxCnt_eth"]*row[f"TxCnt_eth_{days}_SMA"]), 
      "{:.0f}".format(max_values["TxCnt_ltc"]*row["TxCnt_ltc"]), 
      "{:.0f}".format(max_values["TxCnt_ltc"]*row[f"TxCnt_ltc_{days}_SMA"]) ])
  collabel=("Date", "Price ETH", "TxCnt ETH", "TxCnt ETH Avg", "TxCnt LTC", "TxCnt LTC Avg")
  ax1.axis('tight')
  ax1.axis('off')
  ax1.table(cellText=clust_data, colLabels=collabel, loc='center')
  plt.show()

create_price_transaction_report(merged_data_s, days)
