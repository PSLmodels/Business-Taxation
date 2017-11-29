"""
This file provides the implementation of business tax reforms
"""

"""
Set defauls for various, repeals and other provisions
Note that these must be constant after implementation.
"""
brc_defaults_other = {
    'undepBasis_corp_hc': {0: 0.0},
    'undepBasis_noncorp_hc': {0: 0.0},
    'amt_repeal': {9e99: False},
    'pymtc_repeal': {9e99: False},
    'ftc_hc': {9e99: 0.0},
    'sec199_hc': {9e99: 0.0},
    'oldIntPaid_corp_hc': {0: 0.0},
    'newIntPaid_corp_hc': {0: 0.0},
    'netIntPaid_corp_hc': {0: 0.0},
    'oldIntPaid_noncorp_hc': {0: 0.0},
    'newIntPaid_noncorp_hc': {0: 0.0}
}


def test_btax_reform(paramdict):
    assert type(paramdict) == dict
    paramnames = list(btax_defaults)
    paramnames.remove('year')
    keylist = []
    for key in paramdict:
        key2 = int(key)
        assert key2 in range(2014, 2027)
        for param in paramdict[key]:
            assert param in paramnames

def test_other_reform(paramdict):
    assert type(paramdict) == dict
    paramnames = brc_defaults_other.keys()
    for key in paramdict:
        assert key in brc_defaults_other.keys()
        #year = int(paramdict[key].keys()[0])
        #assert year in range(2014, 2027)


def update_btax_params(param_dict):
    """
    param_dict is a year: {param: value} dictionary.
    Acceptable years are 2017-2027. Ex:
        {'2018': {'tau_c': 0.3}}
    """
    test_btax_reform(param_dict)
    params_df = copy.deepcopy(btax_defaults)
    yearlist = []
    for key in param_dict:
        yearlist.append(key)
    yearlist.sort()
    years = np.asarray(params_df['year'])
    for year in yearlist:
        for param in param_dict[year]:
            paramlist1 = np.asarray(params_df[param])
            paramlist1[years >= int(year)] = param_dict[year][param]
            params_df[param] = paramlist1
    return params_df

def update_brc_params(paramdict_other):
    test_other_reform(paramdict_other)
    other_params = copy.deepcopy(brc_defaults_other)
    for key in paramdict_other:
        other_params[key] = paramdict_other[key]
    return other_params

def extract_other_param(paramname, paramdict):
    assert paramname in list(paramdict)
    year = list(paramdict[paramname])[0]
    val = paramdict[paramname][year]
    return (year, val)

btax_params_reform = update_btax_params(btax_dict1)
other_params_reform = update_brc_params(btax_dict2)

btax_params_reform['tau_nc'] = calc_mtr_nc_list(iit_params_ref)
print "All parameters updated"
