import os
import numpy as np
import pandas as pd
from taxcalc import read_egg_csv
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
ctax_data_dir = 'brc_data'
btax_data_dir = 'btax_data'


def read_csv(filename):
    """
    Returns Pandas DataFrame object containing data in specified filename,
    which is an absolute path to the CSV file without the CURRENT_PATH.
    """
    assert filename.endswith('.csv')
    fname = os.path.join(CURRENT_PATH, filename)
    if os.path.exists(fname):
        dframe = pd.read_csv(fname)
    else:  # find file in conda package
        dframe = read_egg_csv(filename)  # pragma: no cover
    return dframe


class Data():
    """
    Constructor for the Data object.
    The purpose of this object is to read and contain all of the necessary
    datasets to run the analyses in BRC. This also provides a central
    mechanism for updating and improving the underlying data. One of the
    important features of the Data object is that it should not be changed
    by any other objects in BRC.
    """

    def __init__(self):
        self.gfactors = read_csv('gfactors.csv')
        self.historical_taxdata = read_csv('historical_taxdata.csv')
        self.historical_combined = read_csv(
            os.path.join(ctax_data_dir, 'historical_combined.csv'))
        # Tax revenue data
        self.taxrev_data = read_csv(
            os.path.join(ctax_data_dir, 'taxrev.csv'))
        # Data for FTC model
        self.ftc_taxrates_data = read_csv(
            os.path.join(ctax_data_dir, 'ftc_taxrates_data.csv'))
        self.ftc_gdp_data = read_csv(
            os.path.join(ctax_data_dir, 'ftc_gdp_data.csv'))
        self.ftc_other_data = read_csv(
            os.path.join(ctax_data_dir, 'ftc_other_data.csv'))
        # Data for Sec. 199
        self.sec199_data = read_csv(
            os.path.join(ctax_data_dir, 'sec199.csv'))
        # Investment data
        self.investmentrate_data = read_csv(
            os.path.join(ctax_data_dir, 'investment_rates.csv'))
        self.investmentshare_data = read_csv(
            os.path.join(ctax_data_dir, 'investment_shares.csv'))
        self.investmentGfactors_data = read_csv(
            os.path.join(ctax_data_dir, 'investment_gfactors.csv'))
        # Tax depreciation information
        self.depreciationIRS_data = read_csv(
            os.path.join(ctax_data_dir, 'dep_data.csv'))
        self.bonus_data = read_csv(
            os.path.join(ctax_data_dir, 'bonus_data.csv'))
        # Debt data
        self.debt_data_corp = read_csv(
            os.path.join(ctax_data_dir, 'corp_debt_data.csv'))
        self.debt_data_noncorp = read_csv(
            os.path.join(ctax_data_dir, 'noncorp_debt_data.csv'))
        # Pass-through IRS data
        self.partner_data = read_csv(
            os.path.join(ctax_data_dir, 'partnership_data.csv'))
        self.Scorp_data = read_csv(
            os.path.join(ctax_data_dir, 'scorp_data.csv'))
        self.sp_data = read_csv(
            os.path.join(ctax_data_dir, 'sp_nonfarm_data.csv'))
        # Defaults for posssible use (may be deprecated)
        self.btax_defaults = read_csv(
            os.path.join(CURRENT_PATH, 'mini_params_btax.csv'))
        self.econ_defaults = read_csv(
            os.path.join(CURRENT_PATH, 'mini_params_econ.csv'))
        self.rescale_corp = np.ones(14)
        self.rescale_noncorp = np.ones(14)
        # Read in adjustment factors
        adj_factors = read_csv('adjfactors.csv')
        self.param_amt = adj_factors['param_amt'].values[0]
        self.amt_frac = adj_factors['amt_frac'].values[0]
        self.totaluserate_pymtc = adj_factors['totaluserate_pymtc'].values[0]
        self.userate_pymtc = adj_factors['userate_pymtc'].values[0]
        self.trans_amt1 = adj_factors['trans_amt1'].values[0]
        self.trans_amt2 = adj_factors['trans_amt2'].values[0]
        self.stock2014 = adj_factors['stock2014'].values[0]
        self.adjfactor_ftc_corp = adj_factors['ftc'].values[0]
        self.adjfactor_dep_corp = adj_factors['dep_corp'].values[0]
        self.adjfactor_dep_noncorp = adj_factors['dep_noncorp'].values[0]
        self.adjfactor_int_corp = adj_factors['int_corp'].values[0]
        self.adjfactor_int_noncorp = adj_factors['int_noncorp'].values[0]
        # Read in pass-through shares
        passthru_factors = read_csv('passthru_shares.csv')
        self.depshare_scorp_posinc = passthru_factors['dep_scorp_pos'].values[0]
        self.depshare_scorp_neginc = passthru_factors['dep_scorp_neg'].values[0]
        self.depshare_sp_posinc = passthru_factors['dep_sp_pos'].values[0]
        self.depshare_sp_neginc = passthru_factors['dep_sp_neg'].values[0]
        self.depshare_partner_posinc = passthru_factors['dep_part_pos'].values[0]
        self.depshare_partner_neginc = passthru_factors['dep_part_neg'].values[0]
        self.intshare_scorp_posinc = passthru_factors['int_scorp_pos'].values[0]
        self.intshare_scorp_neginc = passthru_factors['int_scorp_neg'].values[0]
        self.intshare_sp_posinc = passthru_factors['int_sp_pos'].values[0]
        self.intshare_sp_neginc = passthru_factors['int_sp_neg'].values[0]
        self.intshare_partner_posinc = passthru_factors['int_part_pos'].values[0]
        self.intshare_partner_neginc = passthru_factors['int_part_neg'].values[0]

    def assets_data(self):
        """
        Retrieves the DataFrame with asset dames and amounts
        """
        asset_data = read_csv('mini_assets.csv')
        asset_data.drop([3, 21, 32, 91], axis=0, inplace=True)
        asset_data.reset_index(drop=True, inplace=True)
        return asset_data

    def econ_depr_df(self):
        """
        Retrieves the DataFrame with economic depreciation rates
        """
        df_econdepr = read_csv(
            os.path.join(btax_data_dir, 'economic_depreciation_rates.csv'))
        asset = np.asarray(df_econdepr['Asset'])
        asset[78] = 'Communications equipment manufacturing'
        asset[81] = 'Motor vehicles and parts manufacturing'
        df_econdepr['Asset'] = asset
        df_econdepr.drop('Code', axis=1, inplace=True)
        df_econdepr.rename(columns={'Economic Depreciation Rate': 'delta'},
                           inplace=True)
        df_econdepr.drop([56, 89, 90], axis=0, inplace=True)
        df_econdepr.reset_index(drop=True, inplace=True)
        return df_econdepr

    def taxdep_info_gross(self):
        """
        Retrieves the basic DataFrame with tax depreciation information
        """
        taxdep1 = read_csv(
            os.path.join(btax_data_dir, 'tax_depreciation_rates.csv'))
        taxdep1.drop(['System'], axis=1, inplace=True)
        taxdep1.rename(columns={'GDS Life': 'L_gds', 'ADS Life': 'L_ads',
                                'Asset Type': 'Asset'}, inplace=True)
        asset = np.asarray(taxdep1['Asset'])
        asset[81] = 'Motor vehicles and parts manufacturing'
        method = np.asarray(taxdep1['Method'])
        method[asset == 'Land'] = 'None'
        method[asset == 'Inventories'] = 'None'
        taxdep1['Asset'] = asset
        taxdep1['Method'] = method
        taxdep1.drop([56, 89, 90], axis=0, inplace=True)
        taxdep1.reset_index(drop=True, inplace=True)
        return taxdep1.merge(right=self.econ_depr_df(), how='outer', on='Asset')

    def update_rescaling(self, corparray, ncorparray):
        """
        Updates the rescaling factors associated with the Data class object
        """
        assert len(corparray) == 14
        assert len(ncorparray) == 14
        self.rescale_corp = corparray
        self.rescale_noncorp = ncorparray
