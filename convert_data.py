import pandas as pd

file_paths = [
    'us/crsp_daily_agricultural.csv.gz',
    'us/crsp_daily_educational-services.csv.gz',
    'us/crsp_daily_entertainment-recreation.csv.gz',
    'us/crsp_daily_etfs.csv.gz',
    'us/crsp_daily_finance-insurance.csv.gz',
    'us/crsp_daily_healthcare.csv.gz',
    'us/crsp_daily_hospitality.csv.gz',
    'us/crsp_daily_information-technology.csv.gz',
    'us/crsp_daily_management-companies.csv.gz',
    'us/crsp_daily_manufacturing.csv.gz',
    'us/crsp_daily_oil-gas-mining.csv.gz',
    'us/crsp_daily_other-services.csv.gz',
    'us/crsp_daily_professional-services.csv.gz',
    'us/crsp_daily_public-administration.csv.gz',
    'us/crsp_daily_real-estate.csv.gz',
    'us/crsp_daily_retail-trade.csv.gz',
    'us/crsp_daily_support-services.csv.gz',
    'us/crsp_daily_transportation-warehousing.csv.gz',
    'us/crsp_daily_utilities.csv.gz',
    'us/crsp_daily_wholesale-trade.csv.gz'
]

def convert_gz_to_csv(gz_file_path):
    csv_file_path = gz_file_path.replace('.csv.gz', '.csv')
    df = pd.read_csv(gz_file_path)
    df.to_csv(csv_file_path, index=False)
    return csv_file_path

for path in file_paths:
    new_csv_path = convert_gz_to_csv(path)
    print(f'Converted: {new_csv_path}')