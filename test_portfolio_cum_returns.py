import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from arch.unitroot.cointegration import phillips_ouliaris, engle_granger
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

# To reformat if necessary
def extract_top_pairs(pairs_with_pvalues):
    return [pair for pair, _ in pairs_with_pvalues]


# Define your top pairs
top_pairs_engle = [
    ('8766.T', '9613.T'), ('1802.T', '9432.T'), ('5101.T', '9532.T'),
    ('7203.T', '9532.T'), ('5714.T', '7267.T'), ('8331.T', '8354.T'),
    ('5711.T', '8309.T'), ('6503.T', '6504.T'), ('4151.T', '9432.T'),
    ('6471.T', '7267.T')
]

# top_pairs_PO = [
#     ('5711.T', '8309.T'), ('8309.T', '8801.T'), ('5711.T', '8316.T'), 
#     ('6723.T', '9107.T'), ('8002.T', '8309.T'), ('7762.T', '8233.T'), 
#     ('5108.T', '6326.T'), ('8031.T', '8309.T'), ('5401.T', '6723.T'), 
#     ('3086.T', '8331.T')
# ]

top_pairs = top_pairs_engle

print(top_pairs)

# Initialize an empty Series to accumulate the daily returns for each pair
daily_returns = pd.Series(0, index=prices.index)

# Calculate the daily returns for each pair and update the portfolio value
for stock1, stock2 in top_pairs:
    print(f"Processing pair: {stock1}, {stock2}")
    # Normalize prices
    stock1_normalized = prices[stock1] / prices[stock1].iloc[0]
    stock2_normalized = prices[stock2] / prices[stock2].iloc[0]

    print("Stock1 Normalized:\n", stock1_normalized.head())
    print("Stock2 Normalized:\n", stock2_normalized.head())

    # Estimate spread and hedge ratio
    y = stock1_normalized
    x = stock2_normalized
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    hedge_ratio = model.params[1]

    # Calculate spread
    spread = y - hedge_ratio * stock2_normalized
    print("Spread:\n", spread.head())

    # Define trading signals using z-score
    spread_mean = spread.rolling(window=30).mean()
    spread_std = spread.rolling(window=30).std()
    z_score = (spread - spread_mean) / spread_std

    # Handle NaNs
    spread_mean.fillna(method='ffill', inplace=True)
    spread_std.fillna(method='ffill', inplace=True)
    z_score.fillna(method='ffill', inplace=True)

    print("Z-Score:\n", z_score.head())

    # Generate buy and sell signals
    entry_threshold = 2
    exit_threshold = 0
    signal = pd.Series(np.where(z_score > entry_threshold, -1, np.nan), index=z_score.index)  # Short signal
    signal = pd.Series(np.where(z_score < -entry_threshold, 1, signal), index=z_score.index)  # Long signal
    signal = pd.Series(np.where(abs(z_score) < exit_threshold, 0, signal), index=z_score.index)  # Exit signal; not in use when =0

    # Fill the NaN signals forward (i.e., unless there's a new signal, maintain position)
    signal = signal.ffill().fillna(0)

    print("Signals:\n", signal.head())

    # Translate signals to positions
    stock1_position = signal
    stock2_position = -signal * hedge_ratio

    # Ensure Series to be multiplied have the same index
    stock1_position_shifted = stock1_position.shift().fillna(0)
    stock1_pct_change = prices[stock1].pct_change().fillna(0)
    stock2_position_shifted = stock2_position.shift().fillna(0)
    stock2_pct_change = prices[stock2].pct_change().fillna(0)

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

# Calculate the cumulative returns for the portfolio
cum_return = (1 + daily_returns).cumprod()

# Print the final cumulative return
print(cum_return.iloc[-1])

# Plot the cumulative returns
print('Plotting results...')
plt.figure(figsize=(10, 6))
cum_return.plot(title='Cumulative Returns From Top Ten Cointegrated Pairs (Engle-Granger)')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.show()
print('Finished')
