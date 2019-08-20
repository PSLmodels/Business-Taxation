"""
Contains pytest fixtures for the whole pytest session.
"""
# CODING-STYLE CHECKS:
# pycodestyle conftest.py

import os
import numpy
import pandas
import pytest
import taxcalc as itax
from biztax import Policy, Data


# convert all numpy warnings into errors so they can be detected in tests
numpy.seterr(all='raise')


@pytest.fixture(scope='session')
def tests_path():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def puf_path(tests_path):
    return os.path.join(tests_path, '..', '..', 'puf.csv')


@pytest.fixture(scope='session')
def puf_fullsample(puf_path):
    return pandas.read_csv(puf_path)


@pytest.fixture(scope='session')
def puf_subsample(puf_fullsample):
    # draw same puf.csv subsample as in Tax-Calculator test_pufcsv.py
    return puf_fullsample.sample(frac=0.05, random_state=2222)


@pytest.fixture(scope='session')
def clp_params_df():  # current-law policy parameters as a multi-year DataFrame
    policy = Policy()
    return policy.parameters_dataframe()


@pytest.fixture(scope='session')
def reforms():
    reform_dict = dict()
    # reform 0, the baseline
    policy0 = Policy()
    reform_dict[0] = {
        'params_df': policy0.parameters_dataframe(),
        'policy_obj': policy0
    }
    # reform 1
    policy1 = Policy()
    reform1 = {
        # 2017 provisions:
        'tau_c': {2017: 0.3},
        'depr_3yr_method': {2017: 'GDS'},
        'depr_3yr_bonus': {2017: 0.8},
        'depr_5yr_method': {2017: 'ADS'},
        'depr_5yr_bonus': {2017: 0.8},
        'depr_7yr_method': {2017: 'Economic'},
        'depr_7yr_bonus': {2017: 0.8},
        'depr_10yr_method': {2017: 'GDS'},
        'depr_10yr_bonus': {2017: 0.6},
        'depr_15yr_method': {2017: 'Expensing'},
        'depr_15yr_bonus': {2017: 0.6},
        'depr_20yr_method': {2017: 'ADS'},
        'depr_20yr_bonus': {2017: 0.4},
        'depr_25yr_method': {2017: 'GDS'},
        'depr_25yr_bonus': {2017: 0.2},
        'depr_275yr_method': {2017: 'GDS'},
        'depr_275yr_bonus': {2017: 0.2},
        'depr_39yr_method': {2017: 'ADS'},
        'depr_39yr_bonus': {2017: 0.2},
        'tau_amt': {2017: 0.0},
        'pymtc_hc': {2017: 1.0},
        # 2018 provisions:
        'intPaid_corp_hc': {2018: 0.5},
        'intIncome_corp_hc': {2018: 0.5},
        'sec199_rt': {2018: 0.045},
        'ftc_hc': {2018: 0.5}
    }
    policy1.implement_reform(reform1)
    reform_dict[1] = {
        'params_df': policy1.parameters_dataframe(),
        'policy_obj': policy1
    }
    # reform 2
    policy2 = Policy()
    reform2 = {
        # 2017 provisions:
        'oldIntPaid_corp_hcyear': {2017: 2017},
        'oldIntPaid_corp_hc': {2017: 0.5},
        'newIntPaid_corp_hcyear': {2017: 2017},
        'newIntPaid_corp_hc': {2017: 1.0},
        'oldIntPaid_noncorp_hcyear': {2017: 2017},
        'oldIntPaid_noncorp_hc': {2017: 0.5},
        'newIntPaid_noncorp_hcyear': {2017: 2017},
        'newIntPaid_noncorp_hc': {2017: 1.0},
        # 2018 provisions:
        'undepBasis_corp_hcyear': {2018: 2018},
        'undepBasis_corp_hc': {2018: 0.5},
        'undepBasis_noncorp_hcyear': {2018: 2018},
        'undepBasis_noncorp_hc': {2018: 0.5}
    }
    policy2.implement_reform(reform2)
    reform_dict[2] = {
        'params_df': policy2.parameters_dataframe(),
        'policy_obj': policy2
    }
    return reform_dict


@pytest.fixture(scope='session')
def actual_vs_expect():
    """
    Code template for comparing actual DataFrame with expected DataFrame
    read from a CSV-formatted file.
    """
    def act_vs_exp(act_df, exp_csv_filename, precision=0):
        """
        The function returned by the actual_vs_expect fixture.
        """
        tests_path = os.path.abspath(os.path.dirname(__file__))
        exp_path = os.path.join(tests_path, exp_csv_filename)
        exp_df = pandas.read_csv(exp_path, index_col=False)
        assert list(act_df.columns.values) == list(exp_df.columns.values)
        diffs = False
        for col in act_df.columns.values:
            if not numpy.allclose(act_df[col], exp_df[col]):
                diffs = True
        if diffs:
            act_csv_filename = '{}{}'.format(exp_path[:-10], 'actual.csv')
            frmt = '%.{}f'.format(precision)
            act_df.to_csv(act_csv_filename, float_format=frmt, index=False)
            act_fname = os.path.basename(act_csv_filename)
            exp_fname = exp_csv_filename
            msg = '\n'
            msg += 'NEW RESULTS IN FILE {}\n'.format(act_fname)
            msg += 'DIFFER FROM IN FILE {}\n'.format(exp_fname)
            msg += 'If diffs are OK, move ACTUAL file to EXPECT file and '
            msg += 'rerun test.'
            raise ValueError(msg)
    return act_vs_exp
