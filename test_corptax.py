import numpy as np
import pandas as pd

track_progress = False

OVERWRITE = False

# Corporate tax results to check
vars_to_check = ['ebitda', 'taxDep', 'nid', 'sec199', 'taxinc', 'taxbc',
                 'ftc', 'amt', 'pymtc', 'gbc', 'taxrev']

# No II tax changes or behavioral responses
iit_params_ref = {}
elast_dict = {}

"""
Test C0: No reform
"""
btax_dict1 = {}
btax_dict2 = {}
exec(open('run_brc.py').read())
testpass0 = True
if OVERWRITE:
    combined_ref.to_csv('test_results/test_corp0_out.csv', index=False)
else:
    expected_output = pd.read_csv('test_results/test_corp0_out.csv')
    for v in vars_to_check:
        expected = expected_output[v]
        result = combined_ref[v]
        testpass0 *= np.allclose(expected, result, atol = 1e-08)

"""
Test C1: Multiple policy changes
    Corporate income tax rate
    Depreciation rules
    Net interest deduction
    AMT & PYMTC
    Section 199 haircut
    FTC haircut
"""
btax_dict1 = {2017: {
        'tau_c': 0.3,
        'depr_3yr_method': 'GDS',
        'depr_3yr_bonus': 0.8,
        'depr_5yr_method': 'ADS',
        'depr_5yr_bonus': 0.8,
        'depr_7yr_method': 'Economic',
        'depr_7yr_bonus': 0.8,
        'depr_10yr_method': 'GDS',
        'depr_10yr_bonus': 0.6,
        'depr_15yr_method': 'Expensing',
        'depr_15yr_bonus': 0.6,
        'depr_20yr_method': 'ADS',
        'depr_20yr_bonus': 0.4,
        'depr_25yr_method': 'EconomicDS',
        'depr_25yr_bonus': 0.2,
        'depr_275yr_method': 'GDS',
        'depr_275yr_bonus': 0.2,
        'depr_39yr_method': 'ADS',
        'depr_39yr_bonus': 0.2,
        'tau_amt': 0.0,
        'pymtc_status': 1}}
btax_dict2 = {'netIntPaid_corp_hc': {2018: 0.5},
              'sec199_hc': {2018: 0.5},
              'ftc_hc': {2018: 0.5}}
exec(open('run_brc.py').read())
testpass1 = True
if OVERWRITE:
    combined_ref.to_csv('test_results/test_corp1_out.csv', index=False)
else:
    expected_output = pd.read_csv('test_results/test_corp1_out.csv')
    for v in vars_to_check:
        expected = expected_output[v]
        result = combined_ref[v]
        testpass1 *= np.allclose(expected, result, atol = 1e-08)


"""
Test C2: Remainiing untested changes
    Interest paid haircuts
    Haircut on undepreciated basis
    Reclassify depreciation life
"""
btax_dict1 = {}
btax_dict2 = {'oldIntPaid_corp_hc': {2017: 0.5},
              'newIntPaid_corp_hc': {2017: 1.0},
              'undepBasis_corp_hc': {2018: 0.5},
              'reclassify_taxdep_gdslife': {2018: {39: 25}}}
exec(open('run_brc.py').read())
testpass2 = True
if OVERWRITE:
    combined_ref.to_csv('test_results/test_corp2_out.csv', index=False)
else:
    expected_output = pd.read_csv('test_results/test_corp2_out.csv')
    for v in vars_to_check:
        expected = expected_output[v]
        result = combined_ref[v]
        testpass2 *= np.allclose(expected, result, atol = 1e-08)

# Display test results
if testpass0:
    print('Test corptax 0: PASS')
else:
    print('Test corptax 0: FAIL')
if testpass1:
    print('Test corptax 1: PASS')
else:
    print('Test corptax 1: FAIL')
if testpass2:
    print('Test corptax 2: PASS')
else:
    print('Test corptax 2: FAIL')

