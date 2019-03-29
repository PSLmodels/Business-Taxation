"""
Test BtaxMini class.
"""
import pandas as pd
import pytest
from biztax import BtaxMini


def test_run_btax_mini(clp_params_df):
    """
    Test run_btax_mini method
    """
    btaxmini = BtaxMini(clp_params_df)
    assert isinstance(btaxmini, BtaxMini)
    year_list = [2017]
    res = btaxmini.run_btax_mini(year_list)
    assert isinstance(res, pd.DataFrame)
