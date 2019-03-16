"""
Test corpoate-aspects of BusinessModel class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_bm_corp.py
# pylint --disable=locally-disabled test_bm_corp.py

import os
import filecmp
import pytest
# pylint: disable=import-error
from biztax import BusinessModel, Response


@pytest.mark.parametrize('with_response', [(False), (True)])
def test_bm_corp0(with_response, actual_vs_expect,
                  puf_fullsample, tests_path):
    """
    Test BusinessModel corporate results under a corporate-income-tax reform
    using calc_norespone() and calc_withresponse() with zero elasticities,
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
        response = Response()
        response.update_elasticities({})  # all elasticities are zero
        bizmod = BusinessModel(citax_refdict, iitax_refdict,
                               investor_data=puf_fullsample)
        bizmod.calc_withresponse(response)
    else:
        bizmod = BusinessModel(citax_refdict, iitax_refdict,
                               investor_data=puf_fullsample)
        bizmod.calc_noresponse()
    # compare actual and expected results
    resp = 'wresp' if with_response else 'nresp'
    dec = 4
    results = bizmod.corp_base.taxreturn.combined_return.round(dec)
    fname = 'bm_corp0_base_{}_expect.csv'.format(resp)
    actual_vs_expect(results, fname, precision=dec)
    results = bizmod.corp_ref.taxreturn.combined_return.round(dec)
    fname = 'bm_corp0_refm_{}_expect.csv'.format(resp)
    actual_vs_expect(results, fname, precision=dec)
