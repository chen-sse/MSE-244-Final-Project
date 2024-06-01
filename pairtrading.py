import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import arch.unitroot
from statsmodels.tsa.stattools import coint
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
metadata.rename(columns={'Nikkei Industrial Classification':'Industry'},
                inplace=True)

# Drop the metadata rows and process date
prices = prices.iloc[3:]
prices.rename(columns={'Ticker':'Date'}, inplace=True)
prices['Date'] = pd.to_datetime(prices['Date'])
prices.set_index('Date', inplace=True, drop=True)
prices = prices.astype(float)

# Extract price series for Honda and Toyota
honda = prices['7267.T']
toyota = prices['7203.T']

# Generate all unique pairs of tickers
tickers = prices.columns
num_pairs = sum(1 for _ in combinations(tickers, 2))
pairs = combinations(tickers, 2)
results = {}

# Iterate over each pair and perform Engle-Granger cointegration test on log prices
# We take the more significant of the two p-values
count = 0
low_p_values = 0
for stock1, stock2 in pairs:
    count += 1
    p_value = min(coint(np.log(prices[stock1]), np.log(prices[stock2]))[1], coint(np.log(prices[stock2]), np.log(prices[stock1]))[1])
    results[(stock1, stock2)] = p_value
    if p_value < 0.05:
        low_p_values += 1
    print(f"{count} of {num_pairs} completed; # of p-values < 0.05: {low_p_values}")

# Sort results by p-value
sorted_results = sorted(results.items(), key=lambda x: x[1])

# Display the top 10 pairs with the lowest p-values
print(sorted_results[:10])

########## calculate returns of trading strategy ##########
'''
# Normalize prices
honda_normalized = honda / honda.iloc[0]
toyota_normalized = toyota / toyota.iloc[0]

# Estimate spread and hedge ratio
y = honda_normalized
x = toyota_normalized
x = sm.add_constant(x)
model = sm.OLS(y, x).fit()
hedge_ratio = model.params[1]

# Calculate spread
spread = y - hedge_ratio * toyota_normalized

# define trading signals using z-score
spread_mean = spread.rolling(window=30).mean()
spread_std = spread.rolling(window=30).std()
z_score = (spread - spread_mean) / spread_std

# handle NaNs
spread_mean.fillna(method='ffill', inplace=True)
spread_std.fillna(method='ffill', inplace=True)
z_score.fillna(method='ffill', inplace=True)

# Generate buy and sell signals
entry_threshold = 2
exit_threshold = 0
signal = pd.Series(np.where(z_score > entry_threshold, -1, np.nan))  # Short signal
signal = pd.Series(np.where(z_score < -entry_threshold, 1, signal))  # Long signal
signal = pd.Series(np.where(abs(z_score) < exit_threshold, 0, signal))  # Exit signal; not in use when =0

# Fill the NaN signals forward (i.e. unless there's a new signal, maintain position)
signal = signal.ffill().fillna(0)

# Translate signals to positions
honda_position = signal
toyota_position = -signal * hedge_ratio

# Ensure Series to be multiplied have same index
honda_position_shifted = honda_position.shift().fillna(0)
honda_pct_change = honda.pct_change().fillna(0)
toyota_position_shifted = toyota_position.shift().fillna(0)
toyota_pct_change = toyota.pct_change().fillna(0)

common_index = range(3202)
honda_position_shifted.index = common_index
honda_pct_change.index = common_index
toyota_position_shifted.index = common_index
toyota_pct_change.index = common_index

# Calculate strategy returns
honda_return = honda_position_shifted * honda_pct_change
toyota_return = toyota_position_shifted * toyota_pct_change
strategy_return = honda_return + toyota_return
cum_return = (1 + strategy_return).cumprod()

# Plot the cumulative returns
print('Plotting results...')
plt.figure(figsize=(10, 6))
cum_return.plot(title='Cumulative Returns from Pairs Trading Strategy')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.show()
print('Finished')
'''