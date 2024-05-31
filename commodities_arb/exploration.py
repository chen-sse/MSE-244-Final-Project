import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set the directory containing your CSV files
data_dir = "commodities"

# List of commodity CSV files
commodity_files = [
    #"BrentCrudeOilLastDay.csv",
    #"CoffeeC.csv",
    "corn.csv",
    #"cotton2.csv",
    #"crudeoil.csv",
    #"feedercattle.csv",
    #"GasolineRBOB.csv",
    #"HeatingOil.csv",
    #"HenryHubNaturalGas FinancialLastDayComposite.csv",
    #"LeanHogsComposite.csv",
    #"livecattlecomposite.csv",
    #"lumber.csv",
    #"NaturalGas.csv",
    #"Sugar11.csv",
    "wheatcomposite.csv",
    #"soybeancomposite.csv"
]
# Function to load, clean, and normalize data
def load_and_clean_data(file):
    df = pd.read_csv(os.path.join(data_dir, file))
    df['Date_'] = pd.to_datetime(df['Date_'])
    df = df.sort_values(by='Date_')
    
    # Remove rows with NaNs, zeros, and infinities in the 'Settlement' column
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['Settlement'])
    df = df[df['Settlement'] != 0]
    
    # Normalize the 'Settlement' prices
    df['Normalized_Settlement'] = (df['Settlement'] - df['Settlement'].mean()) / df['Settlement'].std()
    
    return df

# Load data into a dictionary of DataFrames
data = {file.split('.')[0]: load_and_clean_data(file) for file in commodity_files}

# Function to filter data between 2000 and 2010
def filter_data(df):
    return df[(df['Date_'] >= '2000-01-01') & (df['Date_'] <= '2010-12-31')]

# Plot normalized time series for each commodity
plt.figure(figsize=(14, 8))
for name, df in data.items():
    df_filtered = filter_data(df)
    plt.plot(df_filtered['Date_'], df_filtered['Normalized_Settlement'], label=name)
plt.xlabel('Date')
plt.ylabel('Normalized Settlement Price')
plt.title('Normalized Commodity Futures Prices (2000-2010)')
plt.legend()
plt.show()

# Calculate and display summary statistics for normalized prices between 2000 and 2010
for name, df in data.items():
    df_filtered = filter_data(df)
    print(f"Summary statistics for {name} (2000-2010, Normalized):")
    print(df_filtered['Normalized_Settlement'].describe())
    print("\n")

# Pair plot for selected commodities using normalized prices (2000-2010)
selected_commodities = list(data.keys())[:5]
merged_data = pd.DataFrame()
for name in selected_commodities:
    merged_data[name] = filter_data(data[name]).set_index('Date_')['Normalized_Settlement']

sns.pairplot(merged_data)
plt.show()

# Correlation matrix heatmap using normalized prices (2000-2010)
plt.figure(figsize=(10, 8))
sns.heatmap(merged_data.corr(), annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix of Selected Commodities (2000-2010, Normalized)')
plt.show()

# Seasonality analysis using normalized prices (monthly mean prices, 2000-2010)
for name, df in data.items():
    df_filtered = filter_data(df)
    df_filtered['Month'] = df_filtered['Date_'].dt.month
    monthly_mean = df_filtered.groupby('Month')['Normalized_Settlement'].mean()
    plt.figure(figsize=(10, 6))
    sns.barplot(x=monthly_mean.index, y=monthly_mean.values)
    plt.title(f'Seasonality Analysis for {name} (2000-2010, Normalized)')
    plt.xlabel('Month')
    plt.ylabel('Average Normalized Settlement Price')
    plt.show()