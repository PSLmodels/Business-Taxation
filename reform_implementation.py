"""
This file provides the implementation of business tax reforms
"""


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
    for key in paramdict:
        assert key in brc_defaults_other.keys()
    if 'reclassify_taxdep_gdslife' in paramdict:
        year = paramdict['reclassify_taxdep_gdslife'].keys()[0]
        for life in paramdict['reclassify_taxdep_gdslife'][year]:
            assert life in [3, 5, 7, 10, 15, 20, 25, 27.5, 39]
    if 'reclassify_taxdep_adslife' in paramdict:
        year = paramdict['reclassify_taxdep_adslife'].keys()[0]
        for life in paramdict['reclassify_taxdep_adslife'][year]:
            assert life in [3, 4, 5, 6, 7, 9, 9.5, 10, 12, 14, 15,
                            18, 19, 20, 25, 28, 30, 40, 50, 100]


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

(mtr_nclist_ref, mtr_elist_ref) = gen_mtr_lists(iit_params_ref)
btax_params_reform['tau_nc'] = mtr_nclist_ref
btax_params_reform['tau_e'] = mtr_elist_ref
print "All parameters updated"
