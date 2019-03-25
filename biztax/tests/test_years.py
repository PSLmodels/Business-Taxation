"""
Test named numerical constants in the years.py file.
"""
import taxcalc as itax
from biztax import START_YEAR, END_YEAR


def test_years():
    """
    Test that years-related constants are compatible with itax.Policy years
    """
    assert START_YEAR <= END_YEAR
    assert START_YEAR >= itax.Policy.JSON_START_YEAR
    assert END_YEAR <= itax.Policy.LAST_BUDGET_YEAR
