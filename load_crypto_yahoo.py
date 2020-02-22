
##############################################################################################
# load_crypto_yahoo.py
#
# Loads crypto market data from Yahoo finance and formats it into file that can be used
# for deep learning market analysis.
#
# The Yahoo finance market data contains daily prices and trading volumes for major coins.
#
###############################################################################################


import glob
import os
import ntpath
import pandas as pd
import sys

# Set path for imports.  Assumes current directory is the one where this file is in.  Usually "/user/dataloaders/"
sys.path.insert(0, os.path.join(os.getcwd(), "dataloaders" ) )
print("Path:", sys.path)

from yahoo_finance import get_data_from_yahoo

ticker_list = ["BTC-USD", "ETH-USD", "LTC-USD", "XRP-USD", "XLM-USD", "XEM-USD", "XMR-USD", "DASH-USD"]

def save_mkt_to_files(market_data_dir):
  market_data = get_data_from_yahoo(ticker_list, True)  
  for key, df in market_data.items():
    df.to_csv('{}/{}.csv'.format(market_data_dir, key))
  return market_data

# merge_market_data(market_data)
#
# The market data contains time series for multiple tickers.
# Each timeseries is in a seperate dataframe.
# This function merges all of the timeseries in market_data into
# a single dataframe index by time.
#
# It also only includes the columns Volume and Adj Close.
#
# The final file will have the format,
#
# Date, tk1_volume, tk1_adj_close, tk2_volume, tk2_adj_close, ...
#
def merge_market_data(market_data):

  merged_data = pd.DataFrame()
  for key, df in market_data.items():
    # The Yahoo data has a duplicated COB date in the data for 2016-03-27.
    # Remove the duplicate COB and any others that might be present.
    df = df[~df.index.duplicated(keep='first')]
    ticker = key.split('-')[0]  
    df.rename(columns = {'Volume': 'volume_' + ticker, 'Adj Close': 'adj_close_' + ticker}, inplace=True)
    df = df.drop(['High','Low','Open','Close'], axis=1) 
    if merged_data.empty:
      merged_data = df
    else:
      merged_data = merged_data.join(df, how='outer')      
  return merged_data    

def read_mkt_from_files(market_data_dir):
  all_data = {}
  files = glob.glob(market_data_dir + "\\*.csv")
  for name in files:
    print("Reading", name)
    data = pd.read_csv(name)
    ticker = ntpath.basename(name).split('.')[0]
    all_data[ticker] = data
  print("Done reading files.")    
  return all_data

def remove_all_files(data_dir):
  files = glob.glob(data_dir + "\\*")
  for name in files:
    os.remove(name)

# reload_market=True will cause the program to load market data from the provide.
# reload_market=False will read market data from locally stored files
print("\nBEGIN: load_crypto.py")

reload_market = True

# Determine where market data is stored.  
# "posix" means we are running in colab
# Anything else means we are running on windows
print("Running on:", os.name)
if os.name=="posix":
  data_dir = "/content/deep_market/market_data"
else:  
  data_dir = os.path.join(os.getcwd(), "market_data" )
merged_data_filename = '{}/{}.csv'.format(data_dir, "combined_data")
if reload_market:
  print("Reloading market data from provider.")
  print("Will store market data in directory", data_dir)
  remove_all_files(data_dir)
  market_data = save_mkt_to_files(data_dir)
else:  
  print("Using local files for market data.", data_dir)
  if os.path.isfile(merged_data_filename):
    os.remove(merged_data_filename)
  market_data = read_mkt_from_files(data_dir)
merged_markets = merge_market_data(market_data)
merged_markets.to_csv(merged_data_filename)
print("merged_markets:\n", merged_markets)

print("DONE: load_crypto.py\n")
