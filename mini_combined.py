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

def calc_F(f, i, fracded, a, b):
    F = f * i * fracded * np.exp(-i * a) * (1 - np.exp(-i * (b - a)))
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
    Flist = np.asarray(calc_Flist(f, rd+pi, fracded, length))
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
    Flist = np.asarray(calc_Flist(f, rd+pi, fracded, length))
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
        tdict = {'0': btax_params['tau_c'][start_year-2017]}
        for i in range(start_year - 2016, len(btax_params['year'])):
            if btax_params['tau_c'][i] != btax_params['tau_c'][i-1]:
                tdict[str(i - (start_year-2017))] = btax_params['tau_c'][i]
    return tdict

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


"""
Code to run btax-mini
"""

def build_prelim_oneyear(year, econ_params, btax_params, iitref):
    assert year in range(2017, 2028)
    [r_c, r_nc, r_d, pi, f_c, f_nc] = get_econ_params_oneyear(econ_params, year)
    taxdep = get_btax_params_oneyear(btax_params, year)
    tdict_c = make_tdict_c(btax_params, year)
    tdict_nc = make_tdict_nc(iitref, year)
    asset_data = copy.deepcopy(assets_data)
    main_data = asset_data.merge(right=taxdep, how='outer', on='Asset')
    main_data['uc_c'] = 0.
    #main_data['eatr_c'] = 0.
    main_data['uc_nc'] = 0.
    #main_data['eatr_nc'] = 0.
    for j in range(len(main_data)):
        main_data['uc_c'][j] = calc_usercost(r_c, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_c, r_d, 1-int_hc_c, tdict_c, 100)
        main_data['uc_nc'][j] = calc_usercost(r_nc, pi, main_data['delta'][j], main_data['Method'][j], main_data['L'][j], main_data['bonus'][j], f_nc, r_d, 1-int_hc_nc, tdict_nc, 100)
    main_data['u_c'][main_data['Asset'] == 'Inventories'] = calc_rho_inv(r_c, pi, inv_method, 0.5, tdict_c)
    main_data['u_nc'][main_data['Asset'] == 'Inventories'] = calc_rho_inv(r_nc, pi, inv_method, 0.5, tdict_nc)
    main_data.drop(['assets_c', 'assets_nc', 'L', 'Method', 'bonus'], axis=1, inplace=True)
    return main_data

def run_btax_mini(yearlist, btax_refdict, iit_refdict):
    btax_params_df = update_btax_params(btax_refdict)
    econ_params_df = copy.deepcopy(econ_defaults)
    basedata = copy.deepcopy(assets_data)
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

