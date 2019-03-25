"""
Test Response class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_response.py
# pylint --disable=locally-disabled test_response.py

import numpy as np
import pytest
# pylint: disable=import-error
from biztax import Response


def test_calc_all_already_called():
    """
    Test calc_all_already_called method
    """
    response = Response()
    assert not response.calc_all_already_called()


def test_update_elasticities():
    """
    Test (in)correct use of update_elasticities method
    """
    response = Response()
    with pytest.raises(ValueError):
        response.update_elasticities({'unknown_elasticity_name': 0.0})
    response.update_elasticities({'inv_eatr_c': -0.8})
