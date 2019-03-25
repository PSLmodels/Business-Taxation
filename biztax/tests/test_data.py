"""
Test Data class.
"""
import numpy as np
import pytest
from biztax import Data


def test_update_rescaling():
    """
    Test update_rescaling method.
    """
    data = Data()
    # check default values set in Data ctor
    assert isinstance(data.rescale_corp, np.ndarray)
    assert isinstance(data.rescale_noncorp, np.ndarray)
    array_length = 14
    assert len(data.rescale_corp) == array_length
    assert len(data.rescale_noncorp) == array_length
    ones = np.ones(array_length)
    assert np.allclose(data.rescale_corp, ones)
    assert np.allclose(data.rescale_noncorp, ones)
    # update the data.rescale_* values
    sf_corp = 3.4
    sf_noncorp = 2.7
    data.update_rescaling(ones * sf_corp, ones * sf_noncorp)
    assert np.allclose(data.rescale_corp, ones * sf_corp)
    assert np.allclose(data.rescale_noncorp, ones * sf_noncorp)
