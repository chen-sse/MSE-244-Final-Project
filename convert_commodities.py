import pandas as pd

file_paths = [
    'commodities/NYMEX-B0.csv.gz',
    'commodities/NYMEX-BZ.csv.gz',
    'commodities/NYMEX-CL.csv.gz',
    'commodities/NYMEX-HH.csv.gz',
    'commodities/NYMEX-HO.csv.gz',
    'commodities/NYMEX-NG.csv.gz',
    'commodities/NYMEX-NG.csv.gz',
    'commodities/NYMEX-RB.csv.gz',
    'commodities/CBOT-ZC.csv.gz',
    'commodities/CBOT-ZL.csv.gz',
    'commodities/CBOT-ZW.csv.gz',
    'commodities/CBOT-ZM.csv.gz',
    'commodities/CBOT-ZS.csv.gz',
    'commodities/CME-GF.csv.gz',
    'commodities/CME-LBS.csv.gz',
    'commodities/CME-LE.csv.gz',
    'commodities/CME-HE.csv.gz',
    'commodities/NYBOT-CT.csv.gz',
    'commodities/NYBOT-KC.csv.gz',
    'commodities/NYBOT-SB.csv.gz'
]

def convert_gz_to_csv(gz_file_path):
    csv_file_path = gz_file_path.replace('.csv.gz', '.csv')
    df = pd.read_csv(gz_file_path)
    df.to_csv(csv_file_path, index=False)
    return csv_file_path

for path in file_paths:
    new_csv_path = convert_gz_to_csv(path)
    print(f'Converted: {new_csv_path}')