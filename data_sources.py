from functools import lru_cache
import pandas as pd
import numpy as np

btax_data_path = 'btax_data/'


@lru_cache(maxsize=None)
def assets_data():
    asset_data = pd.read_csv('mini_assets.csv')
    asset_data.drop([3, 21, 32, 91], axis=0, inplace=True)
    asset_data.reset_index(drop=True, inplace=True)
    return asset_data


@lru_cache(maxsize=None)
def econ_depr_df():
    """Import depreciation data"""
    df_econdepr = pd.read_csv(btax_data_path +
                              'Economic Depreciation Rates.csv')
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


@lru_cache(maxsize=None)
def taxdep_info_gross():
    """Tax depreciation information"""
    taxdep1 = pd.read_csv(btax_data_path + 'tax_depreciation_rates.csv')
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
    return taxdep1.merge(right=econ_depr_df(), how='outer', on='Asset')
