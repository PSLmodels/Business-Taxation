"""
Business-Taxation demo for PSL event
"""
import taxcalc as itax  # capabilities of individual Tax-Calculator
from biztax import Policy, BusinessModel, Response
import pandas as pd

btax_reform_dict0 = {'tau_c': {2020: 0.20}}

# Create business Policy object
btax_policy_reform0 = Policy()
btax_policy_reform0.implement_reform(btax_reform_dict0)

# Create an individual-tax itax.Policy object with no reform
itax_policy_noreform0 = itax.Policy()

# Execute BusinessModel calculations with no response
BM0 = BusinessModel(btax_policy_reform0, itax_policy_noreform0, investor_data='rpuf.csv')
BM0.calc_all(response=None)

print(BM0.model_results)
print('Change in corporate tax revenue ($B): ' +
      str(sum(BM0.model_results['CTax_change'])))




btax_reform_dict1 = {
    'depr_3yr_method': {2020: 'Expensing'},
    'depr_5yr_method': {2020: 'Expensing'},
    'depr_7yr_method': {2020: 'Expensing'},
    'depr_10yr_method': {2020: 'Expensing'},
    'depr_15yr_method': {2020: 'Expensing'},
    'depr_20yr_method': {2020: 'Expensing'},
    'depr_25yr_method': {2020: 'Expensing'},
    'depr_275yr_method': {2020: 'Expensing'},
    'depr_39yr_method': {2020: 'Expensing'},
    'undepBasis_corp_hc': {2020: 1.0},
    'undepBasis_corp_hcyear': {2020: 2020},
    'undepBasis_noncorp_hc': {2020: 1.0},
    'undepBasis_noncorp_hcyear': {2020: 2020},
    'intPaid_corp_hc': {2020: 1.0},
    'intPaid_noncorp_hc': {2020: 1.0},
    'capgains_corp_hc': {2020: 1.0},
    'statelocaltax_hc': {2020: 1.0},
    'pymtc_hc': {2020: 1.0}
}

# Create business Policy object
btax_policy_reform1 = Policy()
btax_policy_reform1.implement_reform(btax_reform_dict1)

# Create an individual-tax itax.Policy object with no reform
itax_policy_noreform1 = itax.Policy()

# Execute BusinessModel calculations with no response
BM1 = BusinessModel(btax_policy_reform1, itax_policy_noreform1, investor_data='rpuf.csv')
BM1.calc_all(response=None)

print(BM1.model_results)
print('Change in corporate tax revenue ($B): ' +
      str(sum(BM1.model_results['CTax_change'])))

btax_reform_dict2 = {
    'tau_c': {2020: 0.15},
    'depr_3yr_method': {2020: 'Economic'},
    'depr_5yr_method': {2020: 'Economic'},
    'depr_7yr_method': {2020: 'Economic'},
    'depr_10yr_method': {2020: 'Economic'},
    'depr_15yr_method': {2020: 'Economic'},
    'depr_20yr_method': {2020: 'Economic'},
    'depr_25yr_method': {2020: 'Economic'},
    'depr_275yr_method': {2020: 'Economic'},
    'depr_39yr_method': {2020: 'Economic'},
    'depr_3yr_bonus': {2020: 0.0},
    'depr_5yr_bonus': {2020: 0.0},
    'depr_7yr_bonus': {2020: 0.0},
    'depr_10yr_bonus': {2020: 0.0},
    'depr_15yr_bonus': {2020: 0.0},
    'depr_20yr_bonus': {2020: 0.0},
    'depr_25yr_bonus': {2020: 0.0},
    'depr_275yr_bonus': {2020: 0.0},
    'depr_39yr_bonus': {2020: 0.0},
    'muniIntIncome_corp_hc': {2020: 0.0},
    'adjustedTaxInc_limit': {2020: 9e99},
    'statelocaltax_hc': {2020: 1.0},
    'pymtc_hc': {2018: 1.0},
    'GILTI_thd': {2020: 0.0},
    'GILTI_inclusion': {2020: 1.0},
    'fdii_rt': {2020: 0.0}
}

# Create business Policy object
btax_policy_reform2 = Policy()
btax_policy_reform2.implement_reform(btax_reform_dict2)

# Create an individual-tax itax.Policy object with no reform
itax_policy_noreform2 = itax.Policy()

# Execute BusinessModel calculations with no response
BM2 = BusinessModel(btax_policy_reform2, itax_policy_noreform2, investor_data='rpuf.csv')
BM2.calc_all(response=None)

print(BM2.model_results)
print('Change in corporate tax revenue ($B): ' +
      str(sum(BM2.model_results['CTax_change'])))


