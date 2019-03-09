"""
Test corpoate-aspects of BusinessModel class.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_bm_corp.py
# pylint --disable=locally-disabled test_bm_corp.py

import pytest
# pylint: disable=import-error
from biztax import BusinessModel


@pytest.mark.parametrize('with_responses', [
    (False),
    # (True) possibly add test with responses
])
def test_bm_corp(with_responses, actual_vs_expect, puf_fullsample):
    """
    Test BusinessModel corporate results under a corporate-income-tax reform
    with and without responses.
    """
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
    bizmod = BusinessModel(citax_refdict, iitax_refdict,
                           investor_data=puf_fullsample)
    # calculate results depending on value of with_responses
    if with_responses:
        # specify investment and debt responses
        elasticities = {
            'inv_usercost_c': -1.0,
            'inv_usercost_nc': -0.5,
            'debt_taxshield_c': 0.4,
            'debt_taxshield_nc': 0.2,
            'first_year_response': 2018
        }
        bizmod.update_elasticities(elasticities)
        bizmod.calc_withresponse()
    else:
        bizmod.calc_noresponse()
    # compare actual and expected results
    dec = 4
    results = (bizmod.corp_base.taxreturn.combined_return).round(dec)
    actual_vs_expect(results, 'bm_corp_base_nresp_expect.csv', precision=dec)
    results = (bizmod.corp_ref.taxreturn.combined_return).round(dec)
    actual_vs_expect(results, 'bm_corp_refm_nresp_expect.csv', precision=dec)
