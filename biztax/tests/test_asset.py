"""
Test Asset class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_asset.py
# pylint --disable=locally-disabled test_asset.py

import pandas as pd
import pytest
# pylint: disable=import-error
from biztax import Asset


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


@pytest.mark.parametrize('has_response', [(False), (True)])
def test_build_inv_matrix(has_response, default_btax_params):
    """
    Test build_inv_matrix method
    """
    if has_response:
        resp = None  # TODO: what to put here?
    else:
        resp = None
    asset = Asset(default_btax_params, response=resp)
    asset.get_ccr_data()
    asset.build_inv_matrix()
    if has_response:
        # TODO: assert isinstance(asset.response, pd.DataFrame)
        assert asset.response is None
    else:
        assert asset.response is None

@pytest.mark.xfail
def test_calc_depreciation_allyears(default_btax_params):
    """
    Test calcDep_allyears method
    """
    asset = Asset(default_btax_params)
    asset.get_ccr_data()
    asset.build_inv_matrix()
    asset.build_deprLaw_matrices()
    asset.calcDep_allyears()

@pytest.mark.xfail
def test_calc_depreciation_budget(default_btax_params):
    """
    Test calcDep_budget method
    """
    asset = Asset(default_btax_params)
    asset.get_ccr_data()
    asset.build_inv_matrix()
    asset.build_deprLaw_matrices()
    asset.calcDep_allyears()
