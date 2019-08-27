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
from biztax.data import Data
from biztax.policy import Policy
from biztax.asset import Asset
from biztax.debt import Debt

industrylist = ['ALL', 'FARM', 'FFRA', 'MINE', 'UTIL', 'CNST',
                'DMAN', 'NMAN', 'WHTR', 'RETR', 'TRAN', 'INFO',
                'FINC', 'FINS', 'INSU', 'REAL', 'LEAS', 'PROF',
                'MGMT', 'ADMN', 'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS']

industry_columns = {'ALL': [1],
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

RAW_DATA_PATH1 = 'data_prep/historical_corp/'
RAW_DATA_PATH2 = 'data_prep/historical_debt/'
OUTPUT_PATH = 'biztax/brc_data/'
"""
SECTION 1. READ TAX DATA
"""
# Taxable interest income
taxint = np.zeros(14)
# Nontaxable interest income
ntaxint = np.zeros(14)
# Interest paid
intpaid = np.zeros(14)
for year in range(2000, 2014):
    data1 = pd.read_csv(RAW_DATA_PATH1 + 'corp' + str(year) + '.csv', index_col=0)
    #taxint[year-2000] = (data1.loc['Interest income', 'ALL'] -
    #                     data1.loc['Interest income', 'FINC'] -
    #                     data1.loc['Interest income', 'FINS'] -
    #                     data1.loc['Interest income', 'INSU'] -
    #                     data1.loc['Interest income', 'MGMT'])
    #ntaxint[year-2000] = (data1.loc['Nontaxable interest income', 'ALL'] -
    #                      data1.loc['Nontaxable interest income', 'FINC'] -
    #                      data1.loc['Nontaxable interest income', 'FINS'] -
    #                      data1.loc['Nontaxable interest income', 'INSU'] -
    #                      data1.loc['Nontaxable interest income', 'MGMT'])
    #intpaid[year-2000] = (data1.loc['Interest paid', 'ALL'] -
    #                      data1.loc['Interest paid', 'FINC'] -
    #                      data1.loc['Interest paid', 'FINS'] -
    #                      data1.loc['Interest paid', 'INSU'] -
    #                      data1.loc['Interest paid', 'MGMT'])
    taxint[year-2000] = data1.loc['Interest income', 'ALL']
    ntaxint[year-2000] = data1.loc['Nontaxable interest income', 'ALL']
    intpaid[year-2000] = data1.loc['Interest paid', 'ALL']




"""
SECTION 2. READ FA DEBT DATA AND RATES
"""
# Read debt data
debtdata = pd.read_csv(RAW_DATA_PATH2 + 'FRB_Z1.csv', header=5)
# Compute nonfinancial noncorporate debt liabilities
debtdata['L_nc'] = (debtdata['FL144104005.A'] - debtdata['FL104104005.A']) / 1000.
debtdata['L_c'] = debtdata['FL104104005.A'] / 1000.
# Compute nonfinancial corporate debt assets
debtdata['At_c'] = (debtdata['FL104022005.A'] + debtdata['FL104023005.A'] +
                    debtdata['FL102051003.A'] + debtdata['FL103030003.A'] +
                    debtdata['FL103034000.A']) / 1000.
debtdata['An_c'] = debtdata['FL103062003.A'] / 1000.
debtdata.drop(['FL144104005.A', 'FL104104005.A', 'FL104022005.A', 
               'FL104023005.A', 'FL103062003.A', 'FL102051003.A',
               'FL103030003.A', 'FL103034000.A'], axis=1, inplace=True)
debtdata.rename(columns={'Time Period': 'year'}, inplace=True)
debtdata.set_index('year', inplace=True)
# Drop unnecessary years
debtdata.drop([2015, 2016, 2017, 2018], axis=0, inplace=True)
# Read interest rate and premium data
ratedata = pd.read_csv(RAW_DATA_PATH2 + 'fredgraph.csv')
ratedata['DATE'] = range(1955, 2020)
ratedata.rename(columns={'DATE': 'year'}, inplace=True)
ratedata.set_index('year', inplace=True)
# Drop unnecessary years
ratedata.drop([1955, 1956, 1957, 1958, 1958, 1959,
               2015, 2016, 2017, 2018, 2019], axis=0, inplace=True)
# Extend 1962 rates to 1960
ratedata.loc[1960:1962, 'T10YFF'] = ratedata.loc[1962, 'T10YFF']
ratedata.loc[1960:1962, 'DGS10'] = ratedata.loc[1962, 'DGS10']
#ratedata.loc[1961] = ratedata.iloc[1962]
# Compute corporate bond premium over 10-year T-bond rate
ratedata['i_pr'] = (np.asarray(ratedata['BAAFFM'], dtype=float) -
                    np.asarray(ratedata['T10YFF'], dtype=float)) / 100.
ratedata['i_t'] = np.asarray(ratedata['DGS10'], dtype=float) / 100.
ratedata.drop(['BAAFFM', 'T10YFF', 'DGS10'], axis=1, inplace=True)
# Merge datasets together and save
debt2 = debtdata.merge(right=ratedata, how='inner', on='year')
debt2.to_csv(OUTPUT_PATH + 'debt_history.csv')



"""
SECTION 3. COMPUTE ADJUSTMENT FACTORS AND RESCALE
Runs the Debt model, computes taxable interest income,
municipal interest income, and interest paid.
Compares these with the IRS numbers to get adjustment
factors. Rescales the debt history to match IRS on average.
"""
def calcIDAdjustment(corp, eta=0.4):
    """
    Calculates the adjustment factors for the corporate and noncorporate
    debt and interest.
    eta: retirement rate of existing debt
    """
    data = Data()
    policy = Policy()
    policy_params_df = policy.parameters_dataframe()
    # Create Asset object
    asset = Asset(policy_params_df, corp)
    asset.calc_all()
    # Get asset forecast
    forecast = asset.get_forecast()
    # Create Debt object
    debt = Debt(policy_params_df, forecast, corp=corp)
    debt.calc_all()
    # Get unscaled interest incomes and expenses
    intpaid_model = debt.int_expense[40:54]
    intinc_model = debt.int_income[40:54]
    muniinc_model = debt.muni_income[40:54]
    if corp:
        # Exclude anomalous results for 2007
        paid_scale = (sum(intpaid[:7] / intpaid_model[:7]) +
                      sum(intpaid[8:] / intpaid_model[8:])) / 13.
        inc_scale = (sum(taxint[:7] / intinc_model[:7]) +
                     sum(taxint[8:] / intinc_model[8:])) / 13.
        muni_scale = (sum(ntaxint[:7] / muniinc_model[:7]) +
                      sum(ntaxint[8:] / muniinc_model[8:]))/ 13.
        scales = [paid_scale, inc_scale, muni_scale]
    else:
        ID_irs = np.array(data.debt_data_noncorp['ID_Scorp'][40:54] +
                          data.debt_data_noncorp['ID_sp'][40:54] +
                          data.debt_data_noncorp['ID_partner'][40:54])
        scales = sum(ID_irs / intpaid_model) / 14.
    assets14 = forecast[0]
    return (scales, assets14, intpaid_model, intinc_model, muniinc_model)

(scales_corp, ast_c_14, intpaid_model, intinc_model, muniinc_model) = calcIDAdjustment(True)
(scale_ncorp, ast_nc_14, _, _, _) = calcIDAdjustment(False)
print(scales_corp)
print(scale_ncorp)

newdebt = copy.deepcopy(debt2)
newdebt['L_c'] = debt2['L_c'] * scales_corp[0]
newdebt['L_nc'] = debt2['L_nc'] * scale_ncorp
newdebt['At_c'] = debt2['At_c'] * scales_corp[1]
newdebt['An_c'] = debt2['An_c'] * scales_corp[2]
newdebt.to_csv(OUTPUT_PATH + 'debt_history.csv')


pol1 = Policy()
# Create Asset object
asset = Asset(pol1.parameters_dataframe(), True)
asset.calc_all()
# Create Debt object
debt = Debt(pol1.parameters_dataframe(), asset.get_forecast(), corp=True)
debt.calc_all()

df1 = pd.DataFrame({'inc_mod': intinc_model * scales_corp[1],
                    'paid_mod': intpaid_model * scales_corp[0],
                    'muni_mod': muniinc_model * scales_corp[2],
                    'inc_irs': taxint, 'paid_irs': intpaid, 'muni_irs': ntaxint})
df1.to_csv('debt_fit.csv')

