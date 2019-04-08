"""
Test Business-Taxation JSON parameter files.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_parameters.py

import os
import json
import pytest
from biztax import Policy, START_YEAR


@pytest.mark.parametrize("fname",
                         [("policy_current_law.json")])
def test_json_file_contents(tests_path, fname):
    """
    Check contents of JSON parameter files.
    """
    # specify test information
    required_keys = ['name', 'desc',
                     'sec1', 'sec2', 'notes',
                     'row_label',
                     'col_var', 'col_label',
                     'value_type', 'value', 'valid_values']
    valid_value_types = ['boolean', 'integer', 'real', 'string']
    invalid_keys = ['invalid_minmsg', 'invalid_maxmsg', 'invalid_action']
    # read JSON parameter file into a dictionary
    path = os.path.join(tests_path, '..', fname)
    pfile = open(path, 'r')
    allparams = json.load(pfile)
    pfile.close()
    assert isinstance(allparams, dict)
    # check elements in each parameter sub-dictionary
    failures = ''
    for pname in allparams:
        # all parameter names should be strings
        assert isinstance(pname, str)
        # check that param contains required keys
        param = allparams[pname]
        assert isinstance(param, dict)
        for key in required_keys:
            assert key in param
        if param['value_type'] == 'string':
            for key in invalid_keys:
                assert key not in param
            assert isinstance(param['valid_values']['options'], list)
        else:
            for key in invalid_keys:
                assert key in param
            assert param['invalid_action'] in ['stop', 'warn']
        # check for non-empty name and desc strings
        assert isinstance(param['name'], str)
        if not param['name']:
            assert '{} name'.format(pname) == 'empty string'
        assert isinstance(param['desc'], str)
        if not param['desc']:
            assert '{} desc'.format(pname) == 'empty string'
        # check that value_type is correct string
        if not param['value_type'] in valid_value_types:
            msg = 'param:<{}>; value_type={}'
            fail = msg.format(pname, param['value_type'])
            failures += fail + '\n'
        # check that cpi_inflatable param has value_type real
        if param['cpi_inflatable'] and param['value_type'] != 'real':
            msg = 'param:<{}>; value_type={}; cpi_inflatable={}'
            fail = msg.format(pname, param['value_type'],
                              param['cpi_inflatable'])
            failures += fail + '\n'
        # ensure that cpi_inflatable is False when value_type is not real
        if param['cpi_inflatable'] and param['value_type'] != 'real':
            msg = 'param:<{}>; cpi_inflatable={}; value_type={}'
            fail = msg.format(pname, param['cpi_inflatable'],
                              param['value_type'])
            failures += fail + '\n'
        # check that row_label is list
        rowlabel = param['row_label']
        assert isinstance(rowlabel, list)
        # check all row_label values
        cyr = START_YEAR
        for rlabel in rowlabel:
            assert int(rlabel) == cyr
            cyr += 1
        # check type and dimension of value
        value = param['value']
        assert isinstance(value, list)
        assert len(value) == len(rowlabel)
        # check that col_var and col_label are consistent
        cvar = param['col_var']
        assert isinstance(cvar, str)
        clab = param['col_label']
        if cvar == '':
            assert isinstance(clab, str) and clab == ''
        else:
            msg = 'param:<{}>; collab={}'
            fail = msg.format(pname, clab)
            failures += fail + '\n'
        # check that there are no indexed parameters
        if param['cpi_inflated']:
            msg = 'param:<{}>; cpi_inflated=True'
            fail = msg.format(pname)
            failures += fail + '\n'
    if failures:
        raise ValueError(failures)
