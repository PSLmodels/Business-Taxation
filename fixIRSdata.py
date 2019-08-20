"""
Due to appalling, inconsistent and embarrassingly
awful formatting decisions by the IRS in their Excel
files, these files must be cleaned up to be rendered
usable. This script reads in each file, cleans it up,
and saves the useful parts in a CSV.
"""

import numpy as np
import pandas as pd
import copy

industry_list = ['ALL', 'FARM', 'FFRA', 'MINE', 'UTIL', 'CNST',
                'DMAN', 'NMAN', 'WHTR', 'RETR', 'TRAN', 'INFO',
                'FINC', 'FINS', 'INSU', 'REAL', 'LEAS', 'PROF',
                'MGMT', 'ADMN', 'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS']

industry_column1 = {'ALL': [1],
                    'FARM': [3],
                    'FFRA': [4,5],
                    'MINE': [6],
                    'UTIL': [7],
                    'CNST': [8],
                    'DMAN': [18, 24, 25, 26, 27, 28, 29, 30, 31, 32],
                    'NMAN': [13, 14, 15, 16, 17, 19, 20, 21, 22, 23],
                    'WHTR': [34],
                    'RETR': [38],
                    'TRAN': [52],
                    'INFO': [59],
                    'FINC': [67],
                    'FINS': [68],
                    'INSU': [69],
                    'REAL': [72],
                    'LEAS': [73, 74],
                    'PROF': [75],
                    'MGMT': [76],
                    'ADMN': [77],
                    'EDUC': [80],
                    'HLTH': [81],
                    'ARTS': [85],
                    'ACCM': [88],
                    'OTHS': [91]}
industry_column2 = {'ALL': [1],
                    'FARM': [3],
                    'FFRA': [4,5],
                    'MINE': [6],
                    'UTIL': [7],
                    'CNST': [8],
                    'DMAN': [18, 24, 25, 26, 27, 28, 29, 30, 31, 32],
                    'NMAN': [13, 14, 15, 16, 17, 19, 20, 21, 22, 23],
                    'WHTR': [34],
                    'RETR': [38],
                    'TRAN': [52],
                    'INFO': [59],
                    'FINC': [68],
                    'FINS': [69],
                    'INSU': [70],
                    'REAL': [73],
                    'LEAS': [74, 75],
                    'PROF': [76],
                    'MGMT': [77],
                    'ADMN': [78],
                    'EDUC': [81],
                    'HLTH': [82],
                    'ARTS': [86],
                    'ACCM': [89],
                    'OTHS': [92]}
industry_column3 = {'ALL': [1],
                    'FARM': [3],
                    'FFRA': [4,5],
                    'MINE': [6],
                    'UTIL': [7],
                    'CNST': [8],
                    'DMAN': [18, 24, 25, 26, 27, 28, 29, 30, 31, 32],
                    'NMAN': [13, 14, 15, 16, 17, 19, 20, 21, 22, 23],
                    'WHTR': [34],
                    'RETR': [37],
                    'TRAN': [51],
                    'INFO': [58],
                    'FINC': [64],
                    'FINS': [65],
                    'INSU': [66],
                    'REAL': [69],
                    'LEAS': [70, 71],
                    'PROF': [72],
                    'MGMT': [73],
                    'ADMN': [74],
                    'EDUC': [77],
                    'HLTH': [78],
                    'ARTS': [82],
                    'ACCM': [86],
                    'OTHS': [88]}

col1 = ['Unnamed: 0']
col2 = ['Unnamed: 0']
col3 = ['Unnamed: 0']

for ind in industry_list:
    col1.extend(industry_column1[ind])
    col2.extend(industry_column2[ind])
    col3.extend(industry_column3[ind])

"""
SECTION 1. CORPORATE DATA
"""
RAW_DATA_PATH = 'data_prep/historical_corp/'
OUTPUT_PATH = 'biztax/brc_data/'
taxitems = ['Cash', 'Inventories', 'Land',
            'Total receipts','Business receipts', 
            'Interest income', 'Nontaxable interest income',
            'Rents', 'Royalties',
            'Net short-term capital gain reduced by net long-term capital loss',
            'Net long-term capital gain reduced by net short-term capital loss',
            'Net gain, noncapital assets', 'Dividends, domestic', 'Dividends, foreign',
            'Other receipts',
            'Total deductions',  'Cost of goods sold',
            'Compensation of officers', 'Salaries and wages',
            'Repairs', 'Bad debts', 'Rent paid on business property',
            'Taxes paid', 'Interest paid', 'Charitable contributions',
            'Amortization', 'Depreciation', 'Depletion',
            'Advertising',
            'Pension, profit sharing, stock, annuity', 'Employee benefit programs',
            'Domestic production income share',
            'Net loss, noncapital assets', 'Other deductions',
            'Total receipts less total deductions',
            'Constructive taxable income from related foreign corporations',
            'Net income', 'Income subject to tax',
            'Total income tax before credits', 'Income tax', 'Alternative minimum tax',
            'Foreign tax credit', 'General business credit', 'Prior year minimum tax credit',
            'Total income tax after credits']

# Read in the file for 2013
dc13a = pd.read_excel(RAW_DATA_PATH + '13co13ccr.xls', header=6)
# Drop unwanted asset lines
dc13a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc13a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc13a.drop([0, 74], axis=0, inplace=True)
# Remove unwanted columns
dc13b = dc13a.filter(items=col1)
# Remove unacceptable characters
dc13b.replace('[1]', 0., inplace=True)
dc13b.replace('*', '', inplace=True)
dc13b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc13b) == len(taxitems)
dc13b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc13c = dc13b.astype(float)
dc13c['items'] = taxitems
# Select the desired industries
dc13d = dc13c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc13c[col]
    dc13d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc13d.loc[12, industry_list] = dc13d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc13d.loc[31, industry_list] = (dc13d.loc[31, industry_list] / 0.09
                                / dc13d.loc[37, industry_list])
dc13d.to_csv(RAW_DATA_PATH + 'corp2013.csv', index=False)
# Also export as the 2013 tax return
dc13d.to_csv(OUTPUT_PATH + 'corp_taxreturn_2013.csv')

# Read in the file for 2012
dc12a = pd.read_excel(RAW_DATA_PATH + '12co13ccr.xls', header=13)
# Drop unwanted asset lines
dc12a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc12a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc12a.drop([0, 74, 75], axis=0, inplace=True)
# Remove unwanted columns
dc12b = dc12a.filter(items=col1)
# Remove unacceptable characters
dc12b.replace('[1]', 0., inplace=True)
dc12b.replace('*', '', inplace=True)
dc12b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc12b) == len(taxitems)
dc12b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc12c = dc12b.astype(float)
dc12c['items'] = taxitems
# Select the desired industries
dc12d = dc12c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc12c[col]
    dc12d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc12d.loc[12, industry_list] = dc12d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc12d.loc[31, industry_list] = (dc12d.loc[31, industry_list] / 0.09
                                / dc12d.loc[37, industry_list])
dc12d.to_csv(RAW_DATA_PATH + 'corp2012.csv', index=False)


# Read in the file for 2011
dc11a = pd.read_excel(RAW_DATA_PATH + '11co13ccr.xls', header=13)
# Drop unwanted asset lines
dc11a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc11a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc11a.drop([0, 74, 75], axis=0, inplace=True)
# Remove unwanted columns
dc11b = dc11a.filter(items=col1)
# Remove unacceptable characters
dc11b.replace('[1]', 0., inplace=True)
dc11b.replace('*', '', inplace=True)
dc11b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc11b) == len(taxitems)
dc11b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc11c = dc11b.astype(float)
dc11c['items'] = taxitems
# Select the desired industries
dc11d = dc11c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc11c[col]
    dc11d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc11d.loc[12, industry_list] = dc11d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc11d.loc[31, industry_list] = (dc11d.loc[31, industry_list] / 0.09
                                / dc11d.loc[37, industry_list])
dc11d.to_csv(RAW_DATA_PATH + 'corp2011.csv', index=False)

# Read in the file for 2010
dc10a = pd.read_excel(RAW_DATA_PATH + '10co13ccr.xls', header=13)
# Drop unwanted asset lines
dc10a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc10a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc10a.drop([0, 74, 75], axis=0, inplace=True)
# Remove unwanted columns
dc10b = dc10a.filter(items=col1)
# Remove unacceptable characters
dc10b.replace('[1]', 0., inplace=True)
dc10b.replace('*', '', inplace=True)
dc10b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc10b) == len(taxitems)
dc10b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc10c = dc10b.astype(float)
dc10c['items'] = taxitems
# Select the desired industries
dc10d = dc10c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc10c[col]
    dc10d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc10d.loc[12, industry_list] = dc10d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc10d.loc[31, industry_list] = (dc10d.loc[31, industry_list] / 0.09
                                / dc10d.loc[37, industry_list])
dc10d.to_csv(RAW_DATA_PATH + 'corp2010.csv', index=False)

# Read in the file for 2009
dc09a = pd.read_excel(RAW_DATA_PATH + '09co13ccr.xls', header=14)
# Drop unwanted asset lines
dc09a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc09a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc09a.drop([0, 74, 75], axis=0, inplace=True)
# Remove unwanted columns
dc09b = dc09a.filter(items=col1)
# Remove unacceptable characters
dc09b.replace('[1]', 0., inplace=True)
dc09b.replace('*', '', inplace=True)
dc09b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc09b) == len(taxitems)
dc09b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc09c = dc09b.astype(float)
dc09c['items'] = taxitems
# Select the desired industries
dc09d = dc09c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc09c[col]
    dc09d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc09d.loc[12, industry_list] = dc09d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc09d.loc[31, industry_list] = (dc09d.loc[31, industry_list] / 0.09
                                / dc09d.loc[37, industry_list])
dc09d.to_csv(RAW_DATA_PATH + 'corp2009.csv', index=False)

# Read in the file for 2008
dc08a = pd.read_excel(RAW_DATA_PATH + '08co13ccr.xls', header=13)
# Drop unwanted asset lines
dc08a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc08a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc08a.drop([0, 74, 75], axis=0, inplace=True)
# Remove unwanted columns
dc08b = dc08a.filter(items=col1)
# Remove unacceptable characters
dc08b.replace('[1]', 0., inplace=True)
dc08b.replace('*', '', inplace=True)
dc08b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc08b) == len(taxitems)
dc08b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc08c = dc08b.astype(float)
dc08c['items'] = taxitems
# Select the desired industries
dc08d = dc08c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += dc08c[col]
    dc08d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc08d.loc[12, industry_list] = dc08d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc08d.loc[31, industry_list] = (dc08d.loc[31, industry_list] / 0.09
                                / dc08d.loc[37, industry_list])
dc08d.to_csv(RAW_DATA_PATH + 'corp2008.csv', index=False)

# Read in the file for 2007
dc07a = pd.read_excel(RAW_DATA_PATH + '07co13ccr.xls', header=13)
# Drop unwanted asset lines
dc07a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc07a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
dc07a.drop([0, 35, 75, 76], axis=0, inplace=True)
# Remove unwanted columns
dc07b = dc07a.filter(items=col2)
# Remove unacceptable characters
dc07b.replace('[1]', 0., inplace=True)
dc07b.replace('*', '', inplace=True)
dc07b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc07b) == len(taxitems)
dc07b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc07c = dc07b.astype(float)
dc07c['items'] = taxitems
# Select the desired industries
dc07d = dc07c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc07c[col]
    dc07d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc07d.loc[12, industry_list] = dc07d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc07d.loc[31, industry_list] = (dc07d.loc[31, industry_list] / 0.09
                                / dc07d.loc[37, industry_list])
dc07d.to_csv(RAW_DATA_PATH + 'corp2007.csv', index=False)

# Read in the file for 2006
dc06a = pd.read_excel(RAW_DATA_PATH + '06co13ccr.xls', header=13)
# Drop unwanted asset lines
dc06a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc06a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc06a.drop([0, 37, 41, 43, 69, 77, 81, 82], axis=0, inplace=True)
# Remove unwanted columns
dc06b = dc06a.filter(items=col2)
# Remove unacceptable characters
dc06b.replace('[1]', 0., regex=True, inplace=True)
dc06b.replace(r'\*', '', regex=True, inplace=True)
dc06b.replace('-', 0., inplace=True)
dc06b.replace(r'\,', '', regex=True, inplace=True)
dc06b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc06b) == len(taxitems)
dc06b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc06c = dc06b.astype(float)
dc06c['items'] = taxitems
# Select the desired industries
dc06d = dc06c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc06c[col]
    dc06d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc06d.loc[12, industry_list] = dc06d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc06d.loc[31, industry_list] = (dc06d.loc[31, industry_list] / 0.09
                                / dc06d.loc[37, industry_list])
dc06d.to_csv(RAW_DATA_PATH + 'corp2006.csv', index=False)


# Read in the file for 2005
dc05a = pd.read_excel(RAW_DATA_PATH + '05co13ccr.xls', header=13)
# Drop unwanted asset lines
dc05a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc05a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc05a.drop([0, 37, 41, 43, 69, 77, 78, 82, 83], axis=0, inplace=True)
# Remove unwanted columns
dc05b = dc05a.filter(items=col2)
# Remove unacceptable characters
dc05b.replace('[1]', 0., regex=True, inplace=True)
dc05b.replace(r'\*', '', regex=True, inplace=True)
dc05b.replace('-', 0., inplace=True)
dc05b.replace(r'\,', '', regex=True, inplace=True)
dc05b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(dc05b) == len(taxitems)
dc05b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc05c = dc05b.astype(float)
dc05c['items'] = taxitems
# Select the desired industries
dc05d = dc05c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc05c[col]
    dc05d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc05d.loc[12, industry_list] = dc05d.loc[12, industry_list] / 0.3
# Compute DPAD-eligible share of taxable income
dc05d.loc[31, industry_list] = (dc05d.loc[31, industry_list] / 0.09
                                / dc05d.loc[37, industry_list])
dc05d.to_csv(RAW_DATA_PATH + 'corp2005.csv', index=False)

# Read in the file for 2004
dc04a = pd.read_excel(RAW_DATA_PATH + '04co13ccr.xls', header=13)
# Drop unwanted asset lines
dc04a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc04a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc04a.drop([0, 37, 41, 43, 68, 76, 77, 81, 82], axis=0, inplace=True)
# Remove unwanted columns
dc04b = dc04a.filter(items=col2)
# Remove unacceptable characters
dc04b.replace('[1]', 0., regex=True, inplace=True)
dc04b.replace(r'\*', '', regex=True, inplace=True)
dc04b.replace('-', 0., inplace=True)
dc04b.replace(r'\,', '', regex=True, inplace=True)
dc04b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
dc04b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc04c1 = dc04b.astype(float)
# Insert zeros for domestic production deduction
dc04c2 = copy.deepcopy(dc04c1.iloc[:31])
newrow = pd.DataFrame(np.zeros((1,len(col2)-1)), columns=col2[1:])
dc04c3 = dc04c2.append(newrow, ignore_index=True)
dc04c4 = copy.deepcopy(dc04c1.iloc[31:])
dc04c5 = dc04c3.append(dc04c4, ignore_index=True)
assert len(dc04c5) == len(taxitems)
dc04c5['items'] = taxitems
# Select the desired industries
dc04d = dc04c5.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc04c5[col]
    dc04d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc04d.loc[12, industry_list] = dc04d.loc[12, industry_list] / 0.3
dc04d.to_csv(RAW_DATA_PATH + 'corp2004.csv', index=False)

# Read in the file for 2003
dc03a = pd.read_excel(RAW_DATA_PATH + '03co13mi.xls', header=12)
# Drop unwanted asset lines
dc03a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc03a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc03a.drop([0, 37, 41, 43, 63, 69, 77, 78, 82], axis=0, inplace=True)
dc03a.drop([83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93], axis=0, inplace=True)
# Remove unwanted columns
dc03b = dc03a.filter(items=col2)
# Remove unacceptable characters
dc03b.replace('[1]', 0., inplace=True)
dc03b.replace(r'\*', '', regex=True, inplace=True)
dc03b.replace('-', 0., inplace=True)
dc03b.replace(r'\,', '', regex=True, inplace=True)
dc03b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
dc03b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc03c1 = dc03b.astype(float)
# Insert zeros for domestic production deduction
dc03c2 = copy.deepcopy(dc03c1.iloc[:31])
newrow = pd.DataFrame(np.zeros((1,len(col2)-1)), columns=col2[1:])
dc03c3 = dc03c2.append(newrow, ignore_index=True)
dc03c4 = copy.deepcopy(dc03c1.iloc[31:])
dc03c5 = dc03c3.append(dc03c4, ignore_index=True)
assert len(dc03c5) == len(taxitems)
dc03c5['items'] = taxitems
# Select the desired industries
dc03d = dc03c5.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc03c5[col]
    dc03d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc03d.loc[12, industry_list] = dc03d.loc[12, industry_list] / 0.3
dc03d.to_csv(RAW_DATA_PATH + 'corp2003.csv', index=False)

# Read in the file for 2002
dc02a = pd.read_excel(RAW_DATA_PATH + '02co13mi.xls', header=12)
# Drop unwanted asset lines
dc02a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc02a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc02a.drop([0, 37, 41, 43, 63, 69, 77, 78, 82], axis=0, inplace=True)
dc02a.drop([83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93], axis=0, inplace=True)
# Remove unwanted columns
dc02b = dc02a.filter(items=col2)
# Remove unacceptable characters
dc02b.replace('[1]', 0., inplace=True)
dc02b.replace(r'\*', '', regex=True, inplace=True)
dc02b.replace('-', 0., inplace=True)
dc02b.replace(r'\,', '', regex=True, inplace=True)
dc02b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
dc02b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc02c1 = dc02b.astype(float)
# Insert zeros for domestic production deduction
dc02c2 = copy.deepcopy(dc02c1.iloc[:31])
newrow = pd.DataFrame(np.zeros((1,len(col2)-1)), columns=col2[1:])
dc02c3 = dc03c2.append(newrow, ignore_index=True)
dc02c4 = copy.deepcopy(dc02c1.iloc[31:])
dc02c5 = dc02c3.append(dc02c4, ignore_index=True)
assert len(dc02c5) == len(taxitems)
dc02c5['items'] = taxitems
# Select the desired industries
dc02d = dc02c5.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += dc02c5[col]
    dc02d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc02d.loc[12, industry_list] = dc02d.loc[12, industry_list] / 0.3
dc02d.to_csv(RAW_DATA_PATH + 'corp2002.csv', index=False)

# Read in the file for 2001
dc01a = pd.read_excel(RAW_DATA_PATH + '01co13mi.xls', header=12, nrows=82)
# Drop unwanted asset lines
dc01a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc01a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
dc01a.drop([0, 37, 41, 43, 62, 68, 76, 77, 81], axis=0, inplace=True)
# Remove unwanted columns
dc01b = dc01a.filter(items=col3)
# Remove unacceptable characters
dc01b.replace('[1]', 0., inplace=True)
dc01b.replace(r'\*', '', regex=True, inplace=True)
dc01b.replace('-', 0., inplace=True)
dc01b.replace(r'\,', '', regex=True, inplace=True)
dc01b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
dc01b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc01c1 = dc01b.astype(float)
# Insert zeros for salaries and domestic production deduction
dc01c2 = copy.deepcopy(dc01c1.iloc[:18])
newrow = pd.DataFrame(np.zeros((1,len(col3)-1)), columns=col3[1:])
dc01c3 = dc01c2.append(newrow, ignore_index=True)
dc01c4 = copy.deepcopy(dc01c1.iloc[18:30])
dc01c5 = dc01c3.append(dc01c4, ignore_index=True)
dc01c6 = dc01c5.append(newrow, ignore_index=True)
dc01c7 = copy.deepcopy(dc01c1.iloc[30:])
dc01c8 = dc01c6.append(dc01c7, ignore_index=True)
assert len(dc01c8) == len(taxitems)
dc01c8['items'] = taxitems
# Select the desired industries
dc01d = dc01c8.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column3[ind]:
        ser1 += dc01c8[col]
    dc01d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc01d.loc[12, industry_list] = dc01d.loc[12, industry_list] / 0.3
dc01d.to_csv(RAW_DATA_PATH + 'corp2001.csv', index=False)

# Read in the file for 2000
dc00a = pd.read_excel(RAW_DATA_PATH + '00co13mi.xls', header=13)
# Drop unwanted asset lines
dc00a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
dc00a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34], axis=0, inplace=True)
# Drop other unwanted lines
dc00a.drop([0, 38, 42, 44, 64, 70, 76, 77, 80, 81, 85], axis=0, inplace=True)
dc00a.drop([86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98], axis=0, inplace=True)
# Remove unwanted columns
dc00b = dc00a.filter(items=col3)
# Remove unacceptable characters
dc00b.replace('[1]', 0., inplace=True)
dc00b.replace(r'\*', '', regex=True, inplace=True)
dc00b.replace('-', 0., inplace=True)
dc00b.replace(r'\,', '', regex=True, inplace=True)
dc00b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
dc00b.drop(['Unnamed: 0'], axis=1, inplace=True)
dc00c1 = dc00b.astype(float)
# Insert zeros for domestic production deduction
dc00c2 = copy.deepcopy(dc00c1.iloc[:31])
newrow = pd.DataFrame(np.zeros((1,len(col3)-1)), columns=col3[1:])
dc00c3 = dc00c2.append(newrow, ignore_index=True)
dc00c4 = copy.deepcopy(dc00c1.iloc[31:])
dc00c5 = dc00c3.append(dc00c4, ignore_index=True)
assert len(dc00c5) == len(taxitems)
dc00c5['items'] = taxitems
# Select the desired industries
dc00d = dc00c5.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column3[ind]:
        ser1 += dc00c5[col]
    dc00d[ind] = ser1 / 10**6
# Fix dividends from domestic corporations
dc00d.loc[12, industry_list] = dc00d.loc[12, industry_list] / 0.3
dc00d.to_csv(RAW_DATA_PATH + 'corp2000.csv', index=False)






"""
SECTION 2. S CORPORATION DATA
"""
RAW_DATA_PATH = 'data_prep/historical_scorp/'
OUTPUT_PATH = 'biztax/brc_data/'
taxitems = ['Cash', 'Inventories', 'Land',
            'Total receipts','Business receipts', 
            'Net gain, noncapital assets', 'Other receipts',
            'Total deductions',  'Cost of goods sold',
            'Compensation of officers', 'Salaries and wages',
            'Repairs', 'Bad debts', 'Rent paid on business property',
            'Taxes paid', 'Interest paid',
            'Amortization', 'Depreciation', 'Depletion',
            'Advertising',
            'Pension, profit sharing, stock, annuity', 'Employee benefit programs',
            'Net loss, noncapital assets', 'Other deductions',
            'Total receipts less total deductions', 'Net income']

# Read in the file for 2013
ds13a = pd.read_excel(RAW_DATA_PATH + '13co07s.xls', header=6)
# Drop unwanted asset lines
ds13a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds13a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds13a.drop([0, 1, 32, 35, 57, 58, 59, 60], axis=0, inplace=True)
# Remove unwanted columns
ds13b = ds13a.filter(items=col1)
# Remove unacceptable characters
ds13b.replace('[1]', 0., inplace=True)
ds13b.replace('*', '', inplace=True)
ds13b.replace('d', 0., inplace=True)
ds13b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds13b) == len(taxitems)
ds13b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds13c = ds13b.astype(float)
ds13c['items'] = taxitems
# Select the desired industries
ds13d = ds13c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds13c[col]
    ds13d[ind] = ser1 / 10**6
ds13d.to_csv(RAW_DATA_PATH + 'scorp2013.csv', index=False)

# Read in the file for 2012
ds12a = pd.read_excel(RAW_DATA_PATH + '12co07s.xls', header=12)
# Drop unwanted asset lines
ds12a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds12a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds12a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds12b = ds12a.filter(items=col1)
# Remove unacceptable characters
ds12b.replace('[1]', 0., inplace=True)
ds12b.replace('*', '', inplace=True)
ds12b.replace('d', 0., inplace=True)
ds12b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds12b) == len(taxitems)
ds12b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds12c = ds12b.astype(float)
ds12c['items'] = taxitems
# Select the desired industries
ds12d = ds12c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds12c[col]
    ds12d[ind] = ser1 / 10**6
ds12d.to_csv(RAW_DATA_PATH + 'scorp2012.csv', index=False)

# Read in the file for 2011
ds11a = pd.read_excel(RAW_DATA_PATH + '11co07s.xls', header=12)
# Drop unwanted asset lines
ds11a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds11a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds11a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds11b = ds11a.filter(items=col1)
# Remove unacceptable characters
ds11b.replace('[1]', 0., inplace=True)
ds11b.replace('*', '', inplace=True)
ds11b.replace('d', 0., inplace=True)
ds11b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds11b) == len(taxitems)
ds11b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds11c = ds11b.astype(float)
ds11c['items'] = taxitems
# Select the desired industries
ds11d = ds11c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds11c[col]
    ds11d[ind] = ser1 / 10**6
ds11d.to_csv(RAW_DATA_PATH + 'scorp2011.csv', index=False)

# Read in the file for 2010
ds10a = pd.read_excel(RAW_DATA_PATH + '10co07s.xls', header=11)
# Drop unwanted asset lines
ds10a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds10a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds10a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds10b = ds10a.filter(items=col1)
# Remove unacceptable characters
ds10b.replace('[1]', 0., inplace=True)
ds10b.replace('*', '', inplace=True)
ds10b.replace('d', 0., inplace=True)
ds10b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds10b) == len(taxitems)
ds10b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds10c = ds10b.astype(float)
ds10c['items'] = taxitems
# Select the desired industries
ds10d = ds10c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds10c[col]
    ds10d[ind] = ser1 / 10**6
ds10d.to_csv(RAW_DATA_PATH + 'scorp2010.csv', index=False)

# Read in the file for 2009
ds09a = pd.read_excel(RAW_DATA_PATH + '09co07s.xls', header=12)
# Drop unwanted asset lines
ds09a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds09a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds09a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds09b = ds09a.filter(items=col1)
# Remove unacceptable characters
ds09b.replace('[1]', 0., inplace=True)
ds09b.replace('*', '', inplace=True)
ds09b.replace('d', 0., inplace=True)
ds09b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds09b) == len(taxitems)
ds09b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds09c = ds09b.astype(float)
ds09c['items'] = taxitems
# Select the desired industries
ds09d = ds09c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds09c[col]
    ds09d[ind] = ser1 / 10**6
ds09d.to_csv(RAW_DATA_PATH + 'scorp2009.csv', index=False)

# Read in the file for 2008
ds08a = pd.read_excel(RAW_DATA_PATH + '08co07s.xls', header=12)
# Drop unwanted asset lines
ds08a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds08a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds08a.drop([0, 1, 34, 56, 57, 58], axis=0, inplace=True)
# Remove unwanted columns
ds08b = ds08a.filter(items=col1)
# Remove unacceptable characters
ds08b.replace('[1]', 0., inplace=True)
ds08b.replace('*', '', inplace=True)
ds08b.replace('d', 0., inplace=True)
ds08b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds08b) == len(taxitems)
ds08b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds08c = ds08b.astype(float)
ds08c['items'] = taxitems
# Select the desired industries
ds08d = ds08c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds08c[col]
    ds08d[ind] = ser1 / 10**6
ds08d.to_csv(RAW_DATA_PATH + 'scorp2008.csv', index=False)

# Read in the file for 2007
ds07a = pd.read_excel(RAW_DATA_PATH + '07co07s.xls', header=13)
# Drop unwanted asset lines
ds07a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds07a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds07a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds07b = ds07a.filter(items=col1)
# Remove unacceptable characters
ds07b.replace('[1]', 0., inplace=True)
ds07b.replace('*', '', inplace=True)
ds07b.replace('d', 0., inplace=True)
ds07b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds07b) == len(taxitems)
ds07b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds07c = ds07b.astype(float)
ds07c['items'] = taxitems
# Select the desired industries
ds07d = ds07c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column1[ind]:
        ser1 += ds07c[col]
    ds07d[ind] = ser1 / 10**6
ds07d.to_csv(RAW_DATA_PATH + 'scorp2007.csv', index=False)

# Read in the file for 2006
ds06a = pd.read_excel(RAW_DATA_PATH + '06co07s.xls', header=12)
# Drop unwanted asset lines
ds06a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds06a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds06a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds06b = ds06a.filter(items=col2)
# Remove unacceptable characters
ds06b.replace('[1]', 0., inplace=True)
ds06b.replace(r'\*', '', regex=True, inplace=True)
ds06b.replace('d', 0., inplace=True)
ds06b.replace('-', 0., inplace=True)
ds06b.replace(r'\,', '', regex=True, inplace=True)
ds06b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds06b) == len(taxitems)
ds06b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds06c = ds06b.astype(float)
ds06c['items'] = taxitems
# Select the desired industries
ds06d = ds06c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += ds06c[col]
    ds06d[ind] = ser1 / 10**6
ds06d.to_csv(RAW_DATA_PATH + 'scorp2006.csv', index=False)

# Read in the file for 2005
ds05a = pd.read_excel(RAW_DATA_PATH + '05co1120s07.xls', header=12)
# Drop unwanted asset lines
ds05a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds05a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds05a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds05b = ds05a.filter(items=col2)
# Remove unacceptable characters
ds05b.replace('[1]', 0., inplace=True)
ds05b.replace(r'\*', '', regex=True, inplace=True)
ds05b.replace('d', 0., inplace=True)
ds05b.replace('-', 0., inplace=True)
ds05b.replace(r'\,', '', regex=True, inplace=True)
ds05b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds05b) == len(taxitems)
ds05b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds05c = ds05b.astype(float)
ds05c['items'] = taxitems
# Select the desired industries
ds05d = ds05c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += ds05c[col]
    ds05d[ind] = ser1 / 10**6
ds05d.to_csv(RAW_DATA_PATH + 'scorp2005.csv', index=False)

# Read in the file for 2004
ds04a = pd.read_excel(RAW_DATA_PATH + '04co14ccr.xls', header=12)
# Drop unwanted asset lines
ds04a.drop([2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20], axis=0, inplace=True)
# Drop unwanted liability lines
ds04a.drop([21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31], axis=0, inplace=True)
# Drop other unwanted lines
ds04a.drop([0, 1, 34, 56, 57, 58, 59], axis=0, inplace=True)
# Remove unwanted columns
ds04b = ds04a.filter(items=col2)
# Remove unacceptable characters
ds04b.replace('[1]', 0., inplace=True)
ds04b.replace(r'\*', '', regex=True, inplace=True)
ds04b.replace('d', 0., inplace=True)
ds04b.replace('-', 0., inplace=True)
ds04b.replace(r'\,', '', regex=True, inplace=True)
ds04b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds04b) == len(taxitems)
ds04b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds04c = ds04b.astype(float)
ds04c['items'] = taxitems
# Select the desired industries
ds04d = ds04c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += ds04c[col]
    ds04d[ind] = ser1 / 10**6
ds04d.to_csv(RAW_DATA_PATH + 'scorp2004.csv', index=False)

# Read in the file for 2003
ds03a = pd.read_excel(RAW_DATA_PATH + '03co14bs.xls', header=12)
# Drop unwanted asset lines
ds03a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
ds03a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], axis=0, inplace=True)
# Drop other unwanted lines
ds03a.drop([0, 35, 36, 52, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68], axis=0, inplace=True)
# Remove unwanted columns
ds03b = ds03a.filter(items=col2)
# Remove unacceptable characters
ds03b.replace('[1]', 0., inplace=True)
ds03b.replace(r'\*', '', regex=True, inplace=True)
ds03b.replace('d', 0., inplace=True)
ds03b.replace('-', 0., inplace=True)
ds03b.replace(r'\,', '', regex=True, inplace=True)
ds03b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds03b) == len(taxitems)
ds03b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds03c = ds03b.astype(float)
ds03c['items'] = taxitems
# Select the desired industries
ds03d = ds03c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += ds03c[col]
    ds03d[ind] = ser1 / 10**6
ds03d.to_csv(RAW_DATA_PATH + 'scorp2003.csv', index=False)

# Read in the file for 2002
ds02a = pd.read_excel(RAW_DATA_PATH + '02co14bs.xls', header=12)
# Drop unwanted asset lines
ds02a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
ds02a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], axis=0, inplace=True)
# Drop other unwanted lines
ds02a.drop([0, 35, 36, 52, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68], axis=0, inplace=True)
# Remove unwanted columns
ds02b = ds02a.filter(items=col2)
# Remove unacceptable characters
ds02b.replace('[1]', 0., inplace=True)
ds02b.replace(r'\*\*\*', 0., regex=True, inplace=True)
ds02b.replace(r'\*', '', regex=True, inplace=True)
ds02b.replace('d', 0., inplace=True)
ds02b.replace('-', 0., inplace=True)
ds02b.replace(r'\,', '', regex=True, inplace=True)
ds02b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds02b) == len(taxitems)
ds02b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds02c = ds02b.astype(float)
ds02c['items'] = taxitems
# Select the desired industries
ds02d = ds02c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column2[ind]:
        ser1 += ds02c[col]
    ds02d[ind] = ser1 / 10**6
ds02d.to_csv(RAW_DATA_PATH + 'scorp2002.csv', index=False)

# Read in the file for 2001
ds01a = pd.read_excel(RAW_DATA_PATH + '01co14bs.xls', header=12, nrows=62)
# Drop unwanted asset lines
ds01a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
ds01a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], axis=0, inplace=True)
# Drop other unwanted lines
ds01a.drop([0, 35, 36, 51, 58, 59, 60, 61], axis=0, inplace=True)
# Remove unwanted columns
ds01b = ds01a.filter(items=col3)
# Remove unacceptable characters
ds01b.replace('[1]', 0., inplace=True)
ds01b.replace(r'\*\*\*', 0., regex=True, inplace=True)
ds01b.replace(r'\*', '', regex=True, inplace=True)
ds01b.replace('d', 0., inplace=True)
ds01b.replace('-', 0., inplace=True)
ds01b.replace(r'\,', '', regex=True, inplace=True)
ds01b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
ds01b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds01c1 = ds01b.astype(float)
# Insert missing salary data
ds01c2 = copy.deepcopy(ds01c1.iloc[:10])
newrow = pd.DataFrame(np.zeros((1,len(col3)-1)), columns=col3[1:])
ds01c3 = ds01c2.append(newrow, ignore_index=True)
ds01c4 = copy.deepcopy(ds01c1.iloc[10:])
ds01c5 = ds01c3.append(ds01c4, ignore_index=True)
assert len(ds01c5) == len(taxitems)
ds01c5['items'] = taxitems
# Select the desired industries
ds01d = ds01c5.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column3[ind]:
        ser1 += ds01c5[col]
    ds01d[ind] = ser1 / 10**6
ds01d.to_csv(RAW_DATA_PATH + 'scorp2001.csv', index=False)

# Read in the file for 2000
ds00a = pd.read_excel(RAW_DATA_PATH + '00co14bs.xls', header=12, nrows=62)
ds00a.drop([1, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19], axis=0, inplace=True)
# Drop unwanted liability lines
ds00a.drop([20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33], axis=0, inplace=True)
# Drop other unwanted lines
ds00a.drop([0, 36, 37, 53, 60, 61], axis=0, inplace=True)
# Remove unwanted columns
ds00a.rename({-5: 5}, axis=1, inplace=True)
ds00b = ds00a.filter(items=col3)
# Remove unacceptable characters
ds00b.replace('[1]', 0., inplace=True)
ds00b.replace(r'\*\*\*', 0., regex=True, inplace=True)
ds00b.replace(r'\*', '', regex=True, inplace=True)
ds00b.replace('d', 0., inplace=True)
ds00b.replace('-', 0., inplace=True)
ds00b.replace(r'\,', '', regex=True, inplace=True)
ds00b.reset_index(inplace=True, drop=True)
# Ensure everything in float format
assert len(ds00b) == len(taxitems)
ds00b.drop(['Unnamed: 0'], axis=1, inplace=True)
ds00c = ds00b.astype(float)
ds00c['items'] = taxitems
# Select the desired industries
ds00d = ds00c.filter(items=['items'])
for ind in industry_list:
    ser1 = np.zeros(len(taxitems))
    for col in industry_column3[ind]:
        ser1 += ds00c[col]
    ds00d[ind] = ser1 / 10**6
ds00d.to_csv(RAW_DATA_PATH + 'scorp2000.csv', index=False)


