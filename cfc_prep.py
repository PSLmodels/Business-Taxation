"""
This file prepares the data for use by the Asset class.
It begins with the detailed asset types by industry from the BEA. 

Note that the current approach is very simple, only using totals
for all CFCs and all majority-owned foreign affiliates. Future
improvements would use data by country and potentially by country
and industry. 
"""

import numpy as np
import pandas as pd
import copy
import os
from biztax.data import Data
from biztax.asset import Asset
from biztax.policy import Policy
from biztax.cfc import CFC
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS, HISTORY_START

RAW_DATA_PATH = 'data_prep/international/'
OUTPUT_PATH = 'biztax/brc_data/'

# Import all Excel files
# CFC data by industry
cfc_industry = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '14it01cfr.xls'))
# CFC data by country of incorporation
cfc_country = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '14it02cfr.xls'))
# Balance sheet data of majority-owned foreign affiliates
bal_mofa = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'PartII-B1-B12.xls'))
# Balance sheet data of US parent companies
bal_parent = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'PartI-L1-M2.xls'))
# Income and sales of US parent companies
inc_parent = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'PartI-N1-P1.xls'))






"""
SECTION 1. DATA ON CONTROLLED FOREIGN CORPORATIONS

The data come from IRS SOI data on CFCs.
"""
# Read relevant data
cfc_raw = pd.read_excel(cfc_industry, header=6)
cfc1 = cfc_raw.filter(items=['All industries              ', '(4)',
	                         '(7)', '(8)', '(16)', '(17)', '(19)'])
cfc1.rename(columns={'All industries              ': 'industry',
	                 '(4)': 'assets', '(7)': 'earnings',
	                 '(8)': 'foreigntax', '(16)': 'divpaid',
	                 '(17)': 'subpartF', '(19)': 'accum'},
	        inplace=True)
# Combine industry groups to match preferred industries
cols = ['industry', 'assets', 'profits', 'foreigntax',
        'divpaid', 'subpartF', 'accum']
cfc2 = copy.deepcopy(cfc1).transpose()
cfc2['ALL'] = cfc2[0]
cfc2['FARM'] = cfc2[2]
cfc2['FFRA'] = 0.
cfc2['MINE'] = cfc2[3]
cfc2['UTIL'] = cfc2[6]
cfc2['CNST'] = cfc2[8]
cfc2['DMAN'] = (cfc2[23] + cfc2[24] + cfc2[25] + cfc2[26] +
	            cfc2[31] + cfc2[36] + cfc2[37] + cfc2[40] + cfc2[43])
cfc2['NMAN'] = (cfc2[10] + cfc2[11] + cfc2[14] + cfc2[15] +
	            cfc2[16] + cfc2[22])
cfc2['WHTR'] = cfc2[46]
cfc2['RETR'] = cfc2[58]
cfc2['TRAN'] = cfc2[61]
cfc2['INFO'] = cfc2[64]
cfc2['FINC'] = cfc2[73]
cfc2['FINS'] = cfc2[76]
cfc2['INSU'] = cfc2[79]
cfc2['REAL'] = cfc2[84]
cfc2['LEAS'] = cfc2[85]
cfc2['PROF'] = cfc2[87]
cfc2['MGMT'] = cfc2[93]
cfc2['ADMN'] = cfc2[96]
cfc2['EDUC'] = 0.
cfc2['HLTH'] = 0.
cfc2['ARTS'] = cfc2[97]
cfc2['ACCM'] = cfc2[98]
cfc2['OTHS'] = cfc2[99] + cfc2[100]
cfc3 = cfc2.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                      'UTIL', 'CNST', 'DMAN', 'NMAN',
	                      'WHTR', 'RETR', 'TRAN', 'INFO',
	                      'FINC', 'FINS', 'INSU', 'REAL',
	                      'LEAS', 'PROF', 'MGMT', 'ADMN',
	                      'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
cfc3.drop(['industry'], axis=0, inplace=True)
cfc4 = cfc3.transpose()
# Fix the scales
cfc5 = cfc4 / 10**9
# Compute foreign tax rate and repatriation rates
cfc5['taxrt'] = cfc5['foreigntax'] / (cfc5['earnings'] + 0.000001)
cfc5['reprate_e'] = cfc5['divpaid'] / (cfc5['earnings'] - cfc5['foreigntax'] - cfc5['subpartF'] + 0.000001)
cfc5['reprate_a'] = 0.
# Fix accumulated untaxed earnings to starting value
cfc5['accum'] = (cfc5['accum'] - (cfc5['earnings'] -
	             cfc5['divpaid'] * (1 + cfc5['taxrt']) -
	             cfc5['subpartF']))



"""
SECTION 2. DATA ON MAJORITY-OWNED FOREIGN AFFILIATES

The data come from BEA data on majority-owned foreign affiliates
of US MNEs. This includes CFCs, foreign branches, and majority-owned
foreign disregarded entities.

The data in this section are used to estimate data on real activity
for CFCs. Currently, this is only for net PPE, which will be necessary
to model GILTI. In the future, we could also add CapEx, R&D and other
activities.
"""
mofa_raw = pd.read_excel(bal_mofa, sheet_name='Table II.B 3', header=7)
mofa1 = mofa_raw.filter(['Unnamed: 0', '(1)', '(5)'])
mofa1.rename(columns={'Unnamed: 0': 'industry',
	                  '(1)': 'assets', '(5)': 'ppe'}, inplace=True)
mofa2 = mofa1.transpose()

mofa2['ALL'] = mofa2[0]
mofa2['FARM'] = mofa2[82]
mofa2['FFRA'] = mofa2[82]
mofa2['MINE'] = mofa2[2]
mofa2['UTIL'] = mofa2[84]
mofa2['CNST'] = mofa2[83]
mofa2['DMAN'] = (mofa2[11] + mofa2[24] + mofa2[25] + mofa2[29] +
	             mofa2[29] + mofa2[34] + mofa2[42] + mofa2[43] +
	             mofa2[46] + mofa2[47])
mofa2['NMAN'] = (mofa2[8] + mofa2[9] + mofa2[10] + mofa2[12] +
	             mofa2[13] + mofa2[14] + mofa2[16] + mofa2[23])
mofa2['WHTR'] = mofa2[49]
mofa2['RETR'] = mofa2[55]
mofa2['TRAN'] = mofa2[85]
mofa2['INFO'] = mofa2[60]
mofa2['FINC'] = mofa2[70]
mofa2['FINS'] = mofa2[71]
mofa2['INSU'] = mofa2[72]
mofa2['REAL'] = mofa2[86]
mofa2['LEAS'] = mofa2[86]
mofa2['PROF'] = mofa2[74]
mofa2['MGMT'] = mofa2[87]
mofa2['ADMN'] = mofa2[88]
mofa2['EDUC'] = mofa2[91]
mofa2['HLTH'] = mofa2[89]
mofa2['ARTS'] = mofa2[91]
mofa2['ACCM'] = mofa2[90]
mofa2['OTHS'] = mofa2[91]


mofa3 = mofa2.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                        'UTIL', 'CNST', 'DMAN', 'NMAN',
	                        'WHTR', 'RETR', 'TRAN', 'INFO',
	                        'FINC', 'FINS', 'INSU', 'REAL',
	                        'LEAS', 'PROF', 'MGMT', 'ADMN',
	                        'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
mofa3.drop(['industry'], axis=0, inplace=True)
mofa4 = mofa3.transpose()
# Fix scale
mofa4 = mofa4 / 1000.

# Use MOFA PPE data for CFCs
cfc5['ppe'] = mofa4['ppe'] * cfc5['assets'] / mofa4['assets']


cfc5.to_csv(OUTPUT_PATH + 'cfc_data.csv')

