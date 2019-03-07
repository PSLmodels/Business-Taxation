import os
import numpy
import pandas as pd
import pytest
import taxcalc as tc


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
def actual_vs_expect():
    """
    Code template for comparing actual DataFrame with expected DataFrame
    read from a CSV-formatted file.
    """
    def act_vs_exp(act_df, exp_csv_filename, precision=1):
        """Actual function returned by the actual_vs_expect fixture."""
        tests_path = os.path.abspath(os.path.dirname(__file__))
        exp_path = os.path.join(tests_path, exp_csv_filename)
        exp_df = pd.read_csv(exp_path, index_col=False)
        # TODO: exp_df.drop('Unnamed: 0', axis='columns', inplace=True)
        diffs = False
        for icol in act_df.columns.values:
            if not numpy.allclose(act_df[icol], exp_df[str(icol)]):
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
