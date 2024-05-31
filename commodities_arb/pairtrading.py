# import pandas as pd
# import numpy as np

# # Load your data
# print('Loading data...')
# corn_data = pd.read_csv('commodities/corn.csv')
# wheat_data = pd.read_csv('commodities/wheatcomposite.csv')
# print('Data loaded')

# # Inspect the first few rows of the data
# print(corn_data.head())
# print(wheat_data.head())


# # Convert Date_ to datetime format
# corn_data['Date_'] = pd.to_datetime(corn_data['Date_'])
# wheat_data['Date_'] = pd.to_datetime(wheat_data['Date_'])

# # Filter relevant columns
# corn_data = corn_data[['FutCode', 'Date_', 'Settlement']]
# wheat_data = wheat_data[['FutCode', 'Date_', 'Settlement']]

# # Sort by FutCode and Date_
# corn_data = corn_data.sort_values(by=['FutCode', 'Date_'])
# wheat_data = wheat_data.sort_values(by=['FutCode', 'Date_'])

# # Inspect the processed data
# print(corn_data.head())
# print(wheat_data.head())


# # Group by FutCode and ensure continuity
# corn_grouped = corn_data.groupby('FutCode')
# wheat_grouped = wheat_data.groupby('FutCode')

# # Function to process each group
# def process_group(group):
#     group = group.set_index('Date_')
#     group = group.resample('D').ffill()  # Forward fill missing dates
#     return group

# # Apply the function to each group
# corn_processed = corn_grouped.apply(process_group).reset_index(level=0, drop=True)
# wheat_processed = wheat_grouped.apply(process_group).reset_index(level=0, drop=True)

# # Inspect the processed data
# print(corn_processed.head())
# print(wheat_processed.head())


# # Merge the processed data on the date
# print('Merging data...')
# data = pd.merge(corn_processed, wheat_processed, on='Date_', suffixes=('_corn', '_wheat'))
# print('Data merged')

# # Inspect the merged data
# print(data.head())


# # Calculate the spread
# print('Calculating spread...')
# data['Spread'] = data['Settlement_corn'] / data['Settlement_wheat']

# # Handle missing values
# print('Handling missing values...')
# data['Spread'].replace([np.inf, -np.inf], np.nan, inplace=True)
# data['Spread'].fillna(method='ffill', inplace=True)

# # Inspect the data with spread
# print(data.head())
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import random

# Load your data with dtype specification to avoid mixed type warnings
print('Loading data...')
dtype_spec = {
    'FutCode': str,
    'Date_': str,
    'Settlement': float,
    # Specify other columns if needed
}
corn_data = pd.read_csv('commodities/corn.csv', dtype=dtype_spec, low_memory=False)
wheat_data = pd.read_csv('commodities/wheatcomposite.csv', dtype=dtype_spec, low_memory=False)
print('Data loaded')

# Convert Date_ to datetime format
corn_data['Date_'] = pd.to_datetime(corn_data['Date_'])
wheat_data['Date_'] = pd.to_datetime(wheat_data['Date_'])

# Filter relevant columns
corn_data = corn_data[['FutCode', 'Date_', 'Settlement']]
wheat_data = wheat_data[['FutCode', 'Date_', 'Settlement']]

# Sort by FutCode and Date_
corn_data = corn_data.sort_values(by=['FutCode', 'Date_'])
wheat_data = wheat_data.sort_values(by=['FutCode', 'Date_'])

# Function to find contracts with matching dates
def find_matching_contracts(corn_data, wheat_data):
    corn_contracts = corn_data['FutCode'].unique()
    wheat_contracts = wheat_data['FutCode'].unique()
    
    for corn_contract in corn_contracts:
        corn_dates = corn_data[corn_data['FutCode'] == corn_contract]['Date_']
        for wheat_contract in wheat_contracts:
            wheat_dates = wheat_data[wheat_data['FutCode'] == wheat_contract]['Date_']
            common_dates = corn_dates[corn_dates.isin(wheat_dates)]
            if len(common_dates) > 0:
                return corn_contract, wheat_contract, common_dates
    return None, None, None

# Find a pair with matching dates
corn_contract, wheat_contract, common_dates = find_matching_contracts(corn_data, wheat_data)

if corn_contract is None or wheat_contract is None:
    print('No matching contracts found.')
else:
    print(f'Selected Corn Contract: {corn_contract}')
    print(f'Selected Wheat Contract: {wheat_contract}')

    # Filter the selected contracts
    corn_selected = corn_data[(corn_data['FutCode'] == corn_contract) & (corn_data['Date_'].isin(common_dates))]
    wheat_selected = wheat_data[(wheat_data['FutCode'] == wheat_contract) & (wheat_data['Date_'].isin(common_dates))]

    # Ensure continuity by resampling and forward-filling missing dates
    corn_selected = corn_selected.set_index('Date_').resample('D').ffill().reset_index()
    wheat_selected = wheat_selected.set_index('Date_').resample('D').ffill().reset_index()

    # Normalize prices
    corn_selected['Normalized'] = corn_selected['Settlement'] / corn_selected['Settlement'].iloc[0]
    wheat_selected['Normalized'] = wheat_selected['Settlement'] / wheat_selected['Settlement'].iloc[0]

    # Estimate spread and hedge ratio
    y = corn_selected['Normalized']
    x = wheat_selected['Normalized']
    x = sm.add_constant(x)
    model = sm.OLS(y, x).fit()
    hedge_ratio = model.params[1]

    # Calculate the spread
    corn_selected['Spread'] = y - hedge_ratio * wheat_selected['Normalized']

    # Define trading signals using z-score
    corn_selected['Spread_mean'] = corn_selected['Spread'].rolling(window=30).mean()
    corn_selected['Spread_std'] = corn_selected['Spread'].rolling(window=30).std()
    corn_selected['Z-score'] = (corn_selected['Spread'] - corn_selected['Spread_mean']) / corn_selected['Spread_std']

    # Handle NaNs in rolling calculations
    corn_selected['Spread_mean'].fillna(method='ffill', inplace=True)
    corn_selected['Spread_std'].fillna(method='ffill', inplace=True)
    corn_selected['Z-score'].fillna(method='ffill', inplace=True)

    # Generate buy and sell signals
    entry_threshold = 2
    exit_threshold = 0
    corn_selected['Signal'] = np.where(corn_selected['Z-score'] > entry_threshold, -1, np.nan)  # Short signal
    corn_selected['Signal'] = np.where(corn_selected['Z-score'] < -entry_threshold, 1, corn_selected['Signal'])  # Long signal
    corn_selected['Signal'] = np.where(abs(corn_selected['Z-score']) < exit_threshold, 0, corn_selected['Signal'])  # Exit signal

    # Fill the NaN signals forward
    corn_selected['Signal'] = corn_selected['Signal'].ffill().fillna(0)

    # Translate signals to positions
    corn_selected['Position_corn'] = corn_selected['Signal']
    corn_selected['Position_wheat'] = -corn_selected['Signal'] * hedge_ratio

    # Calculate strategy returns
    corn_selected['Return_corn'] = corn_selected['Position_corn'].shift() * corn_selected['Settlement'].pct_change()
    wheat_selected['Return_wheat'] = corn_selected['Position_wheat'].shift() * wheat_selected['Settlement'].pct_change()
    corn_selected['Strategy_returns'] = corn_selected['Return_corn'] + wheat_selected['Return_wheat']
    corn_selected['Cumulative_returns'] = (1 + corn_selected['Strategy_returns']).cumprod()

    # Print statistics
    print('Statistics:')
    print(corn_selected.describe())

    # Plot the cumulative returns
    print('Plotting results...')
    plt.figure(figsize=(10, 6))
    corn_selected['Cumulative_returns'].plot(title='Cumulative Returns from Pairs Trading Strategy')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.show()
    print('Finished')
