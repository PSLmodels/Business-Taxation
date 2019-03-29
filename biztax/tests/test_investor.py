"""
Test Investor class.
"""
import pytest
import taxcalc as itax
from biztax import Investor, Policy


def test_incorrect_instantiation():
    """
    Test incorrect Investor instantiation
    """
    with pytest.raises(ValueError):
        Investor(Policy())
    with pytest.raises(ValueError):
        Investor(itax.Policy(), list())
