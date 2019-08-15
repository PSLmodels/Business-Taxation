"""
This file prepares earnings data on C corporations
for use by the Corporation class.

In its current form, it uses data for the total across
industries. When we begin splitting by industry, this will become more
relevant. For now, some odd formatting below is intended for
that future use.
"""

import numpy as np
import pandas as pd
import copy
import os

RAW_DATA_PATH = 'data_prep/historical_corp/'
OUTPUT_PATH = 'biztax/brc_data/'

# Import Excel file
taxfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '13co13ccr.xls'))

# Read data from the Excel file
data1 = pd.read_excel(taxfile, header=6)
data2 = data1.filter(items=['Unnamed: 0', 1])
data2.rename(columns={'Unnamed: 0': 'item', 1: 'amount'},
             inplace=True)
data3 = copy.deepcopy(data2)
data3['amount'] = data2['amount'] / 10**6
data3.to_csv(OUTPUT_PATH + 'corp_taxreturn_2013.csv', index=False)
