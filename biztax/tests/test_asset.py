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


def test_asset_capital_path(actual_vs_expect):
    """
    Test corp/non-corp capital_path results under different reforms.
    """
    reform = Data().btax_defaults
    asset = Asset(reform, corp=True)
    asset.calc_all()
    capital_path = copy.deepcopy(asset.capital_path).round(2)
    actual_vs_expect(capital_path, 'asset_ref0_corp_expect.csv', precision=2)
