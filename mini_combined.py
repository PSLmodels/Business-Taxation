# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 18:35:34 2017

@author: Cody
"""

import pandas as pd
import numpy as np
import copy
import taxcalc
from taxcalc import *

"""
All functions for the calculations.
"""
def calc_I(delta, pi, a, b):
    # Calculates amount of nominal gross income (EBITDA) per period
    # a: beginning of time period
    # b: end of time period
    if delta == pi:
        I = 1
    else:
        I = (1 / (pi - delta) * np.exp((pi - delta) * a) *
             (np.exp((pi - delta) * (b - a)) - 1))
    return I

def calc_Ilist(delta, pi, length=100):
    I0 = calc_I(delta, pi, 0, 0.5)
    Ilist = [I0]
    for j in range(1, length):
        Ilist.append(calc_I(delta, pi, j-0.5, j+0.5))
    return Ilist

def calc_F(f, i, fracded, a, b):
    F = f * i * (b - a) * fracded
    return F

def calc_Flist(f, i, fracded, length=100):
    Flist = [calc_F(f, i, fracded, 0, 0.5)]
    for j in range(1,length):
        Flist.append(calc_F(f, i, fracded, j-0.5, j+0.5))
    return Flist

def calc_Dlist_exp(length=100):
    Dlist = [0] * length
    Dlist[0] = 1
    return Dlist

def calc_D_econ(delta, pi, a, b):
    if delta == pi:
        D = delta * (b - a)
    else:
        D = (delta / (pi - delta) * (np.exp((pi - delta) * b) -
             np.exp((pi - delta) * a)))
    return D

def calc_Dlist_econ(delta, pi, bonus, length=100):
    Dlist = [bonus + (1 - bonus) * calc_D_econ(delta, pi, 0, 0.5)]
    for j in range(1, length):
        Dlist.append((1 - bonus) * calc_D_econ(delta, pi, j-0.5, j+0.5))
    return Dlist

def calc_D_dbsl(N, L, a, b):
    t1 = L * (1 - 1 / N)
    t2 = L
    if b <= t1:
        D = np.exp(-N / L * a) * (1 - np.exp(-N / L * (b - a)))
    elif b <= t2:
        if a < t1:
            Ddb = np.exp(-N / L * a) * (1 - np.exp(-N / L * (t1 - a)))
            Dsl = N / L * np.exp(1 - N) * (b - t1)
            D = Ddb + Dsl
        else:
            D = N / L * np.exp(1 - N) * (b - a)
    else:
        if a < t2:
            D = N / L * np.exp(1 - N) * (t2 - a)
        else:
            D = 0
    return D

def calc_Dlist_dbsl(N, L, bonus, length=100):
    Dlist = [bonus + (1 - bonus) * calc_D_dbsl(N, L, 0, 0.5)]
    for j in range(1, length):
        Dlist.append((1 - bonus) * calc_D_dbsl(N, L, j-0.5, j+0.5))
    return Dlist

def calc_Dlist(method, life, delta, pi, bonus, length=100):
    assert method in ['DB 200%', 'DB 150%', 'SL', 'Economic', 'Expensing', 'None']
    assert bonus >= 0 and bonus <= 1
    if type(length) != int:
        length = int(length)
    if method == 'DB 200%':
        Dlist = calc_Dlist_dbsl(2, life, bonus, length)
    elif method == 'DB 150%':
        Dlist = calc_Dlist_dbsl(1.5, life, bonus, length)
    elif method == 'SL':
        Dlist = calc_Dlist_dbsl(1.0, life, bonus, length)
    elif method == 'Economic':
        Dlist = calc_Dlist_econ(delta, pi, bonus, length)
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

def calc_DiscountFactorList(r, pi, length=100):
    if r + pi == 0:
        DFlist = np.ones(length)
    else:
        nomintd = np.exp(r + pi) - 1
        DFlist = []
        for j in range(length):
            DFlist.append(1 / (1 + nomintd)**j)
    return DFlist

def calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length=100):
    Tlist = np.asarray(calc_Tlist(tdict, length))
    Nlist = np.asarray(calc_Ilist(delta, pi, length))
    DFlist = np.asarray(calc_DiscountFactorList(r, pi, length))
    DDFlist = np.asarray(calc_DiscountFactorList(rd, pi, length))
    Dlist = np.asarray(calc_Dlist(method, life, delta, pi, bonus, length))
    Flist = np.asarray(calc_Flist(f, rd+pi, fracded, length))
    A = sum(Dlist * Tlist * DFlist)
    F = sum(Flist * Tlist * DDFlist)
    N = sum(Nlist * (1 - Tlist) * DFlist)
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
    Nlist = np.asarray(calc_Ilist(delta, pi, length))
    DFlist = np.asarray(calc_DiscountFactorList(r, pi, length))
    DDFlist = np.asarray(calc_DiscountFactorList(rd, pi, length))
    Dlist = np.asarray(calc_Dlist(method, life, delta, pi, bonus, length))
    Flist = np.asarray(calc_Flist(f, rd+pi, fracded, length))
    A = sum(Dlist * Tlist * DFlist)
    F = sum(Flist * Tlist * DDFlist)
    N = sum(Nlist * (1 - Tlist) * DFlist)
    R = -(1 - A - F) + (p + delta) * N
    eatr = (Rstar - R) / P
    return eatr

def calc_usercost(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length=100):
    coc = calc_rho(r, pi, delta, method, life, bonus, f, rd, fracded, tdict, length)
    ucoc = coc + delta
    return ucoc


"""
All code for tax depreciation information
"""
def get_taxdep_info():
    taxdep = pd.read_csv('btax/data/depreciation_rates/tax_depreciation_rates.csv')
    taxdep.drop(['GDS Class Life', 'System'], axis=1, inplace=True)
    taxdep.rename(columns={'GDS Life': 'L_gds', 'ADS Life': 'L_ads', 'Asset Type': 'Asset'}, inplace=True)
    taxdep['Asset'][81] = 'Motor vehicles and parts manufacturing'
    taxdep['Method'][taxdep['Asset'] == 'Land'] = 'None'
    taxdep['Method'][taxdep['Asset'] == 'Inventories'] = 'None'
    econdep = pd.read_csv('btax/data/depreciation_rates/Economic Depreciation Rates.csv')
    econdep['Asset'][78] = 'Communications equipment manufacturing'
    econdep['Asset'][81] = 'Motor vehicles and parts manufacturing'
    econdep.drop('Code', axis=1, inplace=True)
    econdep.rename(columns={'Economic Depreciation Rate': 'delta'}, inplace=True)
    depinfo = taxdep.merge(right=econdep, how='outer', on='Asset')
    return depinfo

taxdep_info_gross = get_taxdep_info()

def taxdep_final(depr_3yr_method, depr_3yr_bonus,
                 depr_5yr_method, depr_5yr_bonus,
                 depr_7yr_method, depr_7yr_bonus,
                 depr_10yr_method, depr_10yr_bonus,
                 depr_15yr_method, depr_15yr_bonus,
                 depr_20yr_method, depr_20yr_bonus,
                 depr_25yr_method, depr_25yr_bonus,
                 depr_275yr_method, depr_275yr_bonus,
                 depr_39yr_method, depr_39yr_bonus):
    taxdep = copy.deepcopy(taxdep_info_gross)
    taxdep['System'] = ''
    # Determine depreciation systems for each asset type
    taxdep['System'][taxdep['L_gds'] == 3] = depr_3yr_method
    taxdep['System'][taxdep['L_gds'] == 5] = depr_5yr_method
    taxdep['System'][taxdep['L_gds'] == 7] = depr_7yr_method
    taxdep['System'][taxdep['L_gds'] == 10] = depr_10yr_method
    taxdep['System'][taxdep['L_gds'] == 15] = depr_15yr_method
    taxdep['System'][taxdep['L_gds'] == 20] = depr_20yr_method
    taxdep['System'][taxdep['L_gds'] == 25] = depr_25yr_method
    taxdep['System'][taxdep['L_gds'] == 27.5] = depr_275yr_method
    taxdep['System'][taxdep['L_gds'] == 39] = depr_39yr_method
    # Determine asset lives to use
    taxdep['L'] = taxdep['L_gds']
    taxdep['L'][taxdep['System'] == 'ADS'] = taxdep['L_ads']
    taxdep['L'][taxdep['System'] == 'None'] = 100
    # Determine depreciation method
    taxdep['Method'][taxdep['System'] == 'ADS'] = 'SL'
    taxdep['Method'][taxdep['System'] == 'Economic'] = 'Economic'
    taxdep['Method'][taxdep['System'] == 'None'] = 'None'
    taxdep.drop(['System', 'L_gds', 'L_ads', ])
    return taxdep


"""
All code for parameters
"""
econ_defaults = pd.read_csv('mini_params_econ.csv')
btax_defaults = pd.read_csv('mini_params_btax.csv')

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
        tdict = {'0': btax_params['tau_c'][start_year-2017]}
        for i in range(start_year - 2016, len(btax_params['year'])):
            if btax_params['tau_c'][i] != btax_params['tau_c'][i-1]:
                tdict[str(i - (start_year-2017))] = btax_params['tau_c'][i]
    return tdict

records_url = 'puf.csv'
def make_calculator(reform_dict, start_year):
    policy1 = Policy()
    behavior1 = Behavior()
    records1 = Records(records_url)
    if reform_dict != {}:
        policy1.implement_reform(reform_dict)
    calc1 = Calculator(records = records1, policy = policy1, behavior = behavior1)
    calc1.advance_to_year(start_year)
    calc1.calc_all()
    return(calc1)
    

def get_mtr_nc(calc):
    mtr1 = calc.mtr('e00900p')[2]
    mtr2 = calc.mtr('e26270')[2]
    mtr3 = calc.mtr('e02000')[2]
    posti = (calc.records.c04800 > 0.)
    inc1 = np.abs(calc.records.e00900)
    inc2 = np.abs(calc.records.e26270)
    inc3 = np.abs(calc.records.e02000 - calc.records.e26270)
    wgt = calc.records.s006
    mtr_nc = (sum((mtr1 * inc1 + mtr2 * inc2 + mtr3 * inc3) * posti * wgt) / 
              sum((inc1 + inc2 + inc3) * posti * wgt))
    return mtr_nc
    
def make_tdict_nc(iitreform, start_year):
    """
    iitreform is a reform dictionary for taxcalc
    Produces a dictionary of tax rates and changes to those rates. 
    For use when calculating rho and EATR
    Assumes no changes after 2027
    """
    assert start_year >= 2017
    assert type(start_year) == int
    calc = make_calculator(iitreform, 2017)
    if start_year >= 2027:
        calc = make_calculator(iitreform, 2027)
        mtr1 = get_mtr_nc(calc)
        tdict = {'0': mtr1}
    else:
        calc = make_calculator(iitreform, start_year)
        tdict = {'0': get_mtr_nc(calc)}
        for i in range(start_year+1, 2027):
            calc.increment_year()
            calc.calc_all()
            tdict[str(i - start_year)] = get_mtr_nc(calc)
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

def get_btax_params_oneyear(btax_params, year):
    method_3yr = btax_params['depr_3yr_method'][year-2017]
    method_5yr = btax_params['depr_5yr_method'][year-2017]
    method_7yr = btax_params['depr_7yr_method'][year-2017]
    method_10yr = btax_params['depr_10yr_method'][year-2017]
    method_15yr = btax_params['depr_15yr_method'][year-2017]
    method_20yr = btax_params['depr_20yr_method'][year-2017]
    method_25yr = btax_params['depr_25yr_method'][year-2017]
    method_275yr = btax_params['depr_275yr_method'][year-2017]
    method_39yr = btax_params['depr_39yr_method'][year-2017]
    bonus_3yr = btax_params['depr_3yr_bonus'][year-2017]
    bonus_5yr = btax_params['depr_5yr_bonus'][year-2017]
    bonus_7yr = btax_params['depr_7yr_bonus'][year-2017]
    bonus_10yr = btax_params['depr_10yr_bonus'][year-2017]
    bonus_15yr = btax_params['depr_15yr_bonus'][year-2017]
    bonus_20yr = btax_params['depr_20yr_bonus'][year-2017]
    bonus_25yr = btax_params['depr_25yr_bonus'][year-2017]
    bonus_275yr = btax_params['depr_275yr_bonus'][year-2017]
    bonus_39yr = btax_params['depr_39yr_bonus'][year-2017]
    taxdep = taxdep_final(method_3yr, bonus_3yr, method_5yr, bonus_5yr,
                          method_7yr, bonus_7yr, method_10yr, bonus_10yr,
                          method_15yr, bonus_15yr, method_20yr, bonus_20yr,
                          method_25yr, bonus_25yr, method_275yr, bonus_275yr,
                          method_39yr, bonus_39yr)
    return taxdep



"""
Code to run btax-mini
"""

def build_prelim_oneyear(year, econ_params, btax_params, iitref):
    assert year in range(2017, 2028)
    [r_c, r_nc, r_d, pi, f_c, f_nc] = get_econ_params_oneyear(econ_params, year)
    taxdep = get_btax_params_oneyear(btax_params, year)
    tdict_c = make_tdict_c(btax_params, year)
    tdict_nc = make_tdict_nc(iitref, year)
    asset_data = pd.read_csv('mini_assets.csv')
    main_data = asset_data.merge(right=taxdep, how='outer', on='Asset')
    main_data.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
    main_data['uc_c'] = 0.
    #main_data['eatr_c'] = 0.
    main_data['uc_nc'] = 0.
    #main_data['eatr_nc'] = 0.
    for j in range(len(main_data)):
        main_data['uc_c'][j] = calc_usercost(r_c, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_c, r_d, 1-int_hc_c, tdict_c, 100)
        main_data['uc_nc'][j] = calc_usercost(r_nc, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_nc, r_d, 1-int_hc_nc, tdict_nc, 100)
    main_data['u_c'][main_data['Asset'] == 'Inventories'] = calc_rho_inv(r_c, pi, inv_method, 0.5, tdict_c)
    main_data['u_nc'][main_data['Asset'] == 'Inventories'] = calc_rho_inv(r_nc, pi, inv_method, 0.5, tdict_nc)
    main_data.drop(['L', 'Method', 'bonus'], axis=1, inplace=True)
    return main_data

def run_btax_mini(yearlist, btax_refdict, iit_refdict):
    btax_params_df = update_btax_params(btax_refdict)
    econ_params_df = copy.deepcopy(econ_defaults)
    basedata = pd.read_csv('mini_assets.csv')
    for year in yearlist:
        results_oneyear = build_prelim_oneyear(year, econ_params_df, btax_params_df, iit_refdict)
        basedata = basedata.merge(right=results_oneyear, how='outer', on='Asset')
    basedata.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
    return basedata

def inv_response(btax_refdict, iit_refdict, elast_c, elast_nc):
    maindata = pd.read_csv('mini_assets.csv')
    maindata.drop(['assets_c', 'assets_nc'], axis=1, inplace=True)
    maindata['deltaIc2014'] = 0.
    maindata['deltaInc2014'] = 0.
    maindata['deltaEc2014'] = 0.
    maindata['deltaEnc2014'] = 0.
    maindata['deltaIc2015'] = 0.
    maindata['deltaInc2015'] = 0.
    maindata['deltaEc2015'] = 0.
    maindata['deltaEnc2015'] = 0.
    maindata['deltaIc2016'] = 0.
    maindata['deltaInc2016'] = 0.
    maindata['deltaEc2016'] = 0.
    maindata['deltaEnc2016'] = 0.
    results_base = run_btax_mini(range(2017,2028), {}, {})
    results_ref = run_btax_mini(range(2017,2028), btax_refdict, iit_refdict)
    for year in range(2017, 2028):
        maindata['deltaIc' + str(year)] = (results_ref['u_c'] / results_base['u_c'] - 1) * elast_c
        maindata['deltaInc' + str(year)] = (results_ref['u_nc'] / results_base['u_nc'] - 1) * elast_nc
        maindata['deltaEc' + str(year)] = (results_ref['u_c'] + results_base['u_c']) / 2.0
        maindata['deltaEnc' + str(year)] = (results_ref['u_nc'] + results_base['u_nc']) / 2.0
    return maindata

