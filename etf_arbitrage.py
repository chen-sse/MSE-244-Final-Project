import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import numpy as np

file_path = 'data/all_data_3.csv'
data = pd.read_csv(file_path)
data.head()
data.info()

date_column = data.columns[0]
data[date_column] = pd.to_datetime(data[date_column], errors='coerce')

start_date = '2010-01-01'
end_date = '2023-12-31'
filtered_data = data[(data[date_column] >= start_date) & (data[date_column] <= end_date)]

complete_data = filtered_data.dropna(axis=1, how='any')

complete_tickers = complete_data.columns[1:]
complete_tickers_list = complete_tickers.tolist()
print(complete_data.head(), complete_tickers_list)

def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    pairs = []
    
    for i in range(n):
        for j in range(i+1, n):
            S1 = data.iloc[:, i]
            S2 = data.iloc[:, j]
            score, pvalue, _ = coint(S1, S2)
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.05:
                pairs.append((data.columns[i], data.columns[j]))
    return score_matrix, pvalue_matrix, pairs

price_data = complete_data.set_index(date_column)
score_matrix, pvalue_matrix, pairs = find_cointegrated_pairs(price_data)
print(pairs)