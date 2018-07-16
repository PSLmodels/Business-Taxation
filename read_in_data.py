# This file reads in all of the datasets and saves them accordingly.
ctax_data_path = 'brc_data/'
btax_data_path = 'btax_data/'
gfactors = pd.read_csv('gfactors.csv')
historical_taxdata = pd.read_csv('historical_taxdata.csv')
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
# import pass-through IRS data
partner_data = pd.read_csv(ctax_data_path + 'partnership data.csv')
Scorp_data = pd.read_csv(ctax_data_path + 'Scorp data.csv')
sp_data = pd.read_csv(ctax_data_path + 'sp_nonfarm data.csv')

btax_defaults = pd.read_csv('mini_params_btax.csv')
econ_defaults = pd.read_csv('mini_params_econ.csv')

# Rescaling factors for later
rescale_corp = np.ones(14)
rescale_noncorp = np.ones(14)
if track_progress:
    print("Data imports complete")
