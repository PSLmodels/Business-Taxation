"""
Test BusinessModel.update_btax_params method.
"""
import numpy
import pytest
from biztax import Policy, NUM_YEARS, START_YEAR


@pytest.mark.parametrize('param',
                         [('depr_25yr_bonus'),
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
def test_update(param):
    # check that default value of param is zero in every year
    default_policy = Policy()
    default_btax_params = default_policy.parameters_dataframe()
    zeros = numpy.zeros(NUM_YEARS)
    assert numpy.allclose(default_btax_params[param], zeros)
    # use Policy to implement a reform that makes param 0.5 in 2018+
    reform_dict_param_str = '_' + param
    btax_reform = {2018: {reform_dict_param_str: [0.5]}}
    reform_policy = Policy()
    reform_policy.implement_reform(btax_reform)
    reform_btax_params = reform_policy.parameters_dataframe()
    # check that values of reform_btax_params[param] are not all zero
    if numpy.allclose(reform_btax_params[param], zeros):
        assert 'update_btax_params' == 'FAILS for {}'.format(param)
