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

industrylist = ['ALL', 'FARM', 'FFRA', 'MINE', 'UTIL', 'CNST',
                'DMAN', 'NMAN', 'WHTR', 'RETR', 'TRAN', 'INFO',
                'FINC', 'FINS', 'INSU', 'REAL', 'LEAS', 'PROF',
                'MGMT', 'ADMN', 'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS']

RAW_DATA_PATH = 'data_prep/historical_corp/'
OUTPUT_PATH = 'biztax/brc_data/'

# Import Excel file
taxfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '13co13ccr.xls'))

# Read data from the Excel file
data1 = pd.read_excel(taxfile, header=6)
data1.drop([74], axis=0, inplace=True)
data1.replace('[1]', 0., inplace=True)
data2 = data1.filter(items=['Unnamed: 0'])
data1.to_csv('testfile.csv')
data2.rename(columns={'Unnamed: 0': 'item'}, inplace=True)
data2['ALL'] = data1[1] / 10**6
data2['FARM'] = data1[3] / 10**6
data2['FFRA'] = (data1[2] - data1[3]) / 10**6
data2['MINE'] = data1[6] / 10**6
data2['UTIL'] = data1[7] / 10**6
data2['CNST'] = data1[8] / 10**6
data2['DMAN'] = (data1[18] + data1[24] + data1[25] + data1[26] +
	             data1[27] + data1[28] + data1[29] + data1[30] +
	             data1[31] + data1[32]) / 10**6
data2['NMAN'] = (data1[13] + data1[14] + data1[15] + data1[16] +
	             data1[17] + data1[19] + data1[20] + data1[21] +
	             data1[22] + data1[23]) / 10**6
data2['WHTR'] = data1[34] / 10**6
data2['RETR'] = data1[38] / 10**6
data2['TRAN'] = data1[52] / 10**6
data2['INFO'] = data1[59] / 10**6
data2['FINC'] = data1[67] / 10**6
data2['FINS'] = data1[68] / 10**6
data2['INSU'] = data1[69] / 10**6
data2['REAL'] = data1[72] / 10**6
data2['LEAS'] = (data1[73] + data1[74]) / 10**6
data2['PROF'] = data1[75] / 10**6
data2['MGMT'] = data1[76] / 10**6
data2['ADMN'] = data1[77] / 10**6
data2['EDUC'] = data1[80] / 10**6
data2['HLTH'] = data1[81] / 10**6
data2['ARTS'] = data1[85] / 10**6
data2['ACCM'] = data1[88] / 10**6
data2['OTHS'] = data1[91] / 10**6
# Replace dividends from domestic corporations with actual ones
data2.loc[41, industrylist] = data2.loc[41, industrylist] / 0.3
data2.to_csv(OUTPUT_PATH + 'corp_taxreturn_2013.csv', index=False)
