##################################################################################
# coinmetrics.ps
#
# Loads crypto currency data from Coin Metrics https://coinmetrics.io/.  This data set can be retrieved using,
#
# curl -LO https://coinmetrics.io/newdata/all.zip
#
# The file all.zip contains one data file for each cryptocurrency.


import os
import pandas as pd
import pycurl
import subprocess
import urllib
from zipfile import ZipFile

# Specify the source file for the crypto data on the coin metrics site
coinmetrics_data_url = "https://coinmetrics.io/newdata/all.zip"
# Specify the local zip file name for the Crypto Data set
crypto_zipdatafile = "E:\\Users\\YGLM\\Development\\data\\all.zip"
# Location where data files are stored
data_dir = "E:\\Users\\YGLM\\Development\\data"

# pycurl NOT working with coinmetrics
def download_coinmetrics_pycurl():
  print(f"Downloading from {coinmetrics_data_url} to file {crypto_zipdatafile}")
  with open(crypto_zipdatafile, mode="wb") as fid:
    curl = pycurl.Curl()
    curl.setopt(curl.URL, coinmetrics_data_url)
    curl.setopt(curl.WRITEDATA, fid)
    curl.setopt(curl.VERBOSE, True)
    curl.perform()
    response_code = curl.getinfo(curl.RESPONSE_CODE)
    if not (200 <= response_code <= 299):
      print(f"There was a problem downloading {curl.getinfo(curl.EFFECTIVE_URL)} ({response_code})")
    curl.close()


def download_coinmetrics_curl():
  print(f"Downloading from {coinmetrics_data_url} to file {crypto_zipdatafile}")
  os.chdir(data_dir)
  print(subprocess.check_output("LoadCoinmetrics.cmd", shell=True).decode())
  print(subprocess.check_output("dir all.zip", shell=True).decode())
  print("Done downloading coinmetrics data.")

def load_crypto_datadict(cryptoccy_list):
  # opening the zip file in READ mode 
  with ZipFile(crypto_zipdatafile, 'r') as zip: 
    files = zip.namelist()
    all_cryptodata = {}
    for curFile in files:
      # Read each file and extract data
      ccyCode = curFile.split(".")[0]
      if (ccyCode in cryptoccy_list):
        cryptoDataFrame = pd.read_csv(zip.open(curFile))
        all_cryptodata[ccyCode] = cryptoDataFrame
  return(all_cryptodata)



