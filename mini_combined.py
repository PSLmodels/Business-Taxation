"""
All functions for the calculations.
"""
def calc_I(delta, r, a, b):
    # Calculates amount of nominal gross income (EBITDA) per period
    # a: beginning of time period
    # b: end of time period
    if r + delta == 0:
        I = b - a
    else:
        I = (1 / (r + delta) * np.exp(-(r + delta) * a) *
             (1 - np.exp(-(r + delta) * (b - a))))
    return I

def calc_Ilist(delta, r, length=100):
    I0 = calc_I(delta, r, 0, 0.5)
    Ilist = [I0]
    for j in range(1, length):
        Ilist.append(calc_I(delta, r, j-0.5, j+0.5))
    return Ilist

def calc_F(f, r, i, delta, fracded, a, b):
    F = f * fracded * np.exp(-i * a) * (1 - np.exp(-i * (b - a)))
    F = (f * i / (r + delta) * fracded * np.exp(-(r + delta) * a) *
         (1 - np.exp(-(r + delta) * (b - a))))
    return F

def calc_Flist(f, r, i, delta, fracded, length=100):
    Flist = [calc_F(f, r, i, delta, fracded, 0, 0.5)]
    for j in range(1, length):
        Flist.append(calc_F(f, r, i, delta, fracded, j-0.5, j+0.5))
    return Flist

def calc_Dlist_exp(length=100):
    Dlist = [0] * length
    Dlist[0] = 1
    return Dlist

def calc_D_econ(delta, r, a, b):
    if r + delta == 0:
        D = delta * (b - a)
    else:
        D = (delta / (r + delta) * np.exp(-(r + delta) * a) *
             (1 - np.exp(-(r + delta) * (b - a))))
    return D

def calc_Dlist_econ(delta, r, bonus, length=100):
    Dlist = [bonus + (1 - bonus) * calc_D_econ(delta, r, 0, 0.5)]
    for j in range(1, length):
        Dlist.append((1 - bonus) * calc_D_econ(delta, r, j-0.5, j+0.5))
    return Dlist

def calc_D_dbsl(N, L, r, pi, a, b):
    N = N * 1.0
    t1 = L * (1 - 1 / N)
    t2 = L
    if b <= t1:
        D = (N / L / (r + pi + N / L) * np.exp(-(r + pi + N / L) * a) *
             (1 - np.exp(-(r + pi + N / L) * (b - a))))
    elif b <= t2:
        if a < t1:
            Ddb = (N / L / (r + pi + N / L) * np.exp(-(r + pi + N / L) * a) *
                   (1 - np.exp(-(r + pi + N / L) * (t1 - a))))
            Dsl = (N / L / (r + pi) * np.exp(1 - N) * np.exp(-(r + pi) * t1) *
                   (1 - np.exp(-(r + pi) * (b - t1))))
            D = Ddb + Dsl
        else:
            D = (N / L / (r + pi) * np.exp(1 - N) * np.exp(-(r + pi) * a) *
                 (1 - np.exp(-(r + pi) * (b - a))))
    else:
        if a < t2:
            D = (N / L / (r + pi) * np.exp(1 - N) * np.exp(-(r + pi) * a) *
                 (1 - np.exp(-(r + pi) * (t2 - a))))
        else:
            D = 0
    return D

def calc_Dlist_dbsl(N, L, bonus, r, pi, length=100):
    Dlist = [bonus + (1 - bonus) * calc_D_dbsl(N, L, r, pi, 0, 0.5)]
    for j in range(1, length):
        Dlist.append((1 - bonus) * calc_D_dbsl(N, L, r, pi, j-0.5, j+0.5))
    return Dlist

def calc_Dlist(method, life, delta, r, pi, bonus, length=100):
    assert method in ['DB 200%', 'DB 150%', 'SL', 'Economic', 'Expensing', 'None']
    assert bonus >= 0 and bonus <= 1
    if type(length) != int:
        length = int(length)
    if method == 'DB 200%':
        Dlist = calc_Dlist_dbsl(2, life, bonus, r, pi, length)
    elif method == 'DB 150%':
        Dlist = calc_Dlist_dbsl(1.5, life, bonus, r, pi, length)
    elif method == 'SL':
        Dlist = calc_Dlist_dbsl(1.0, life, bonus, r, pi, length)
    elif method == 'Economic':
        Dlist = calc_Dlist_econ(delta, r, bonus, length)
    elif method == 'Expensing':
        Dlist = calc_Dlist_exp(length)
    else:
        Dlist = [0] * length
    return Dlist

def calc_Tlist(tdict, length):
    # tdict is a dictionary of tax rates and when they become effective
    # tdict may not be empty
    # tdict must contain at least one key of '0'
    # tdict keys must be as nonnegative integers
    assert len(tdict) > 0
    changelist = []
    for key in tdict:
        changelist.append(int(key))
    changelist.sort()
    ratelist = []
    for chg in changelist:
        ratelist.append(tdict[str(chg)])
    numrates = len(ratelist)
    rateind = 0
    Tlist = [tdict[str(changelist[0])]]
    for j in range(1, length):
        if rateind + 1 == numrates:
            Tlist.append(ratelist[rateind])
        else:
            if j < changelist[rateind+1]:
                Tlist.append(ratelist[rateind])
            else:
                rateind = rateind + 1
                Tlist.append(ratelist[rateind])
    return Tlist

def calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length=100):
    Tlist = np.asarray(calc_Tlist(tdict, length))
    Nlist = np.asarray(calc_Ilist(delta, r, length))
    Dlist = np.asarray(calc_Dlist(method, life, delta, r, pi, bonus, length))
    Flist = np.asarray(calc_Flist(f, r, rd, delta, fracded, length))
    A = sum(Dlist * Tlist)
    F = sum(Flist * Tlist)
    N = sum(Nlist * (1 - Tlist))
    rho = (1 - A - F) / N - delta
    return rho

def calc_rho_inv(r, pi, inv_method, hold, tdict):
    assert inv_method in ['FIFO', 'LIFO', 'Expensing', 'Mix']
    tau = tdict['0']
    rho_exp = r
    rho_lifo = 1 / hold * np.log((np.exp((r + pi) * hold) - tau) / (1 - tau)) - pi
    rho_fifo = 1 / hold * np.log((np.exp(r * hold) - tau) / (1 - tau))
    if inv_method == 'FIFO':
        rho_inv = rho_fifo
    elif inv_method == 'LIFO':
        rho_inv = rho_lifo
    elif inv_method == 'Expensing':
        rho_inv = rho_exp
    else:
        rho_inv = 0.5 * (rho_fifo + rho_lifo)
    return rho_inv

def calc_eatr(p, r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length=100):
    coc = calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length)
    assert p >= coc
    Rstar = (p - r) / (r + delta)
    P = p / (r + delta)
    Tlist = np.asarray(calc_Tlist(tdict, length))
    Nlist = np.asarray(calc_Ilist(delta, r, length))
    Dlist = np.asarray(calc_Dlist(method, life, delta, r, pi, bonus, length))
    Flist = np.asarray(calc_Flist(f, r, rd, delta, fracded, length))
    A = sum(Dlist * Tlist)
    F = sum(Flist * Tlist)
    N = sum(Nlist * (1 - Tlist))
    R = -(1 - A - F) + (p + delta) * N
    eatr = (Rstar - R) / P
    return eatr

def calc_usercost(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length=100):
    coc = calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length)
    ucoc = coc + delta
    return ucoc


"""
All code for parameters
"""
def test_btax_reform(paramdict):
    assert type(paramdict) == dict
    paramnames = list(btax_defaults)
    paramnames.remove('year')
    keylist = []
    for key in paramdict:
        key2 = int(key)
        assert key2 in range(2017, 2027)
        keylist.append(key2)
        #for mod in paramdict[key]:
        for param in paramdict[key]:
            assert param in paramnames

def update_btax_params(param_dict):
    """
    param_dict is a year: mod dictionary. Acceptable years are 2017-2027. Ex:
        {'2018': {'tau_c': 0.3}}
    """
    test_btax_reform(param_dict)
    params_df = copy.deepcopy(btax_defaults)
    yearlist = []
    for key in param_dict:
        yearlist.append(int(key))
    yearlist.sort()
    for year in yearlist:
        for param in param_dict[str(year)]:
            params_df[param][params_df['year'] >= year] = param_dict[str(year)][param]
    return params_df

def make_tdict_c(btax_params, start_year):
    """
    btax_params is a DataFrame of the btax parameters
    Produces a dictionary of tax rates and changes to those rates.
    For use when calculating rho and EATR
    Assumes no changes after 2027
    """
    assert start_year >= 2017
    assert type(start_year) == int
    if start_year >= 2027:
        tdict = {'0': btax_params['tau_c'][10]}
    else:
        tdict = {'0': btax_params['tau_c'][start_year-2014]}
        for i in range(start_year - 2016, len(btax_params['year']) - 3):
            if btax_params['tau_c'][i+3] != btax_params['tau_c'][i+2]:
                tdict[str(i - (start_year-2017))] = btax_params['tau_c'][i+3]
    return tdict

def make_tdict_nc(btax_params, start_year):
    """
    btax_params is a DataFrame of the btax parameters
    Produces a dictionary of tax rates and changes to those rates.
    For use when calculating rho and EATR
    Assumes no changes after 2027
    """
    assert start_year >= 2017
    assert type(start_year) == int
    if start_year >= 2027:
        tdict = {'0': btax_params['tau_nc'][13]}
    else:
        tdict = {'0': btax_params['tau_nc'][start_year-2014]}
        for i in range(start_year - 2016, len(btax_params['year']) - 3):
            tdict[str(i - (start_year-2017))] = btax_params['tau_nc'][i+3]
    return tdict

def get_econ_params_oneyear(econ_params, year):
    r_d = econ_params['r_d'][year-2017]
    r_e_c = econ_params['r_e_c'][year-2017]
    r_e_nc = econ_params['r_e_nc'][year-2017]
    pi = econ_params['pi'][year-2017]
    f_c = econ_params['f_c'][year-2017]
    f_nc = econ_params['f_nc'][year-2017]
    r_c = f_c * r_d + (1 - f_c) * r_e_c
    r_nc = f_nc * r_d + (1 - f_nc) * r_e_nc
    return(r_c, r_nc, r_d, pi, f_c, f_nc)


"""
Code to run btax-mini
"""
def calc_frac_ded(other_params, year):
    """
    fracded is the fraction of interest deductible for all future years
    other_params is the dictionary of parameters not in btax_params
    """
    (hc_nid_year_c, hc_nid_c) = extract_other_param('netIntPaid_corp_hc',
                                                    other_params)
    (hc_id_new_year_c, hc_id_new_c) = extract_other_param('newIntPaid_corp_hc',
                                                          other_params)
    if year < min(hc_nid_year_c, hc_id_new_year_c):
        fracdedc = 1.0
    elif year >= max(hc_nid_year_c, hc_id_new_year_c):
        fracdedc = 1.0 - max(hc_nid_c, hc_id_new_c)
    else:
        if hc_nid_year_c > hc_id_new_year_c:
            fracdedc = 1.0 - hc_id_new_c
        else:
            fracdedc = 1.0 - hc_nid_c
    (hc_id_new_year_nc, hc_id_new_nc) = extract_other_param('newIntPaid_noncorp_hc',
                                                            other_params)
    if year < hc_id_new_year_nc:
        fracdedn = 1.0
    else:
        fracdedn = 1.0 - hc_id_new_nc
    return (fracdedc, fracdedn)

def build_prelim_oneyear(year, econ_params, btax_params, other_params):
    assert year in range(2017, 2028)
    [r_c, r_nc, r_d, pi, f_c, f_nc] = get_econ_params_oneyear(econ_params, year)
    taxdep = get_btax_params_oneyear(btax_params, year)
    tdict_c = make_tdict_c(btax_params, year)
    tdict_nc = make_tdict_nc(btax_params, year)
    asset_data = copy.deepcopy(assets_data)
    main_data = asset_data.merge(right=taxdep, how='outer', on='Asset')
    (fracded_c, fracded_nc) = calc_frac_ded(other_params, year)
    inv_method = btax_params['inventory_method'][year-2014]
    assets = np.asarray(main_data['Asset'])
    uc_c = np.zeros(len(assets))
    uc_nc = np.zeros(len(assets))
    # Add in EATRs?
    for j in range(len(main_data)):
        uc_c[j] = calc_usercost(r_c, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_c, r_d, fracded_c, tdict_c, 100)
        uc_nc[j] = calc_usercost(r_nc, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_nc, r_d, fracded_nc, tdict_nc, 100)
    uc_c[assets == 'Inventories'] = calc_rho_inv(r_c, pi, inv_method, 0.5, tdict_c)
    uc_nc[assets == 'Inventories'] = calc_rho_inv(r_nc, pi, inv_method, 0.5, tdict_nc)
    main_data['uc_c'] = uc_c
    main_data['uc_nc'] = uc_nc
    main_data.drop(['assets_c', 'assets_nc', 'L', 'Method', 'bonus', 'delta'], axis=1, inplace=True)
    return main_data

def run_btax_mini(yearlist, btax_params, other_params):
    econ_params_df = copy.deepcopy(econ_defaults)
    basedata = copy.deepcopy(assets_data)
    for year in yearlist:
        results_oneyear = build_prelim_oneyear(year, econ_params_df, btax_params, other_params)
        results_oneyear.rename(columns={'uc_c': 'u_c' + str(year), 'uc_nc': 'u_nc' + str(year)}, inplace=True)
        basedata = basedata.merge(right=results_oneyear, how='outer', on='Asset')
    basedata.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
    return basedata

def inv_response(firstyear):
    """
    This function calculates the cost of capital under the baseline and reform.
    It returns the percent change in investment and the MPK.
    firstyear: when the firm behavioral response takes effect
    """
    assert type(firstyear) is int
    assert firstyear in range(2017, 2028)
    maindata = copy.deepcopy(assets_data)
    maindata.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
    elast_c = elast_dict['inv_usercost_c']
    elast_nc = elast_dict['inv_usercost_nc']
    for year in range(2014, firstyear):
        maindata['deltaIc' + str(year)] = 0.
        maindata['deltaInc' + str(year)] = 0.
        maindata['deltaEc' + str(year)] = 0.
        maindata['deltaEnc' + str(year)] = 0.
    results_base = run_btax_mini(range(firstyear, 2028), btax_defaults, brc_defaults_other)
    results_ref = run_btax_mini(range(firstyear, 2028), btax_params_reform, other_params_reform)
    for year in range(firstyear, 2028):
        maindata['deltaIc' + str(year)] = (results_ref['u_c' + str(year)] / results_base['u_c' + str(year)] - 1) * elast_c
        maindata['deltaInc' + str(year)] = (results_ref['u_nc' + str(year)] / results_base['u_nc' + str(year)] - 1) * elast_nc
        maindata['deltaEc' + str(year)] = (results_ref['u_c' + str(year)] + results_base['u_c' + str(year)]) / 2.0
        maindata['deltaEnc' + str(year)] = (results_ref['u_nc' + str(year)] + results_base['u_nc' + str(year)]) / 2.0
    return maindata

