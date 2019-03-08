"""
Test Debt class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_debt.py
# pylint --disable=locally-disabled test_debt.py

from copy import deepcopy
import pytest
# pylint: disable=import-error
from biztax import Asset, Debt


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
    asset = Asset(reforms[reform_number], corp=corporate)
    asset.calc_all()
    debt = Debt(reforms[reform_number], asset.get_forecast())
    debt.calc_all()
    decimals = 2
    interest_path = deepcopy(debt.interest_path).round(decimals)
    fname = 'debt_ref{}_{}_expect.csv'.format(reform_number,
                                              'corp' if corporate else 'nonc')
    actual_vs_expect(interest_path, fname, precision=decimals)
