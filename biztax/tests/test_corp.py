"""
Test Corporation class.
"""
import pytest
from biztax import Corporation


@pytest.mark.parametrize('reform_number, real_not_taxr_results',
                         [(0, True),
                          (0, False),
                          (1, True),
                          (1, False),
                          (2, True),
                          (2, False)])
def test_corporation_results(reform_number, real_not_taxr_results,
                             reforms, actual_vs_expect):
    """
    Test different corporation results under different reforms.
    """
    corp = Corporation(reforms[reform_number])
    corp.calc_static()
    decimals = 2
    if real_not_taxr_results:
        results = corp.real_results.round(decimals)
    else:
        results = corp.taxreturn.combined_return.round(decimals)
    res = 'real' if real_not_taxr_results else 'taxr'
    fname = 'corp_ref{}_{}_expect.csv'.format(reform_number, res)
    actual_vs_expect(results, fname, precision=decimals)


def test_incorrect_instantiation(default_btax_params):
    """
    Test incorrect Corporation instantiation
    """
    with pytest.raises(ValueError):
        Corporation(list())
