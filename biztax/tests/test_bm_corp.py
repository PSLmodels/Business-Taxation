"""
Test corporate-aspects of BusinessModel class.
"""
import os
import filecmp
import pytest
from biztax import BusinessModel, Response


@pytest.mark.requires_pufcsv
@pytest.mark.parametrize('with_response', [(False), (True)])
def test_bm_corp0(with_response, actual_vs_expect,
                  puf_subsample, tests_path):
    """
    Test BusinessModel corporate results under a corporate-income-tax reform
    using calc_all(response=None) and calc_all(response=zero_elasticities),
    checking that the two sets of results are the same.
    """
    # ensure that expected results in the two with_response cases are the same
    assert filecmp.cmp(os.path.join(tests_path,
                                    'bm_corp0_base_nresp_expect.csv'),
                       os.path.join(tests_path,
                                    'bm_corp0_base_wresp_expect.csv'),
                       shallow=False)
    assert filecmp.cmp(os.path.join(tests_path,
                                    'bm_corp0_refm_nresp_expect.csv'),
                       os.path.join(tests_path,
                                    'bm_corp0_refm_wresp_expect.csv'),
                       shallow=False)
    # specify corporate-income-tax reform dictionary with these provisions:
    # - apply a 28% corporate tax rate
    # - eliminate bonus depreciation
    # - establish 50% haircut on the deductibility of interest on new debt
    citax_refdict = {
        2018: {
            'tau_c': 0.28,
            'depr_3yr_bonus': 0.0,
            'depr_5yr_bonus': 0.0,
            'depr_7yr_bonus': 0.0,
            'depr_10yr_bonus': 0.0,
            'depr_15yr_bonus': 0.0,
            'depr_20yr_bonus': 0.0,
            'depr_25yr_bonus': 0.0,
            'depr_275yr_bonus': 0.0,
            'depr_39yr_bonus': 0.0,
            'pymtc_status': 1,
            'newIntPaid_corp_hc': 1.0,
            'newIntPaid_corp_hcyear': 2018,
            'oldIntPaid_corp_hc': 1.0,
            'oldIntPaid_corp_hcyear': 2018,
            'newIntPaid_noncorp_hc': 1.0,
            'newIntPaid_noncorp_hcyear': 2018,
            'oldIntPaid_noncorp_hc': 1.0,
            'oldIntPaid_noncorp_hcyear': 2018
        }
    }
    # specify individual-income-tax reform dictionary with no reform provisions
    iitax_refdict = {}
    # calculate results in different ways depending on value of with_response
    if with_response:
        zero_elast_response = Response()
        zero_elast_response.update_elasticities({})  # all zero elasticities
        bizmod = BusinessModel(citax_refdict, iitax_refdict,
                               investor_data=puf_subsample)
        bizmod.calc_all(response=zero_elast_response)
    else:
        bizmod = BusinessModel(citax_refdict, iitax_refdict,
                               investor_data=puf_subsample)
        bizmod.calc_all(response=None)
    # compare actual and expected results
    resp = 'wresp' if with_response else 'nresp'
    dec = 4
    results = bizmod.corp_base.taxreturn.combined_return.round(dec)
    fname = 'bm_corp0_base_{}_expect.csv'.format(resp)
    actual_vs_expect(results, fname, precision=dec)
    results = bizmod.corp_ref.taxreturn.combined_return.round(dec)
    fname = 'bm_corp0_refm_{}_expect.csv'.format(resp)
    actual_vs_expect(results, fname, precision=dec)


def test_incorrect_calc_all(puf_subsample):
    """
    Test incorrect call of calc_all method.
    """
    # Do quick simulation of executing response.calc_all(...) by setting
    # one calculated response to anything other than None
    pre_calc_response = Response()
    pre_calc_response.investment_response = 9.99
    # Try to use pre_calc_response as argument to BusinessModel.calc_all method
    bizmod = BusinessModel({}, {}, investor_data=puf_subsample)
    with pytest.raises(ValueError):
        bizmod.calc_all(response=pre_calc_response)
