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
from biztax import Policy, Data, BusinessModel


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
def reforms():
    reform_dict = dict()
    # reform 0, the baseline
    policy0 = Policy()
    reform_dict[0] = policy0.parameters_dataframe()
    # reform 1
    policy1 = Policy()
    reform1 = {
        2017: {
            '_tau_c': [0.3],
            '_depr_3yr_method': ['GDS'],
            '_depr_3yr_bonus': [0.8],
            '_depr_5yr_method': ['ADS'],
            '_depr_5yr_bonus': [0.8],
            '_depr_7yr_method': ['Economic'],
            '_depr_7yr_bonus': [0.8],
            '_depr_10yr_method': ['GDS'],
            '_depr_10yr_bonus': [0.6],
            '_depr_15yr_method': ['Expensing'],
            '_depr_15yr_bonus': [0.6],
            '_depr_20yr_method': ['ADS'],
            '_depr_20yr_bonus': [0.4],
            '_depr_25yr_method': ['GDS'],
            '_depr_25yr_bonus': [0.2],
            '_depr_275yr_method': ['GDS'],
            '_depr_275yr_bonus': [0.2],
            '_depr_39yr_method': ['ADS'],
            '_depr_39yr_bonus': [0.2],
            '_tau_amt': [0.0],
            '_pymtc_status': [1]
        },
        2018: {
            '_netIntPaid_corp_hc': [0.5],
            '_sec199_hc': [0.5],
            '_ftc_hc': [0.5]
        }
    }
    policy1.implement_reform(reform1)
    reform_dict[1] = policy1.parameters_dataframe()
    # reform 2
    policy2 = Policy()
    reform2 = {
        2017: {
            '_oldIntPaid_corp_hcyear': [2017],
            '_oldIntPaid_corp_hc': [0.5],
            '_newIntPaid_corp_hcyear': [2017],
            '_newIntPaid_corp_hc': [1.0],
            '_oldIntPaid_noncorp_hcyear': [2017],
            '_oldIntPaid_noncorp_hc': [0.5],
            '_newIntPaid_noncorp_hcyear': [2017],
            '_newIntPaid_noncorp_hc': [1.0]
        },
        2018: {
            '_undepBasis_corp_hcyear': [2018],
            '_undepBasis_corp_hc': [0.5],
            '_undepBasis_noncorp_hcyear': [2018],
            '_undepBasis_noncorp_hc': [0.5]
        }
    }
    policy2.implement_reform(reform2)
    reform_dict[2] = policy2.parameters_dataframe()
    return reform_dict


@pytest.fixture(scope='session')
def default_btax_params(tests_path):
    fname = os.path.join(tests_path, '..', 'mini_params_btax.csv')
    return pandas.read_csv(fname)


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
