"""
Test BusinessModel.update_btax_params method.
"""
import numpy
import pytest
from biztax import BusinessModel, NUM_YEARS, START_YEAR

@pytest.mark.one
@pytest.mark.parametrize('param',
                         [('depr_3yr_bonus'),
                          ('depr_5yr_bonus'),
                          ('depr_7yr_bonus'),
                          ('depr_10yr_bonus'),
                          ('depr_15yr_bonus'),
                          ('depr_20yr_bonus'),
                          ('depr_25yr_bonus'),
                          ('depr_275yr_bonus'),
                          ('depr_39yr_bonus'),
                          ('depr_land_bonus'),
                          ('undepBasis_corp_hc'),
                          ('undepBasis_noncorp_hc'),
                          ('ftc_hc'),
                          ('sec199_hc'),
                          ('oldIntPaid_corp_hc'),
                          ('newIntPaid_corp_hc'),
                          ('netIntPaid_corp_hc'),
                          ('oldIntPaid_noncorp_hc'),
                          ('newIntPaid_noncorp_hc')])
def test_update(param, default_btax_params):
    # check that default value of param is zero in every year
    zeros = numpy.zeros(NUM_YEARS)
    assert numpy.allclose(default_btax_params[param], zeros)
    # use BusinessModel to implement a reform that makes param 0.5 in 2018+
    btax_reform = {2018: {param: 0.5}}
    bizmod = BusinessModel(btax_reform, {}, investor_data='nodata')
    reform_btax_params = bizmod.btax_params_ref
    # check that values of reform_btax_params[param] are not all zero
    if numpy.allclose(reform_btax_params[param], zeros):
        assert 'update_btax_params' == 'FAILS for {}'.format(param)
