"""
Test Asset class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_asset.py
# pylint --disable=locally-disabled test_asset.py

from copy import deepcopy
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
    capital_path = deepcopy(asset.capital_path).round(decimals)
    fname = 'asset_ref{}_{}_expect.csv'.format(reform_number,
                                               'corp' if corporate else 'nonc')
    actual_vs_expect(capital_path, fname, precision=decimals)
