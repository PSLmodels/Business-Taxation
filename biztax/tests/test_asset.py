"""
Test Asset class.
"""
import pandas as pd
import pytest
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
    asset = Asset(reforms[reform_number]['params_df'], corp=corporate)
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
    with pytest.raises(ValueError):
        Asset(pd.DataFrame(), response=list())


def test_update_response(clp_params_df):
    """
    Test update_response method
    """
    asset = Asset(clp_params_df)
    assert asset.response is None
    response_df = pd.DataFrame()
    asset.update_response(response_df)
    assert isinstance(asset.response, pd.DataFrame)
