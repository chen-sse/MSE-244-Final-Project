import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set the directory containing your CSV files
data_dir = "commodities"

# List of commodity CSV files
commodity_files = [
    "BrentCrudeOilLastDay.csv",
    "CoffeeC.csv",
    "corn.csv",
    "cotton2.csv",
    "crudeoil.csv",
    "feedercattle.csv",
    "GasolineRBOB.csv",
    "HeatingOil.csv",
    "HenryHubNaturalGas FinancialLastDayComposite.csv",
    "LeanHogsComposite.csv",
    "livecattlecomposite.csv",
    "lumber.csv",
    "NaturalGas.csv",
    "Sugar11.csv",
    "wheatcomposite.csv",
    "soybeancomposite.csv"
]
# Function to load and clean data
def load_and_clean_data(file):
    df = pd.read_csv(os.path.join(data_dir, file))
    df['Date_'] = pd.to_datetime(df['Date_'])
    df = df.sort_values(by='Date_')
    
    # Remove rows with NaNs, zeros, and infinities in the 'Settlement' column
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['Settlement'])
    df = df[df['Settlement'] != 0]
    
    return df

# Load data into a dictionary of DataFrames
data = {file.split('.')[0]: load_and_clean_data(file) for file in commodity_files}

# Plot time series for each commodity
plt.figure(figsize=(14, 8))
for name, df in data.items():
    plt.plot(df['Date_'], df['Settlement'], label=name)
plt.xlabel('Date')
plt.ylabel('Settlement Price')
plt.title('Commodity Futures Prices')
plt.legend()
plt.show()

# Calculate and display summary statistics
for name, df in data.items():
    print(f"Summary statistics for {name}:")
    print(df['Settlement'].describe())
    print("\n")

# Pair plot for selected commodities (e.g., first 5 commodities)
selected_commodities = list(data.keys())[:5]
merged_data = pd.DataFrame()
for name in selected_commodities:
    merged_data[name] = data[name].set_index('Date_')['Settlement']

sns.pairplot(merged_data)
plt.show()

# Correlation matrix heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(merged_data.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix of Selected Commodities')
plt.show()

# Seasonality analysis (monthly mean prices)
for name, df in data.items():
    df['Month'] = df['Date_'].dt.month
    monthly_mean = df.groupby('Month')['Settlement'].mean()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=monthly_mean.index, y=monthly_mean.values)
    plt.title(f'Seasonality Analysis for {name}')
    plt.xlabel('Month')
    plt.ylabel('Average Settlement Price')
    plt.show()