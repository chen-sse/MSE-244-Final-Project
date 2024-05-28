import pandas as pd
import os

def transform_to_n225_format(crsp_file, output_file, sector):
    print(f"Processing file: {crsp_file}")

    crsp_daily = pd.read_csv(crsp_file, low_memory=False)
    crsp_daily_relevant = crsp_daily[['date', 'TICKER', 'COMNAM', 'PRC']]

    crsp_daily_agg = crsp_daily_relevant.groupby(['date', 'TICKER', 'COMNAM']).mean().reset_index()

    duplicates = crsp_daily_agg[crsp_daily_agg.duplicated(subset=['date', 'TICKER'], keep=False)]
    if not duplicates.empty:
        print(f"Duplicates removed: {crsp_file}")
        print(duplicates)
        crsp_daily_agg = crsp_daily_agg.drop_duplicates(subset=['date', 'TICKER'], keep=False)

    duplicates_after_removal = crsp_daily_agg[crsp_daily_agg.duplicated(subset=['date', 'TICKER'], keep=False)]
    if not duplicates_after_removal.empty:
        print(f"Duplicates still exist: {crsp_file}")
        print(duplicates_after_removal)
        return

    print("Entries to be pivoted:")
    print(crsp_daily_agg)

    try:
        crsp_pivot = crsp_daily_agg.pivot(index='date', columns='TICKER', values='PRC')
    except ValueError as e:
        print(f"Error during pivoting for file {crsp_file}: {e}")
        return
    
    crsp_pivot = crsp_pivot.sort_index(axis=1)

    tickers = crsp_pivot.columns.tolist()
    sectors = [sector] * len(tickers)
    companies = [
        crsp_daily_agg[crsp_daily_agg['TICKER'] == ticker]['COMNAM'].iloc[0]
        for ticker in tickers
    ]

    header_ticker = ['Ticker'] + tickers
    header_sector = ['Sector'] + sectors
    header_company = ['Company'] + companies

    combined_data = [header_ticker, header_sector, header_company] + crsp_pivot.reset_index().values.tolist()

    new_data_df = pd.DataFrame(combined_data)

    new_data_df.to_csv(output_file, index=False, header=False)
    print(f"Finished processing file: {crsp_file}")

import pandas as pd

def merge_csv_files(file_paths):
    """
    Merges multiple CSV files into one, excluding the first column of every file except the first,
    and removes duplicate tickers if any.

    Parameters:
    file_paths (list of str): List of paths to the CSV files to be merged.

    Returns:
    pd.DataFrame: Merged DataFrame with duplicate tickers removed.
    """
    merged_df = pd.read_csv(file_paths[0])

    for file_path in file_paths[1:]:
        df = pd.read_csv(file_path)
        df = df.drop(columns=df.columns[0])
        merged_df = pd.concat([merged_df, df], axis=1)

    merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

    return merged_df

file_paths = [
    'csv_data/crsp_daily_agricultural.csv',
    'csv_data/crsp_daily_educational-services.csv',
    'csv_data/crsp_daily_entertainment-recreation.csv',
    'csv_data/crsp_daily_etfs.csv',
    'csv_data/crsp_daily_finance-insurance.csv',
    'csv_data/crsp_daily_healthcare.csv',
    'csv_data/crsp_daily_hospitality.csv',
    'csv_data/crsp_daily_information-technology.csv',
    'csv_data/crsp_daily_management-companies.csv',
    'csv_data/crsp_daily_manufacturing.csv',
    'csv_data/crsp_daily_oil-gas-mining.csv',
    'csv_data/crsp_daily_other-services.csv',
    'csv_data/crsp_daily_professional-services.csv',
    'csv_data/crsp_daily_public-administration.csv',
    'csv_data/crsp_daily_real-estate.csv',
    'csv_data/crsp_daily_retail-trade.csv',
    'csv_data/crsp_daily_support-services.csv',
    'csv_data/crsp_daily_transportation-warehousing.csv',
    'csv_data/crsp_daily_utilities.csv',
    'csv_data/crsp_daily_wholesale-trade.csv'
]
sector_list = [
    'Agricultural', 
    'Educational Services',
    'Entertainment/Recreation',
    'ETFs',
    'Finance/Insurance',
    'Healthcare',
    'Hospitality',
    'Information Technology',
    'Management',
    'Manufacturing',
    'Oil/Gas',
    'Other Services',
    'Professional Services',
    'Public Administration',
    'Real Estate',
    'Retail Trade',
    'Support Services',
    'Transportation/Warehousing',
    'Utilities',
    'Wholesale Trade'
]
csv_paths = [
    'cleaned_data/all_data_0.csv',
    'cleaned_data/all_data_1.csv',
    'cleaned_data/all_data_2.csv',
    'cleaned_data/all_data_3.csv',
    'cleaned_data/all_data_4.csv',
    'cleaned_data/all_data_5.csv',
    'cleaned_data/all_data_6.csv',
    'cleaned_data/all_data_7.csv',
    'cleaned_data/all_data_8.csv',
    'cleaned_data/all_data_9.csv',
    'cleaned_data/all_data_10.csv',
    'cleaned_data/all_data_11.csv',
    'cleaned_data/all_data_12.csv',
    'cleaned_data/all_data_13.csv',
    'cleaned_data/all_data_14.csv',
    'cleaned_data/all_data_15.csv',
    'cleaned_data/all_data_16.csv',
    'cleaned_data/all_data_17.csv',
    'cleaned_data/all_data_18.csv',
    'cleaned_data/all_data_19.csv',
]

for i in range(len(file_paths)):
    output_file = f'all_data_{i}.csv'
    transform_to_n225_format(file_paths[i], output_file, sector_list[i])

merged_df = merge_csv_files(csv_paths)

output_path = "all_data.csv"
merged_df.to_csv(output_path, index=False)