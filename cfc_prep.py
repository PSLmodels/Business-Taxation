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
cfc_industry = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '14it01cfr.xls'))
cfc_country = pd.ExcelFile(os.path.join(RAW_DATA_PATH, '14it02cfr.xls'))
mne_mofa = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'PartII-B1-B12.xls'))

# Level measures to save for use in CFC class
assets_arr = np.zeros(NUM_YEARS)
ppe_arr = np.zeros(NUM_YEARS)
earnings_arr = np.zeros(NUM_YEARS)
subpartF_arr = np.zeros(NUM_YEARS)
startAccum_arr = np.zeros(NUM_YEARS)


"""
SECTION 1. DATA ON CONTROLLED FOREIGN CORPORATIONS

The data come from IRS SOI data on CFCs.
"""
# Read relevant data
cfc_raw = pd.read_excel(cfc_country, header=6)
assets_arr[0] = np.asarray(cfc_raw['(4)'])[0] / 10**9
earnings_arr[0] = np.asarray(cfc_raw['(7)'])[0] / 10**9
foreigntax = np.asarray(cfc_raw['(8)'])[0] / 10**9
divUS = np.asarray(cfc_raw['(16)'])[0] / 10**9
subpartF_arr[0] = np.asarray(cfc_raw['(17)'])[0] / 10**9
endAccum = np.asarray(cfc_raw['(19)'])[0] / 10**9

# Compute certain terms
ftaxrt = foreigntax / earnings_arr[0]
startAccum_arr[0] = endAccum - earnings_arr[0] + divUS * (1 + ftaxrt) + subpartF_arr[0]
reprate = divUS / (earnings_arr[0] - subpartF_arr[0] - foreigntax)

# Save rates to use in CFC class
ftaxrt_arr = np.asarray([ftaxrt] * 14)
reprate_arr = np.asarray([reprate] * 14)



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
mofa_raw = pd.read_excel(mne_mofa, sheet_name='Table II.B 1', header=7)
assets_mofa = np.asarray(mofa_raw['(1)'])[0] / 1000.
ppe_mofa = np.asarray(mofa_raw['(5)'])[0] / 1000.
ppe_arr[0] = ppe_mofa * assets_arr[0] / assets_mofa



cfc_data = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                         'assets': assets_arr,
                         'ppe': ppe_arr,
                         'earnings': earnings_arr,
                         'taxrt': ftaxrt_arr,
                         'subpartF': subpartF_arr,
                         'accum': startAccum_arr,
                         'reprate_e': reprate_arr,
                         'reprate_a': np.zeros(14)})
cfc_data.to_csv(OUTPUT_PATH + 'cfc_data.csv')
