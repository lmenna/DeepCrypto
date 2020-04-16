##############################################################################################
# load_crypto_coinmetrics.py
#
# Loads crypto market data from Coin Metrics and formats it into files that can be used
# for deep learning market analysis.
#
# The Coin Metrics data contains daily data.  It has prices and trading volumes but 
# also includes blockchain transaction counts.  Many more coins are also included in
# the coin metrics data set. (79 coins as of 02/17/2020)
#
###############################################################################################

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

# Set path for imports.  Assumes current directory is the one where this file is in.  Usually "/user/dataloaders/"
sys.path.insert(0, os.path.join(os.getcwd(), "dataloaders" ) )
print("Path:", sys.path)

from dataloaders.coinmetrics import download_coinmetrics_curl
from dataloaders.coinmetrics import load_crypto_datadict

reload_data = False

if reload_data:
  download_coinmetrics_curl()

cryptoccy_list = ['btc', 'dash', 'dgb', 'eth', 'ltc', 'xem', 'xlm', 'xmr', 'xrp']
datacolumn_list = ['date', 'PriceUSD', 'TxCnt']
all_cryptodata = load_crypto_datadict(cryptoccy_list)
merged_data = pd.DataFrame()
for ticker in all_cryptodata:
  print(ticker)
  df_trimmed = all_cryptodata[ticker][datacolumn_list]
  df_trimmed.rename(columns = {'PriceUSD': 'PriceUSD_' + ticker, 'TxCnt': 'TxCnt_' + ticker}, inplace=True)
  df_trimmed['date'] = pd.to_datetime(df_trimmed['date'])
  df_trimmed['PriceUSD_' + ticker + "_s"] = df_trimmed['PriceUSD_' + ticker] / df_trimmed['PriceUSD_' + ticker].max()
  df_trimmed.set_index("date", inplace=True)
  # Create scaled dataframe
  df_trimmed['TxCnt_' + ticker + "_s"] = df_trimmed['TxCnt_' + ticker] / df_trimmed['TxCnt_' + ticker].max()
  # Keep only recent data
  df_trimmed = df_trimmed.loc[start_date:]
  if merged_data.empty:
    merged_data = df_trimmed
  else:
    merged_data = merged_data.join(df_trimmed, how='outer')      

merged_data_s = pd.DataFrame()
for ticker in all_cryptodata:
  print("Scaled: ", ticker)
  df_trimmed = all_cryptodata[ticker][datacolumn_list]
  df_trimmed.rename(columns = {'PriceUSD': 'PriceUSD_' + ticker, 'TxCnt': 'TxCnt_' + ticker}, inplace=True)
  df_trimmed['date'] = pd.to_datetime(df_trimmed['date'])
  df_trimmed.set_index("date", inplace=True)
  # Create scaled dataframe
  df_trimmed['PriceUSD_' + ticker] = df_trimmed['PriceUSD_' + ticker] / df_trimmed['PriceUSD_' + ticker].max()
  df_trimmed['TxCnt_' + ticker] = df_trimmed['TxCnt_' + ticker] / df_trimmed['TxCnt_' + ticker].max()
  # Create shifted transaction data
  if ticker in ['ltc','eth', 'btc']:
    for i in range(0, 40):
      df_trimmed[f'TxCnt_Shift_{i}_{ticker}'] = df_trimmed[f'TxCnt_{ticker}'].shift(i)
  # Simple moving average for transaction counts      
  days = 10
  df_trimmed[f'TxCnt_{ticker}_{days}_SMA'] = df_trimmed.loc[:,f'TxCnt_{ticker}'].rolling(window=days).mean()      
  # Keep only the most recent data
  df_trimmed = df_trimmed.loc[start_date:]
  if merged_data_s.empty:
    merged_data_s = df_trimmed
  else:
    merged_data_s = merged_data_s.join(df_trimmed, how='outer')  


# Correlation matrix plot
market_corr = merged_data_s.corr()

print("Correlations:")
market_corr.to_csv("cor.csv")
print(market_corr.head())
print(market_corr.tail())

data = market_corr.values
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
heatmap = ax.pcolor(data, cmap=plt.cm.RdYlGn)
fig.colorbar(heatmap)
ax.set_xticks(np.arange(data.shape[0]) + 0.5, minor=False)
ax.set_yticks(np.arange(data.shape[1]) + 0.5, minor=False)
ax.invert_yaxis()
ax.xaxis.tick_top()

column_labels = market_corr.columns
row_labels = market_corr.index

ax.set_xticklabels(column_labels)
ax.set_yticklabels(row_labels)
plt.xticks(rotation=90)
heatmap.set_clim(-1, 1)

plt.tight_layout()
plt.show()

TxCntLTC_Price = []
TxCntETH_Price = []
TxCntBTC_Price = []
price = 'PriceUSD_eth'
for i in range(0, 40):
  TxCntLTC_Price.append(market_corr[f'TxCnt_Shift_{i}_ltc'][price])
  TxCntETH_Price.append(market_corr[f'TxCnt_Shift_{i}_eth'][price])
  TxCntBTC_Price.append(market_corr[f'TxCnt_Shift_{i}_btc'][price])
plt.plot(TxCntLTC_Price)
plt.plot(TxCntETH_Price)
plt.plot(TxCntBTC_Price)
plt.legend(['TxCnt LTC', 'TXCnt ETH', 'TXCnt BTC'], loc='upper right')
plt.title(price)
plt.show()