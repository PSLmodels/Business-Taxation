"""
Test PassThrough class.
"""
import pytest
from biztax import PassThrough


@pytest.mark.parametrize('reform_number, results_type',
                         [(0, 'schc'),
                          (0, 'part'),
                          (0, 'scor'),
                          (1, 'schc'),
                          (1, 'part'),
                          (1, 'scor'),
                          (2, 'schc'),
                          (2, 'part'),
                          (2, 'scor')])
def test_passthrough_results(reform_number, results_type,
                             reforms, actual_vs_expect):
    """
    Test different passthrough results under different reforms.
    """
    pthru = PassThrough(reforms[reform_number]['params_df'])
    pthru.calc_static()
    decimals = 2
    if results_type == 'schc':
        results = pthru.SchC_results.round(decimals)
    elif results_type == 'part':
        results = pthru.partner_results.round(decimals)
    elif results_type == 'scor':
        results = pthru.Scorp_results.round(decimals)
    else:
        assert results_type == 'illegal passthrough results type'
    fname = 'pthru_ref{}_{}_expect.csv'.format(reform_number, results_type)
    actual_vs_expect(results, fname, precision=decimals)


def test_incorrect_instantiation():
    """
    Test incorrect PassThrough instantiation
    """
    with pytest.raises(ValueError):
        PassThrough(list())
