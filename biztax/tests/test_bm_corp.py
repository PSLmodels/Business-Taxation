"""
Test corpoate-aspects of BusinessModel class.
"""
import os
import numpy
import pandas as pd
from biztax import BusinessModel


def test_bm_corp(actual_vs_expect):
    """
    Test BusinessModel corporate results under a corporate-income-tax reform.
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
    # calculate results assuming no responses
    bizmod = BusinessModel(citax_refdict, iitax_refdict)
    bizmod.calc_noresponse()
    # compare actual and expected results
    dec = 4
    results = (bizmod.corp_base.taxreturn.combined_return).round(dec)
    actual_vs_expect(results, 'bm_corp_base_nresp_expect.csv', precision=dec)
    results = (bizmod.corp_ref.taxreturn.combined_return).round(dec)
    actual_vs_expect(results, 'bm_corp_refm_nresp_expect.csv', precision=dec)

    """
    # Add investment and debt responses
    BM.update_elasticities({'inv_usercost_c': -1.0, 'inv_usercost_nc': -0.5,
                            'debt_taxshield_c': 0.4, 'debt_taxshield_nc': 0.2,
                            'first_year_response': 2018})
    BM.calc_withresponse()

    # Look at the changes in total corporate & individual income tax liability
    BM.ModelResults

    # Compare real effects on corporations
    BM.corp_ref.real_results - BM.corp_base.real_results
    """
