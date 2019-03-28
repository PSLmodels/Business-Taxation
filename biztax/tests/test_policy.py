"""
Test Policy class.
"""
import os
import numpy
import pandas
import pytest
import taxcalc as itax
from biztax import Policy, Data, START_YEAR, END_YEAR, NUM_YEARS


def test_policy_json_content():
    """
    Test contents of policy_current_law.json file
    """
    policy_object = Policy()
    policy = getattr(policy_object, '_vals')
    for _, data in policy.items():
        start_year = data.get('start_year')
        assert isinstance(start_year, int)
        assert start_year == START_YEAR
        row_label = data.get('row_label')
        assert isinstance(row_label, list)
        value = data.get('value')
        expected_row_label = [str(start_year + i) for i in range(len(value))]
        if row_label != expected_row_label:
            msg = 'name,row_label,expected_row_label: {}\n{}\n{}'
            raise ValueError(msg.format(data.get('long_name')), row_label,
                             expected_row_label)


def test_implement_reform():
    """
    Test (in)correct use of implement_reform method
    """
    policy = Policy()
    # incorrect uses of implement_reform
    with pytest.raises(ValueError):
        policy.implement_reform(list())
    with pytest.raises(ValueError):
        policy.implement_reform({2099: {'_tau_c': [0.20]}})
    policy.set_year(2019)
    with pytest.raises(ValueError):
        policy.implement_reform({2018: {'_tau_c': [0.20]}})
    with pytest.raises(ValueError):
        policy.implement_reform({2020: {'_tau_c': [-0.2]}})
    with pytest.raises(ValueError):
        policy.implement_reform({2020: {'_inventory_method': ['XIFO']}})
    del policy
    # correct use of implement_reform
    policy = Policy()
    reform = {
        2021: {
            '_tau_c': [0.20],
            '_inventory_method': ['FIFO'],
            '_newIntPaid_corp_hcyear': [2018]
        }
    }
    policy.implement_reform(reform)
    policy.set_year(2020)
    assert policy.tau_c > 0.20
    assert policy.inventory_method == 'Mix'
    assert policy.newIntPaid_corp_hcyear == 0
    policy.set_year(2021)
    assert policy.tau_c == 0.20
    assert policy.inventory_method == 'FIFO'
    assert policy.newIntPaid_corp_hcyear == 2018
    policy.set_year(2022)
    assert policy.tau_c == 0.20
    assert policy.inventory_method == 'FIFO'
    assert policy.newIntPaid_corp_hcyear == 2018


def test_parameters_dataframe():
    """
    Test parameters_dataframe() method
    """
    policy = Policy()
    ppdf = policy.parameters_dataframe()
    assert isinstance(ppdf, pandas.DataFrame)
    assert len(ppdf.index) == NUM_YEARS
    assert ppdf['year'][0] == START_YEAR
    assert ppdf['year'][NUM_YEARS - 1] == END_YEAR
    assert ppdf['tau_c'][START_YEAR - START_YEAR] == 0.347
    assert ppdf['tau_c'][END_YEAR - START_YEAR] == 0.347
    with pytest.raises(KeyError):
        ppdf['tau_c'][-1]
    with pytest.raises(KeyError):
        ppdf['tau_c'][END_YEAR - START_YEAR + 1]
    with pytest.raises(KeyError):
        ppdf['tau_c'][START_YEAR]
    with pytest.raises(KeyError):
        ppdf['tau_c'][END_YEAR]
    with pytest.raises(KeyError):
        ppdf['unknown_parameter'][0]


def test_policy_values(tests_path):
    """
    Compare btax policy parameter values from two different sources:
    biztax/policy_current_law.json and biztax/mini_params_btax.csv
    """
    # read policy parameter DataFrame from biztax/mini_params_btax.csv
    params_csv = Data.read_csv(
        os.path.join(Data.CURRENT_PATH, 'mini_params_btax.csv')
    )
    assert isinstance(params_csv, pandas.DataFrame)
    # create policy parameter DataFrame from biztax/policy_current_law.json
    policy = Policy()
    params_json = policy.parameters_dataframe()
    assert isinstance(params_json, pandas.DataFrame)
    # compare params_json with params_csv
    assert set(params_json.columns) == set(params_csv.columns)
    params_with_diff = list()
    for pname in params_json:
        if params_csv[pname].dtype == numpy.object:
            allclose = numpy.all(params_json[pname] == params_csv[pname])
        else:
            allclose = numpy.allclose(params_json[pname], params_csv[pname])
        if not allclose:
            params_with_diff.append(pname)
    assert not params_with_diff
