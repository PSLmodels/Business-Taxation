"""
Test BtaxMini class.
"""
import pandas as pd
import pytest
from biztax import BtaxMini


def test_run_btax_mini(default_btax_params):
    """
    Test run_btax_mini method
    """
    btaxmini = BtaxMini(default_btax_params)
    assert isinstance(btaxmini, BtaxMini)
    year_list = [2017]
    res = btaxmini.run_btax_mini(year_list)
    assert isinstance(res, pd.DataFrame)
