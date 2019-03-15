"""
Test Asset class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_asset.py
# pylint --disable=locally-disabled test_asset.py

import pandas as pd
import pytest
# pylint: disable=import-error
from biztax import Asset, Response


@pytest.mark.parametrize('reform_number, corporate',
                         [(0, True),
                          (0, False),
                          (1, True),
                          (1, False),
                          (2, True),
                          (2, False)])
def test_asset_capital_path(reform_number, corporate,
                            reforms, actual_vs_expect):
    """
    Test corp/non-corp capital path results under different reforms.
    """
    asset = Asset(reforms[reform_number], corp=corporate)
    asset.calc_all()
    decimals = 2
    capital_path = asset.capital_path.round(decimals)
    fname = 'asset_ref{}_{}_expect.csv'.format(reform_number,
                                               'corp' if corporate else 'nonc')
    actual_vs_expect(capital_path, fname, precision=decimals)


def test_incorrect_instantiation():
    """
    Test incorrect Asset instantiation
    """
    with pytest.raises(ValueError):
        Asset(list())
    with pytest.raises(ValueError):
        Asset(pd.DataFrame(), corp=list())


def test_update_response(default_btax_params):
    """
    Test update_response method
    """
    asset = Asset(default_btax_params)
    assert asset.response is None
    response_df = pd.DataFrame()
    asset.update_response(response_df)
    assert isinstance(asset.response, pd.DataFrame)

@pytest.mark.skip
def test_build_inv_matrix(default_btax_params):
    """
    Test build_inv_matrix method with response
    """
    resp_elasticities = {'inv_usercost_c': -1.0, 'inv_usercost_nc': -0.5}
    resp = Response(resp_elasticities, default_btax_params, default_bax_params)
    resp.calc_inv_response()
    asset = Asset(default_btax_params, response=resp.investment_response)
    asset.get_ccr_data()
    asset.build_inv_matrix()
    assert isinstance(asset.investment_history, pd.DataFrame)

@pytest.mark.skip
def test_calc_depreciation_allyears(puf_subsample, default_btax_params):
    """
    Test calcDep_allyears method
    """
    bizmod = BusinessModel({}, {}, investor_data=puf_subsample)
    bizmod.update_mtrlists()
    response_elasticities = {
        'inv_usercost_c': -1.0,
        'inv_usercost_nc': -0.5,
        'inv_eatr_c': 0.0,
        'inv_eatr_nc': 0.0,
        'debt_taxshield_c': 0.4,
        'debt_taxshield_nc': 0.2,
        'mne_share_c': 0.0,
        'mne_share_nc': 0.0,
        'first_year_response': 2018
    }
    bizmod.response = Response(response_elasticities, {}, {})
    bizmod.response.calc_all()
    asset = Asset(default_btax_params,
                  response=bizmod.response.investment_response)
    asset.calcDep_allyears()

@pytest.mark.skip
def test_calc_depreciation_budget(default_btax_params):
    """
    Test calcDep_budget method
    """
    asset = Asset(default_btax_params)
    asset.get_ccr_data()
    asset.build_inv_matrix()
    asset.build_deprLaw_matrices()
    asset.calcDep_allyears()
