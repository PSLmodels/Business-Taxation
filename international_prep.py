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
# Income and sales of majority-owned foreign affiliates
inc_mofa = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'PartII-D1-D13.xls'))
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
SECTION 2. DATA ON MAJORITY-OWNED FOREIGN AFFILIATES for CFCs

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


"""
SECTION 3. DATA ON US MULTINATIONAL ENTERPRISES

The data come from BEA data on US parent companies of MNEs
and their majority-owned foreign affiliates. This includes
CFCs, foreign branches, and majority-owned foreign 
disregarded entities.

Note that the MOFA data used in section 2 is by industry
of affiliate, whereas all data in this section are by
industry of the parent company.

We use this to produce the domestic and foreign components
of the activities of US MNEs for use by the DomesticMNE
class and for computing FDII.
"""
# Prepare balance sheet data of MOFAs
mofab1 = pd.read_excel(bal_mofa, sheet_name='Table II.B 11', header=7)
mofab2 = mofab1.filter(['Unnamed: 0', '(1)', '(5)'])
mofab2.rename(columns={'Unnamed: 0': 'industry',
	                  '(1)': 'assets', '(5)': 'ppe'}, inplace=True)
mofab3 = mofab2.transpose()
mofab3.replace('(D)', 0., inplace=True)
mofab3['ALL'] = mofab3[0]
mofab3['FARM'] = mofab3[82]
mofab3['FFRA'] = mofab3[82]
mofab3['MINE'] = mofab3[2]
mofab3['UTIL'] = mofab3[84]
mofab3['CNST'] = mofab3[83]
mofab3['DMAN'] = (mofab3[11] + mofab3[24] + mofab3[25] + mofab3[29] +
	              mofab3[29] + mofab3[34] + mofab3[42] + mofab3[43] +
	              mofab3[46] + mofab3[47])
mofab3['NMAN'] = (mofab3[8] + mofab3[9] + mofab3[10] + mofab3[12] +
	              mofab3[13] + mofab3[14] + mofab3[16] + mofab3[23])
mofab3['WHTR'] = mofab3[49]
mofab3['RETR'] = mofab3[55]
mofab3['TRAN'] = mofab3[85]
mofab3['INFO'] = mofab3[60]
mofab3['FINC'] = mofab3[70]
mofab3['FINS'] = mofab3[71]
mofab3['INSU'] = mofab3[72]
mofab3['REAL'] = mofab3[86]
mofab3['LEAS'] = mofab3[86]
mofab3['PROF'] = mofab3[74]
mofab3['MGMT'] = mofab3[87]
mofab3['ADMN'] = mofab3[88]
mofab3['EDUC'] = mofab3[91]
mofab3['HLTH'] = mofab3[89]
mofab3['ARTS'] = mofab3[91]
mofab3['ACCM'] = mofab3[90]
mofab3['OTHS'] = mofab3[91]
mofab4 = mofab3.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                          'UTIL', 'CNST', 'DMAN', 'NMAN',
	                          'WHTR', 'RETR', 'TRAN', 'INFO',
	                          'FINC', 'FINS', 'INSU', 'REAL',
	                          'LEAS', 'PROF', 'MGMT', 'ADMN',
	                          'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
mofab4.drop(['industry'], axis=0, inplace=True)
mofab5 = mofab4.transpose() / 1000.

# Prepare balance sheet data of US parents
prntb1 = pd.read_excel(bal_parent, sheet_name='Table I.L 1', header=5)
prntb2 = prntb1.filter(['Unnamed: 0', '(1)', '(5)'])
prntb2.rename(columns={'Unnamed: 0': 'industry',
	                  '(1)': 'assets', '(5)': 'ppe'}, inplace=True)
prntb3 = prntb2.transpose()
prntb3.replace('(D)', 0., inplace=True)
prntb3['ALL'] = prntb3[0]
prntb3['FARM'] = prntb3[82]
prntb3['FFRA'] = prntb3[82]
prntb3['MINE'] = prntb3[2]
prntb3['UTIL'] = prntb3[84]
prntb3['CNST'] = prntb3[83]
prntb3['DMAN'] = (prntb3[11] + prntb3[24] + prntb3[25] + prntb3[29] +
	              prntb3[29] + prntb3[34] + prntb3[42] + prntb3[43] +
	              prntb3[46] + prntb3[47])
prntb3['NMAN'] = (prntb3[8] + prntb3[9] + prntb3[10] + prntb3[12] +
	              prntb3[13] + prntb3[14] + prntb3[16] + prntb3[23])
prntb3['WHTR'] = prntb3[49]
prntb3['RETR'] = prntb3[55]
prntb3['TRAN'] = prntb3[85]
prntb3['INFO'] = prntb3[60]
prntb3['FINC'] = prntb3[70]
prntb3['FINS'] = prntb3[71]
prntb3['INSU'] = prntb3[72]
prntb3['REAL'] = prntb3[86]
prntb3['LEAS'] = prntb3[86]
prntb3['PROF'] = prntb3[74]
prntb3['MGMT'] = prntb3[87]
prntb3['ADMN'] = prntb3[88]
prntb3['EDUC'] = prntb3[91]
prntb3['HLTH'] = prntb3[89]
prntb3['ARTS'] = prntb3[91]
prntb3['ACCM'] = prntb3[90]
prntb3['OTHS'] = prntb3[91]
prntb4 = prntb3.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                          'UTIL', 'CNST', 'DMAN', 'NMAN',
	                          'WHTR', 'RETR', 'TRAN', 'INFO',
	                          'FINC', 'FINS', 'INSU', 'REAL',
	                          'LEAS', 'PROF', 'MGMT', 'ADMN',
	                          'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
prntb4.drop(['industry'], axis=0, inplace=True)
prntb5 = prntb4.transpose() / 1000.

# Prepare income data of MOFAs
mofai1 = pd.read_excel(inc_mofa, sheet_name='Table II.D 11', header=6)
mofai2 = mofai1.filter(['Unnamed: 0', '(9)', '(11)'])
mofai2.rename(columns={'Unnamed: 0': 'industry',
	                  '(9)': 'foreigntax', '(11)': 'aftertaxinc'}, inplace=True)
mofai3 = mofai2.transpose()
mofai3.replace('(D)', 0., inplace=True)
mofai3['ALL'] = mofai3[0]
mofai3['FARM'] = mofai3[82]
mofai3['FFRA'] = mofai3[82]
mofai3['MINE'] = mofai3[2]
mofai3['UTIL'] = mofai3[84]
mofai3['CNST'] = mofai3[83]
mofai3['DMAN'] = (mofai3[11] + mofai3[24] + mofai3[25] + mofai3[29] +
	              mofai3[29] + mofai3[34] + mofai3[42] + mofai3[43] +
	              mofai3[46] + mofai3[47])
mofai3['NMAN'] = (mofai3[8] + mofai3[9] + mofai3[10] + mofai3[12] +
	              mofai3[13] + mofai3[14] + mofai3[16] + mofai3[23])
mofai3['WHTR'] = mofai3[49]
mofai3['RETR'] = mofai3[55]
mofai3['TRAN'] = mofai3[85]
mofai3['INFO'] = mofai3[60]
mofai3['FINC'] = mofai3[70]
mofai3['FINS'] = mofai3[71]
mofai3['INSU'] = mofai3[72]
mofai3['REAL'] = mofai3[86]
mofai3['LEAS'] = mofai3[86]
mofai3['PROF'] = mofai3[74]
mofai3['MGMT'] = mofai3[87]
mofai3['ADMN'] = mofai3[88]
mofai3['EDUC'] = mofai3[91]
mofai3['HLTH'] = mofai3[89]
mofai3['ARTS'] = mofai3[91]
mofai3['ACCM'] = mofai3[90]
mofai3['OTHS'] = mofai3[91]
mofai4 = mofai3.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                          'UTIL', 'CNST', 'DMAN', 'NMAN',
	                          'WHTR', 'RETR', 'TRAN', 'INFO',
	                          'FINC', 'FINS', 'INSU', 'REAL',
	                          'LEAS', 'PROF', 'MGMT', 'ADMN',
	                          'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
mofai4.drop(['industry'], axis=0, inplace=True)
mofai5 = mofai4.transpose() / 1000.
mofai5['netinc'] = mofai5['aftertaxinc'] + mofai5['foreigntax']
mofai5.drop(['aftertaxinc', 'foreigntax'], axis=1, inplace=True)

# Prepare income data of US parents
prnti1 = pd.read_excel(inc_parent, sheet_name='Table I.N 1', header=6)
prnti2 = prnti1.filter(['Unnamed: 0', '(8)', '(10)'])
prnti2.rename(columns={'Unnamed: 0': 'industry',
	                  '(8)': 'ustax', '(10)': 'aftertaxinc'}, inplace=True)
prnti3 = prnti2.transpose()
prnti3.replace('(D)', 0., inplace=True)
prnti3['ALL'] = prnti3[0]
prnti3['FARM'] = prnti3[82]
prnti3['FFRA'] = prnti3[82]
prnti3['MINE'] = prnti3[2]
prnti3['UTIL'] = prnti3[84]
prnti3['CNST'] = prnti3[83]
prnti3['DMAN'] = (prnti3[11] + prnti3[24] + prnti3[25] + prnti3[29] +
	              prnti3[29] + prnti3[34] + prnti3[42] + prnti3[43] +
	              prnti3[46] + prnti3[47])
prnti3['NMAN'] = (prnti3[8] + prnti3[9] + prnti3[10] + prnti3[12] +
	              prnti3[13] + prnti3[14] + prnti3[16] + prnti3[23])
prnti3['WHTR'] = prnti3[49]
prnti3['RETR'] = prnti3[55]
prnti3['TRAN'] = prnti3[85]
prnti3['INFO'] = prnti3[60]
prnti3['FINC'] = prnti3[70]
prnti3['FINS'] = prnti3[71]
prnti3['INSU'] = prnti3[72]
prnti3['REAL'] = prnti3[86]
prnti3['LEAS'] = prnti3[86]
prnti3['PROF'] = prnti3[74]
prnti3['MGMT'] = prnti3[87]
prnti3['ADMN'] = prnti3[88]
prnti3['EDUC'] = prnti3[91]
prnti3['HLTH'] = prnti3[89]
prnti3['ARTS'] = prnti3[91]
prnti3['ACCM'] = prnti3[90]
prnti3['OTHS'] = prnti3[91]
prnti4 = prnti3.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                          'UTIL', 'CNST', 'DMAN', 'NMAN',
	                          'WHTR', 'RETR', 'TRAN', 'INFO',
	                          'FINC', 'FINS', 'INSU', 'REAL',
	                          'LEAS', 'PROF', 'MGMT', 'ADMN',
	                          'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
prnti4.drop(['industry'], axis=0, inplace=True)
prnti5 = prnti4.transpose() / 1000.
prnti5['netinc'] = prnti5['aftertaxinc'] + prnti5['ustax']
prnti5.drop(['aftertaxinc', 'ustax'], axis=1, inplace=True)

# Prepare sales data of US parents
prnts1 = pd.read_excel(inc_parent, sheet_name='Table I.O 1', header=6)
prnts2 = prnts1.filter(['Unnamed: 0', '(1)', '(2)'])
prnts2.rename(columns={'Unnamed: 0': 'industry',
	                  '(1)': 'total', '(2)': 'us'}, inplace=True)
prnts3 = prnts2.transpose()
prnts3.replace('(D)', 0., inplace=True)
prnts3['ALL'] = prnts3[0]
prnts3['FARM'] = prnts3[82]
prnts3['FFRA'] = prnts3[82]
prnts3['MINE'] = prnts3[2]
prnts3['UTIL'] = prnts3[84]
prnts3['CNST'] = prnts3[83]
prnts3['DMAN'] = (prnts3[11] + prnts3[24] + prnts3[25] + prnts3[29] +
	              prnts3[29] + prnts3[34] + prnts3[42] + prnts3[43] +
	              prnts3[46] + prnts3[47])
prnts3['NMAN'] = (prnts3[8] + prnts3[9] + prnts3[10] + prnts3[12] +
	              prnts3[13] + prnts3[14] + prnts3[16] + prnts3[23])
prnts3['WHTR'] = prnts3[49]
prnts3['RETR'] = prnts3[55]
prnts3['TRAN'] = prnts3[85]
prnts3['INFO'] = prnts3[60]
prnts3['FINC'] = prnts3[70]
prnts3['FINS'] = prnts3[71]
prnts3['INSU'] = prnts3[72]
prnts3['REAL'] = prnts3[86]
prnts3['LEAS'] = prnts3[86]
prnts3['PROF'] = prnts3[74]
prnts3['MGMT'] = prnts3[87]
prnts3['ADMN'] = prnts3[88]
prnts3['EDUC'] = prnts3[82]
prnts3['HLTH'] = prnts3[89]
prnts3['ARTS'] = prnts3[82]
prnts3['ACCM'] = prnts3[90]
prnts3['OTHS'] = prnts3[91]
prnts4 = prnts3.filter(items=['ALL', 'FARM', 'FFRA', 'MINE',
	                          'UTIL', 'CNST', 'DMAN', 'NMAN',
	                          'WHTR', 'RETR', 'TRAN', 'INFO',
	                          'FINC', 'FINS', 'INSU', 'REAL',
	                          'LEAS', 'PROF', 'MGMT', 'ADMN',
	                          'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS'])
prnts4.drop(['industry'], axis=0, inplace=True)
prnts5 = prnts4.transpose() / 1000.
prnts5['foreign_share'] = (prnts5['total'] - prnts5['us']) / (prnts5['total'] + 0.000001)
prnts5.drop(['total', 'us'], axis=1, inplace=True)


# Combine all of these
mne1 = copy.deepcopy(prnts5)
mne1['assets_f'] = mofab5['assets']
mne1['assets_d'] = prntb5['assets']
mne1['ppe_f'] = mofab5['ppe']
mne1['ppe_d'] = prntb5['ppe']
mne1['netinc_f'] = mofai5['netinc']
mne1['netinc_d'] = prnti5['netinc']
mne1.to_csv('test.csv')

"""
SECTION 4. DATA ON US CORPORATIONS WITH FOREIGN INCOME

The data come from IRS data on corporations claiming a
foreign tax credit.

Note that the MOFA data used in section 2 is by industry
of affiliate, whereas all data in this section are by
industry of the parent company.
