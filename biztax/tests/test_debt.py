"""
Test Debt class.
"""
import numpy as np
import pytest
from biztax import Debt, Asset, Data


@pytest.mark.parametrize('reform_number, corporate',
                         [(0, True),
                          (0, False),
                          (1, True),
                          (1, False),
                          (2, True),
                          (2, False)])
def test_debt_interest_path(reform_number, corporate,
                            reforms, actual_vs_expect):
    """
    Test corp/non-corp interest path results under different reforms.
    """
    asset = Asset(reforms[reform_number]['params_df'], corp=corporate)
    asset.calc_all()
    debt = Debt(reforms[reform_number]['params_df'], asset.get_forecast())
    debt.calc_all()
    decimals = 2
    interest_path = debt.interest_path.round(decimals)
    fname = 'debt_ref{}_{}_expect.csv'.format(reform_number,
                                              'corp' if corporate else 'nonc')
    actual_vs_expect(interest_path, fname, precision=decimals)


def test_instantiation(clp_params_df):
    """
    Test (in)correct Debt instantiation
    """
    good_btax_params = clp_params_df
    bad_btax_params = list()
    good_asset_forecast = np.ones(14)
    bad_asset_forecast = np.ones(13)
    good_data = Data()
    bad_data = list()
    good_response = np.zeros(14)
    bad_response = np.zeros(13)
    with pytest.raises(ValueError):
        Debt(bad_btax_params, good_asset_forecast)
    with pytest.raises(ValueError):
        Debt(good_btax_params, bad_asset_forecast)
    Debt(good_btax_params, good_asset_forecast, data=good_data)
    Debt(good_btax_params, good_asset_forecast, data=bad_data)
    with pytest.raises(ValueError):
        Debt(good_btax_params, good_asset_forecast, corp=list())
    Debt(good_btax_params, good_asset_forecast, corp=False)
    with pytest.raises(ValueError):
        Debt(good_btax_params, good_asset_forecast, eta=-0.2)
    Debt(good_btax_params, good_asset_forecast, response=good_response)
    with pytest.raises(ValueError):
        Debt(good_btax_params, good_asset_forecast, response=bad_response)


def test_constrain_history(clp_params_df):
    """
    Test constrain_history method
    """
    good_asset_forecast = np.ones(14)
    debt = Debt(clp_params_df, good_asset_forecast)
    debt.get_haircuts()
    debt.build_level_history()
    debt.build_flow_history()
    debt.originations[0] = -9.9  # triggers constrain_history logic
    debt.constrain_history()
    assert min(debt.originations) == 0.0
