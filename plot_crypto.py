
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import os
import pandas as pd

style.use('ggplot')

# Load market data from previously saved file.
#
# This data is typically in the file "./market_data/combined_data.csv"
#
data_dir = os.path.join(os.getcwd(), "market_data" )
merged_data_filename = '{}/{}.csv'.format(data_dir, "combined_data")
print("Using local files for market data.", data_dir)
print("Reading file", merged_data_filename)
market_data = pd.read_csv(merged_data_filename)

# The loaded market_data will have the format...
#
# Date        volume_COIN1 adj_close_COIN1 ...
# 2015-08-06  #######      ###.##
# ...

# Set the date index
market_data.set_index("Date", inplace=True)
print("market_data\n", market_data.head())

market_data["adj_close_BTC"].plot()
plt.show()

market_corr = market_data.corr()
print(market_corr.head())

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

