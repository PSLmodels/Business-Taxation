# This file reads in all of the datasets and saves them accordingly.
ctax_data_path = 'aggregates_data/'
# import tax revenue data
taxrev_data = pd.read_csv(ctax_data_path + 'taxrev.csv')
# import data for AMT model
amtdata2 = pd.read_csv(ctax_data_path + 'amt data2.csv')
# import data for FTC model
ftc_taxrates_data = pd.read_csv(ctax_data_path + 'ftc taxrates data.csv')
ftc_gdp_data = pd.read_csv(ctax_data_path + 'ftc gdp data.csv')
ftc_other_data = pd.read_csv(ctax_data_path + 'ftc other data.csv')
# import data for Sec. 199
sec199_data = pd.read_csv(ctax_data_path + 'sec199.csv')
# import depreciation data
econdepr_path = 'btax_mini/data/depreciation_rates/\
Economic Depreciation Rates.csv'
df_econdepr = pd.read_csv(econdepr_path)
df_econdepr['Asset'][78] = 'Communications equipment manufacturing'
df_econdepr['Asset'][81] = 'Motor vehicles and parts manufacturing'
df_econdepr.drop('Code', axis=1, inplace=True)
df_econdepr.rename(columns={'Economic Depreciation Rate': 'delta'},
                   inplace=True)
# import other data
investmentrate_data = pd.read_csv(ctax_data_path + 'investmentrates.csv')
investmentshare_data = pd.read_csv(ctax_data_path + 'investmentshares.csv')
investmentGfactors_data = pd.read_csv(ctax_data_path +
                                      'investment_gfactors.csv')
depreciationIRS_data = pd.read_csv(ctax_data_path + 'dep data.csv')
bonus_data = pd.read_csv(ctax_data_path + 'bonus_data.csv')
# import debt data
debt_data_corp = pd.read_csv(ctax_data_path + 'Corp debt data.csv')
debt_data_noncorp = pd.read_csv(ctax_data_path + 'Noncorp debt data.csv')
