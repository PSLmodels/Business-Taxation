"""
Using BRC: An example

This file provides an example of how to use BRC, and walks through the process
of creating a business model and getting the results.

The example here includes 3 changes to policy:
    Apply a 28% corporate tax rate
    Eliminate bonus depreciation
    50% haircut on the deductibility of interest on new debt
"""
from biztax import BusinessModel

# Create the main reform dictionary
btax_refdict = {2018: {'tau_c': 0.28, 
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
                       'oldIntPaid_noncorp_hcyear': 2018}}


# Create the (empty) reform dictionary for the individual income tax (taxcalc)
iitax_refdict = {}

# Create the BusinessModel object
BM = BusinessModel(btax_refdict, iitax_refdict)

# Run the static calculations
BM.calc_noresponse()

# Look at the changes in total corporate and individual income tax liability
BM.ModelResults

# Take a closer look at corporate tax items
# Baseline
(BM.corp_base.taxreturn.combined_return).round(4).to_csv('test_results/ex_out1.csv', index=False)
# Reform
(BM.corp_ref.taxreturn.combined_return).round(4).to_csv('test_results/ex_out2.csv', index=False)

# Add investment and debt responses
BM.update_elasticities({'inv_usercost_c': -1.0, 'inv_usercost_nc': -0.5,
                        'debt_taxshield_c': 0.4, 'debt_taxshield_nc': 0.2,
                        'first_year_response': 2018})
BM.calc_withresponse()

# Look at the changes in total corporate and individual income tax liability
BM.ModelResults

# Compare real effects on corporations
BM.corp_ref.real_results - BM.corp_base.real_results
