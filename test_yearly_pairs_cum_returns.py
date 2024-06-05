# -*- coding: utf-8 -*-
"""pairstrading.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TX4uNtBO8I6eeWCZBbX4ezY7HCKXOCxn
"""

!pip install arch statsmodels

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

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

# Precomputed top pairs
top_pairs_by_year = {
    2008: [('4751.T', '6861.T'), ('6861.T', '9532.T'), ('6861.T', '9107.T'), ('6861.T', '8233.T'), ('6645.T', '8304.T'), ('8304.T', '8316.T'), ('5020.T', '8001.T'), ('6861.T', '9101.T'), ('2502.T', '9532.T'), ('5301.T', '6861.T')],
    2009: [('5214.T', '7013.T'), ('2432.T', '5711.T'), ('2432.T', '9107.T'), ('7004.T', '8795.T'), ('2432.T', '8031.T'), ('3407.T', '5406.T'), ('2432.T', '6479.T'), ('2432.T', '2768.T'), ('2432.T', '6472.T'), ('1963.T', '7004.T')],
    2010: [('3861.T', '6501.T'), ('4324.T', '5802.T'), ('4704.T', '6367.T'), ('7751.T', '9735.T'), ('3861.T', '9104.T'), ('5201.T', '6326.T'), ('3382.T', '9104.T'), ('3861.T', '9107.T'), ('3382.T', '9107.T'), ('4507.T', '6702.T')],
    2011: [('4543.T', '7004.T'), ('2802.T', '4543.T'), ('7751.T', '9101.T'), ('4543.T', '6758.T'), ('1803.T', '4543.T'), ('6326.T', '9432.T'), ('8058.T', '9432.T'), ('4543.T', '8316.T'), ('4503.T', '9432.T'), ('6724.T', '9432.T')],
    2012: [('4755.T', '6479.T'), ('3407.T', '5706.T'), ('3407.T', '5803.T'), ('4021.T', '7751.T'), ('4755.T', '6952.T'), ('3402.T', '4751.T'), ('7261.T', '7751.T'), ('4755.T', '6674.T'), ('4755.T', '8002.T'), ('4755.T', '6762.T')],
    2013: [('6504.T', '9501.T'), ('5714.T', '9022.T'), ('4042.T', '5301.T'), ('1808.T', '7267.T'), ('7733.T', '9007.T'), ('6326.T', '8591.T'), ('7211.T', '9501.T'), ('2768.T', '4042.T'), ('2503.T', '5714.T'), ('3086.T', '5714.T')],
    2014: [('2914.T', '8304.T'), ('4755.T', '6273.T'), ('8304.T', '9532.T'), ('2914.T', '8604.T'), ('8801.T', '8830.T'), ('4452.T', '8304.T'), ('4704.T', '9843.T'), ('4704.T', '5233.T'), ('7912.T', '9107.T'), ('6954.T', '9107.T')],
    2015: [('4523.T', '6479.T'), ('5333.T', '6701.T'), ('2503.T', '4042.T'), ('6594.T', '7733.T'), ('1801.T', '4523.T'), ('1963.T', '4523.T'), ('6301.T', '7741.T'), ('6752.T', '9502.T'), ('4183.T', '6594.T'), ('4704.T', '6701.T')],
    2016: [('8304.T', '8316.T'), ('8304.T', '8306.T'), ('5108.T', '7012.T'), ('7912.T', '8766.T'), ('5108.T', '6302.T'), ('3086.T', '8304.T'), ('7912.T', '8304.T'), ('6305.T', '6501.T'), ('4324.T', '9432.T'), ('8304.T', '8309.T')],
    2017: [('7205.T', '7731.T'), ('7751.T', '8601.T'), ('7205.T', '8233.T'), ('6472.T', '7267.T'), ('5214.T', '6981.T'), ('7731.T', '7751.T'), ('8252.T', '9020.T'), ('1963.T', '6981.T'), ('6981.T', '7741.T'), ('4902.T', '6981.T')],
    2018: [('4061.T', '9502.T'), ('6724.T', '9502.T'), ('6674.T', '9502.T'), ('4183.T', '9502.T'), ('8053.T', '9502.T'), ('7272.T', '9502.T'), ('5233.T', '9502.T'), ('2413.T', '8252.T'), ('6113.T', '9983.T'), ('5706.T', '9502.T')],
    2019: [('5802.T', '6971.T'), ('6506.T', '6645.T'), ('2432.T', '8801.T'), ('1808.T', '7201.T'), ('2802.T', '7752.T'), ('5201.T', '9432.T'), ('1802.T', '2282.T'), ('2282.T', '6273.T'), ('2282.T', '5233.T'), ('4043.T', '9432.T')]
}

# Initialize an empty Series to accumulate the daily returns for each year
daily_returns = pd.Series(0, index=prices.index)

# Define trading strategy
def trading_strategy(year_data, pairs):
    # Initialize Series to accumulate daily returns
    year_daily_returns = pd.Series(0, index=year_data.index)

    for stock1, stock2 in pairs:
        try:
            # Normalize prices
            stock1_normalized = year_data[stock1] / year_data[stock1].iloc[0]
            stock2_normalized = year_data[stock2] / year_data[stock2].iloc[0]

            # Estimate spread and hedge ratio
            y = stock1_normalized
            x = stock2_normalized
            x = sm.add_constant(x)
            model = sm.OLS(y, x).fit()
            hedge_ratio = model.params[1]

            # Calculate spread
            spread = y - hedge_ratio * stock2_normalized

            # Define trading signals using z-score
            spread_mean = spread.rolling(window=30).mean()
            spread_std = spread.rolling(window=30).std()
            z_score = (spread - spread_mean) / spread_std

            # Handle NaNs
            spread_mean.fillna(method='ffill', inplace=True)
            spread_std.fillna(method='ffill', inplace=True)
            z_score.fillna(method='ffill', inplace=True)

            # Generate buy and sell signals
            entry_threshold = 2
            exit_threshold = 0
            signal = pd.Series(np.where(z_score > entry_threshold, -1, np.nan), index=z_score.index)  # Short signal
            signal = pd.Series(np.where(z_score < -entry_threshold, 1, signal), index=z_score.index)  # Long signal
            signal = pd.Series(np.where(abs(z_score) < exit_threshold, 0, signal), index=z_score.index)  # Exit signal; not in use when =0

            # Fill the NaN signals forward (i.e., unless there's a new signal, maintain position)
            signal = signal.ffill().fillna(0)

            # Translate signals to positions
            stock1_position = signal
            stock2_position = -signal * hedge_ratio

            # Ensure Series to be multiplied have the same index
            stock1_position_shifted = stock1_position.shift().fillna(0)
            stock1_pct_change = year_data[stock1].pct_change().fillna(0)
            stock2_position_shifted = stock2_position.shift().fillna(0)
            stock2_pct_change = year_data[stock2].pct_change().fillna(0)

            # Align indices
            common_index = stock1_position_shifted.index.intersection(stock1_pct_change.index).intersection(stock2_position_shifted.index).intersection(stock2_pct_change.index)
            stock1_position_shifted = stock1_position_shifted.loc[common_index]
            stock1_pct_change = stock1_pct_change.loc[common_index]
            stock2_position_shifted = stock2_position_shifted.loc[common_index]
            stock2_pct_change = stock2_pct_change.loc[common_index]

            # Calculate strategy returns
            stock1_return = stock1_position_shifted * stock1_pct_change
            stock2_return = stock2_position_shifted * stock2_pct_change
            pair_strategy_return = stock1_return + stock2_return

            # Add the daily returns for this pair to the daily_returns Series
            year_daily_returns = year_daily_returns.add(pair_strategy_return / len(pairs), fill_value=0)

        except Exception as e:
            print(f"Skipping pair ({stock1}, {stock2}) due to error: {e}")

    return year_daily_returns

# Process each year separately using the top pairs from the previous year
for year in range(2008, 2020):
    print(f"Processing year: {year}")
    if year in top_pairs_by_year:
        year_data = prices[prices.index.year == year]
        if year_data.empty:
            continue
        top_pairs = top_pairs_by_year[year]
        year_daily_returns = trading_strategy(year_data, top_pairs)
        daily_returns = daily_returns.add(year_daily_returns, fill_value=0)

# Calculate the cumulative returns for the portfolio
cum_return = (1 + daily_returns).cumprod()

# Print the final cumulative return
print(cum_return.iloc[-1])

# Plot the cumulative returns
print('Plotting results...')
plt.figure(figsize=(10, 6))
cum_return.plot(title='Cumulative Returns From Yearly Recalculated Top Cointegrated Pairs (Engle-Granger)')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.show()
print('Finished')

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

# Precomputed top pairs for each year
top_pairs_dict = {
    2008: [('4751.T', '6861.T'), ('6861.T', '9532.T'), ('6861.T', '9107.T'), ('6861.T', '8233.T'), ('6645.T', '8304.T'), ('8304.T', '8316.T'), ('5020.T', '8001.T'), ('6861.T', '9101.T'), ('2502.T', '9532.T'), ('5301.T', '6861.T')],
    2009: [('5214.T', '7013.T'), ('2432.T', '5711.T'), ('2432.T', '9107.T'), ('7004.T', '8795.T'), ('2432.T', '8031.T'), ('3407.T', '5406.T'), ('2432.T', '6479.T'), ('2432.T', '2768.T'), ('2432.T', '6472.T'), ('1963.T', '7004.T')],
    2010: [('3861.T', '6501.T'), ('4324.T', '5802.T'), ('4704.T', '6367.T'), ('7751.T', '9735.T'), ('3861.T', '9104.T'), ('5201.T', '6326.T'), ('3382.T', '9104.T'), ('3861.T', '9107.T'), ('3382.T', '9107.T'), ('4507.T', '6702.T')],
    2011: [('4543.T', '7004.T'), ('2802.T', '4543.T'), ('7751.T', '9101.T'), ('4543.T', '6758.T'), ('1803.T', '4543.T'), ('6326.T', '9432.T'), ('8058.T', '9432.T'), ('4543.T', '8316.T'), ('4503.T', '9432.T'), ('6724.T', '9432.T')],
    2012: [('4755.T', '6479.T'), ('3407.T', '5706.T'), ('3407.T', '5803.T'), ('4021.T', '7751.T'), ('4755.T', '6952.T'), ('3402.T', '4751.T'), ('7261.T', '7751.T'), ('4755.T', '6674.T'), ('4755.T', '8002.T'), ('4755.T', '6762.T')],
    2013: [('6504.T', '9501.T'), ('5714.T', '9022.T'), ('4042.T', '5301.T'), ('1808.T', '7267.T'), ('7733.T', '9007.T'), ('6326.T', '8591.T'), ('7211.T', '9501.T'), ('2768.T', '4042.T'), ('2503.T', '5714.T'), ('3086.T', '5714.T')],
    2014: [('2914.T', '8304.T'), ('4755.T', '6273.T'), ('8304.T', '9532.T'), ('2914.T', '8604.T'), ('8801.T', '8830.T'), ('4452.T', '8304.T'), ('4704.T', '9843.T'), ('4704.T', '5233.T'), ('7912.T', '9107.T'), ('6954.T', '9107.T')],
    2015: [('4523.T', '6479.T'), ('5333.T', '6701.T'), ('2503.T', '4042.T'), ('6594.T', '7733.T'), ('1801.T', '4523.T'), ('1963.T', '4523.T'), ('6301.T', '7741.T'), ('6752.T', '9502.T'), ('4183.T', '6594.T'), ('4704.T', '6701.T')],
    2016: [('8304.T', '8316.T'), ('8304.T', '8306.T'), ('5108.T', '7012.T'), ('7912.T', '8766.T'), ('5108.T', '6302.T'), ('3086.T', '8304.T'), ('7912.T', '8304.T'), ('6305.T', '6501.T'), ('4324.T', '9432.T'), ('8304.T', '8309.T')],
    2017: [('7205.T', '7731.T'), ('7751.T', '8601.T'), ('7205.T', '8233.T'), ('6472.T', '7267.T'), ('5214.T', '6981.T'), ('7731.T', '7751.T'), ('8252.T', '9020.T'), ('1963.T', '6981.T'), ('6981.T', '7741.T'), ('4902.T', '6981.T')],
    2018: [('4061.T', '9502.T'), ('6724.T', '9502.T'), ('6674.T', '9502.T'), ('4183.T', '9502.T'), ('8053.T', '9502.T'), ('7272.T', '9502.T'), ('5233.T', '9502.T'), ('2413.T', '8252.T'), ('6113.T', '9983.T'), ('5706.T', '9502.T')],
    2019: [('5802.T', '6971.T'), ('2432.T', '8801.T'), ('1802.T', '2282.T'), ('6506.T', '6645.T'), ('5713.T', '7261.T'), ('4042.T', '6954.T'), ('2282.T', '6273.T'), ('8802.T', '9020.T'), ('8053.T', '9432.T'), ('4902.T', '9613.T')]
}

# Initialize an empty Series to accumulate the daily returns for each pair
daily_returns = pd.Series(0, index=prices.index)

# Process each year separately using the precomputed top pairs
for year, top_pairs in top_pairs_dict.items():
    print(f"Processing year: {year}")
    year_data = prices[prices.index.year == year]
    if year_data.empty:
        print(f"No data for year {year}, skipping...")
        continue

    for (stock1, stock2) in top_pairs:
        print(f"Processing pair: {stock1}, {stock2}")
        try:
            # Normalize prices
            stock1_normalized = year_data[stock1] / year_data[stock1].iloc[0]
            stock2_normalized = year_data[stock2] / year_data[stock2].iloc[0]

            # Estimate spread and hedge ratio
            y = stock1_normalized
            x = stock2_normalized
            x = sm.add_constant(x)
            model = sm.OLS(y, x).fit()
            hedge_ratio = model.params[1]

            # Calculate spread
            spread = y - hedge_ratio * stock2_normalized

            # Define trading signals using z-score
            spread_mean = spread.rolling(window=30).mean()
            spread_std = spread.rolling(window=30).std()
            z_score = (spread - spread_mean) / spread_std

            # Handle NaNs
            spread_mean.fillna(method='ffill', inplace=True)
            spread_std.fillna(method='ffill', inplace=True)
            z_score.fillna(method='ffill', inplace=True)

            # Generate buy and sell signals
            entry_threshold = 2
            exit_threshold = 0
            signal = pd.Series(np.where(z_score > entry_threshold, -1, np.nan), index=z_score.index)  # Short signal
            signal = pd.Series(np.where(z_score < -entry_threshold, 1, signal), index=z_score.index)  # Long signal
            signal = pd.Series(np.where(abs(z_score) < exit_threshold, 0, signal), index=z_score.index)  # Exit signal; not in use when =0

            # Fill the NaN signals forward (i.e., unless there's a new signal, maintain position)
            signal = signal.ffill().fillna(0)

            # Translate signals to positions
            stock1_position = signal
            stock2_position = -signal * hedge_ratio

            # Ensure Series to be multiplied have the same index
            stock1_position_shifted = stock1_position.shift().fillna(0)
            stock1_pct_change = year_data[stock1].pct_change().fillna(0)
            stock2_position_shifted = stock2_position.shift().fillna(0)
            stock2_pct_change = year_data[stock2].pct_change().fillna(0)

            # Align indices
            common_index = stock1_position_shifted.index.intersection(stock1_pct_change.index).intersection(stock2_position_shifted.index).intersection(stock2_pct_change.index)
            stock1_position_shifted = stock1_position_shifted.loc[common_index]
            stock1_pct_change = stock1_pct_change.loc[common_index]
            stock2_position_shifted = stock2_position_shifted.loc[common_index]
            stock2_pct_change = stock2_pct_change.loc[common_index]

            # Calculate strategy returns
            stock1_return = stock1_position_shifted * stock1_pct_change
            stock2_return = stock2_position_shifted * stock2_pct_change
            pair_strategy_return = stock1_return + stock2_return

            # Add the daily returns for this pair to the daily_returns Series
            daily_returns = daily_returns.add(pair_strategy_return / len(top_pairs), fill_value=0)
        except Exception as e:
            print(f"Skipping pair ({stock1}, {stock2}) due to error: {e}")

# Calculate the cumulative returns for the portfolio
cum_return = (1 + daily_returns).cumprod()

# Print the final cumulative return
print(cum_return.iloc[-1])

# Plot the cumulative returns
print('Plotting results...')
plt.figure(figsize=(10, 6))
cum_return.plot(title='Cumulative Returns From Yearly Recalculated Top Cointegrated Pairs (Phillips-Ouliaris)')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.show()
print('Finished')
