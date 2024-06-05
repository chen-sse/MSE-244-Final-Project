import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from arch.unitroot.cointegration import engle_granger
from itertools import combinations
import warnings
warnings.filterwarnings("ignore")

# Load CSV
prices = pd.read_csv('N225.csv')

# Drop tickers with NA values
prices = prices.dropna(axis=1, how='any')

# Extract the industrial classification, sector, and company names
metadata = pd.DataFrame(prices.iloc[:3])
metadata = metadata.T
metadata.columns = metadata.iloc[0]
metadata = metadata.iloc[1:]
metadata.rename(columns={'Nikkei Industrial Classification':'Industry'}, inplace=True)

# Drop the metadata rows and process date
prices = prices.iloc[3:]
prices.rename(columns={'Ticker':'Date'}, inplace=True)
prices['Date'] = pd.to_datetime(prices['Date'])
prices.set_index('Date', inplace=True, drop=True)
prices = prices.astype(float)

print(prices.head())

######### 

# Exclude '9201.T' from tickers - was off the market for a few years, flat prices ruin everything
tickers = prices.columns.difference(['9201.T'])
pairs = list(combinations(tickers, 2)) #list()

print("Pairs:", pairs)

# Initialize an empty Series to accumulate the daily returns for each pair
daily_returns = pd.Series(0, index=prices.index)

# Function to get top cointegrated pairs for a given year
def get_top_pairs(year_data, num_pairs=10):
    results = {}
    for stock1, stock2 in pairs:
        try:
            p_value = min(engle_granger(np.log(year_data[stock1]), np.log(year_data[stock2])).pvalue, 
                          engle_granger(np.log(year_data[stock2]), np.log(year_data[stock1])).pvalue)
            results[(stock1, stock2)] = p_value
        except Exception as e: # 9201.T was breaking
            print(f"Skipping pair ({stock1}, {stock2}) due to error: {e}")
            print(f"{stock1} series:\n{year_data[stock1]}")
            print(f"{stock2} series:\n{year_data[stock2]}")
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    return sorted_results[:num_pairs]

# Initialize dictionary to hold top pairs for each year
yearly_top_pairs = {}

# Calculate top pairs for each year based on the previous year's data
for year in range(prices.index.year.min() + 1, prices.index.year.max() + 1):
    previous_year_data = prices[prices.index.year == (year - 1)]
    print(f"Calculating top pairs for {year} based on {year - 1}")
    top_pairs = get_top_pairs(previous_year_data)
    yearly_top_pairs[year] = top_pairs
    print(f"Top pairs for {year}: {top_pairs}")