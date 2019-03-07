"""
Tests Asset class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_asset.py
# pylint --disable=locally-disabled test_asset.py

import copy
import pandas as pd
import pytest
from biztax import Data, Asset


@pytest.mark.parametrize('reform_num, corporate',
                         [(0, True),
                          (0, False),
                          (1, True),
                          (1, False),
                          (2, True),
                          (2, False)])
def test_asset_capital_path(reform_num, corporate,
                            reform, actual_vs_expect):
    """
    Test corp/non-corp capital_path results under different reforms.
    """
    asset = Asset(reform[reform_num], corp=corporate)
    asset.calc_all()
    decimals = 2
    capital_path = copy.deepcopy(asset.capital_path).round(decimals)
    fname = 'asset_ref{}_{}_expect.csv'.format(reform_num,
                                               'corp' if corporate else 'nonc')
    actual_vs_expect(capital_path, fname, precision=decimals)
