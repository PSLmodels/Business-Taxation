"""
Test BtaxMini class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_btaxmini.py
# pylint --disable=locally-disabled test_btaxmini.py

import pandas as pd
import pytest
# pylint: disable=import-error
from biztax import BtaxMini

@pytest.mark.one
def test_run_btax_mini(default_btax_params):
    """
    Test run_btax_mini method
    """
    btaxmini = BtaxMini(default_btax_params)
    assert isinstance(btaxmini, BtaxMini)
    year_list = [2017]
    res = btaxmini.run_btax_mini(year_list)
    assert isinstance(res, pd.DataFrame)
