import copy
import numpy as np
import pandas as pd
from data_sources import assets_data, econ_depr_df, taxdep_info_gross


def ccr_data():
    """
    Constructs the main CCR dataset used.
    Returns a DataFrame with:
        each asset type,
        corporate stock of each asset type,
        noncorporate stock of each asset type,
        true depreciation rate.
    """
    btax_data = copy.deepcopy(assets_data())
    ccrdata = btax_data.merge(right=econ_depr_df(), how='outer', on='Asset')
    return ccrdata


base_data = ccr_data()
sec179_rate_corp = 0.016687178
bonus_takeup_rate_corp = 0.60290131
sec179_rate_noncorp = 0.17299506
bonus_takeup_rate_noncorp = 0.453683778
LIVES = [3, 5, 7, 10, 15, 20, 25, 27.5, 39]


def taxdep_final(depr_methods, depr_bonuses,
                 reclassify_gds_life, reclassify_ads_life):
    """
    Constructs the DataFrame of information for tax depreciation.
    Only relevant for years beginning with 2014.
    Returns a DataFrame with:
        depreciation method,
        tax depreciation life,
        true depreciation rate,
        bonus depreciation rate.
    """
    taxdep = copy.deepcopy(taxdep_info_gross())
    system = np.empty(len(taxdep), dtype='S10')
    class_life = np.asarray(taxdep['GDS Class Life'])
    # Determine depreciation systems for each asset type
    for cl, method in depr_methods.items():
        system[class_life == cl] = method
    # Determine asset lives to use under any reclassification
    L_gds = np.asarray(taxdep['L_gds'])
    L_ads = np.asarray(taxdep['L_ads'])
    for (L, reclassify) in [(L_gds, reclassify_gds_life),
                            (L_ads, reclassify_ads_life)]:
        for life in reclassify:
            L = np.where(L == life, reclassify[life], L)
    Llist = L_gds
    Llist[system == 'ADS'] = L_ads[system == 'ADS']
    Llist[system == 'None'] = 100
    taxdep['L'] = Llist

    # Determine depreciation method. Default is GDS method
    method = np.asarray(taxdep['Method'])
    method[system == 'ADS'] = 'SL'
    method[system == 'Economic'] = 'Economic'
    method[system == 'None'] = 'None'
    taxdep['Method'] = method

    # Detemine bonus depreciation rate
    bonus = np.zeros(len(taxdep))
    for cl, cl_bonus in depr_bonuses.items():
        bonus[class_life == cl] = cl_bonus
    taxdep['bonus'] = bonus
    taxdep.drop(['L_gds', 'L_ads', 'GDS Class Life'], axis=1, inplace=True)
    return taxdep


def taxdep_preset(year):
    """
    Constructs the DataFrame of information for tax depreciation.
    Only relevant for years before 2014.
    Returns a DataFrame with:
        depreciation method,
        tax depreciation life,
        true depreciation rate,
        bonus depreciation rate.
    """
    taxdep = copy.deepcopy(taxdep_info_gross())
    taxdep['L'] = taxdep['L_gds']
    class_life = np.asarray(taxdep['GDS Class Life'])
    bonus = np.zeros(len(class_life))
    for y in LIVES:
        s = "bonus{}".format(y if y != 27.5 else 27)
        bonus[class_life == y] = bonus_data[s][year - 1960]
    taxdep['bonus'] = bonus
    taxdep.drop(['L_gds', 'L_ads', 'GDS Class Life'], axis=1, inplace=True)
    return taxdep


def get_btax_params_oneyear(btax_params, other_params, year):
    """
    Extracts tax depreciation parameters and
    calls the functions to build the tax depreciation
    DataFrames.
    """
    if year >= 2014:
        year = min(year, 2027)
        depr_methods = {}
        depr_bonuses = {}
        for y in LIVES:
            s = "depr_{}yr_".format(y if y != 27.5 else 275)
            depr_methods[y] = btax_params[s + 'method'][year - 2014]
            depr_bonuses[y] = btax_params[s + 'bonus'][year - 2014]
        # figure out reclassification of tax lives
        gds_year = list(other_params['reclassify_taxdep_gdslife'])[0]
        ads_year = list(other_params['reclassify_taxdep_adslife'])[0]
        if gds_year <= year:
            reclass_gds = other_params['reclassify_taxdep_gdslife'][gds_year]
        else:
            reclass_gds = {}
        if ads_year <= year:
            reclass_ads = other_params['reclassify_taxdep_adslife'][ads_year]
        else:
            reclass_ads = {}
        taxdep = taxdep_final(depr_methods, depr_bonuses,
                              reclass_gds, reclass_ads)
    else:
        taxdep = taxdep_preset(year)
    return taxdep


# longer functions to use
def depreciationDeduction(year_investment, year_deduction, method, L,
                          delta, bonus):
    """
    Computes the nominal depreciation deduction taken on any
    unit investment in any year with any depreciation method and life.
    Parameters:
        year_investment: year the investment is made
        year_deduction: year the CCR deduction is taken
        method: method of CCR (DB 200%, DB 150%, SL, Expensing, None)
        L: class life for DB or SL depreciation (MACRS)
        delta: economic depreciation rate
        bonus: bonus depreciation rate
    """
    assert method in ['DB 200%', 'DB 150%', 'SL', 'Expensing', 'Economic',
                      'None']
    # No depreciation
    if method == 'None':
        deduction = 0
    # Expensing
    elif method == 'Expensing':
        if year_deduction == year_investment:
            deduction = 1.0
        else:
            deduction = 0
    # Economic depreciation
    elif method == 'Economic':
        pi_temp = (investmentGfactors_data['pce'][year_deduction + 1] /
                   investmentGfactors_data['pce'][year_deduction])
        if pi_temp == np.exp(delta):
            annual_change = 1.0
        else:
            if year_deduction == year_investment:
                annual_change = (((pi_temp * np.exp(delta / 2)) ** 0.5 - 1) /
                                 (np.log(pi_temp - delta)))
            else:
                annual_change = ((pi_temp * np.exp(delta) - 1) /
                                 (np.log(pi_temp) - delta))

        if year_deduction < year_investment:
            sval = 0
            deduction = 0
        elif year_deduction == year_investment:
            sval = 1.0
            deduction = bonus + (1 - bonus) * delta * sval * annual_change
        else:
            sval = (np.exp(-delta * (year_deduction - year_investment)) *
                    investmentGfactors_data['pce'][year_deduction] / 2.0 /
                    (investmentGfactors_data['pce'][year_investment] +
                     investmentGfactors_data['pce'][year_investment + 1]))
            deduction = (1 - bonus) * delta * sval * annual_change
    else:
        if method == 'DB 200%':
            N = 2
        elif method == 'DB 150%':
            N = 1.5
        elif method == 'SL':
            N = 1

    # DB or SL depreciation, half-year convention
        t0 = year_investment + 0.5
        t1 = t0 + L * (1 - 1 / N)
        s1 = year_deduction
        s2 = s1 + 1
        if year_deduction < year_investment:
            deduction = 0
        elif year_deduction > year_investment + L:
            deduction = 0
        elif year_deduction == year_investment:
            deduction = bonus + (1 - bonus) * (1 - np.exp(-N / L * 0.5))
        elif s2 <= t1:
            deduction = ((1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                        np.exp(-N / L * (s2 - t0))))
        elif s1 >= t1 and s1 <= t0 + L and s2 > t0 + L:
            deduction = (1 - bonus) * (N / L * np.exp(1 - N) * (s2 - s1) * 0.5)
        elif s1 >= t1 and s2 <= t0 + L:
            deduction = (1 - bonus) * (N / L * np.exp(1 - N) * (s2 - s1))
        elif s1 < t1 and s2 > t1:
            deduction = ((1 - bonus) * (np.exp(-N / L * (s1 - t0)) -
                                        np.exp(-N / L * (t1 - t0)) +
                                        N / L * np.exp(1 - N) * (s2 - t1)))
    return deduction


def build_inv_matrix(corp=True):
    """
    Builds a matrix of investment by asset type by year
    corp: indicator for corporate or noncorporate investment
    Returns 96x75 invesment matrix (96 assets, years 1960-2034)
    """
    inv_mat1 = np.zeros((96, 75))
    # build historical portion
    for j in range(57):
        if corp:
            inv_mat1[:, j] = (investmentrate_data['i' + str(j + 1960)] *
                              investmentshare_data['c_share'][j])
        else:
            inv_mat1[:, j] = (investmentrate_data['i' + str(j + 1960)] *
                              (1 - investmentshare_data['c_share'][j]))
    # Extend investment using NGDP (growth factors from CBO forecast)
    for j in range(57, 75):
        inv_mat1[:, j] = (inv_mat1[:, 56] *
                          investmentGfactors_data['ngdp'][j] /
                          investmentGfactors_data['ngdp'][56])
    # Rescale investment to match investment based on B-Tax for 2017
    if corp:
        inv2017 = np.asarray(base_data['assets_c'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    else:
        inv2017 = np.asarray(base_data['assets_nc'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    inv_mat2 = np.zeros((96, 75))
    l1 = list(range(96))
    l1.remove(32)  # exclude land
    for j in range(75):
        for i in l1:
            inv_mat2[i, j] = inv_mat1[i, j] * inv2017[i] / inv_mat1[i, 57]
    return inv_mat2


def buildDepreciationArray(investment_matrix, corp=True):
    if corp:
        bonus_adj = bonus_takeup_rate_corp
        sec179_adj = sec179_rate_corp
    else:
        bonus_adj = bonus_takeup_rate_noncorp
        sec179_adj = sec179_rate_noncorp
    Dep_arr = np.zeros((96, 75, 75))
    for j in range(75):
        taxdepinfo = get_btax_params_oneyear(btax_defaults,
                                             brc_defaults_other, j + 1960)
        for i in range(96):
            for k in range(j, 75):
                bonus1 = min(taxdepinfo['bonus'][i] * bonus_adj + sec179_adj,
                             1.0)
                Dep_arr[i, j, k] = (depreciationDeduction(
                                        j, k, taxdepinfo['Method'][i],
                                        taxdepinfo['L'][i],
                                        taxdepinfo['delta'][i],
                                        bonus1) *
                                    investment_matrix[i, j])
    return Dep_arr


def calcDepAdjustment(corp=True):
    """
    Calculates the adjustment factor for assets, depreciation and investment
    corp: indicator for whether corporate or noncorporate data
    """
    investment_matrix = build_inv_matrix(corp)
    Dep_arr = buildDepreciationArray(investment_matrix, corp)
    totalAnnualDepreciation = np.zeros(75)
    for k in range(75):
        totalAnnualDepreciation[k] = Dep_arr[:, :, k].sum().sum()
    depreciation_data = copy.deepcopy(depreciationIRS_data)
    depreciation_data['dep_model'] = totalAnnualDepreciation[40:54]
    if corp:
        depreciation_data['scale'] = (depreciation_data['dep_Ccorp'] /
                                      depreciation_data['dep_model'])
    else:
        depreciation_data['scale'] = ((depreciation_data['dep_Scorp'] +
                                       depreciation_data['dep_sp'] +
                                       depreciation_data['dep_partner']) /
                                      depreciation_data['dep_model'])
    adj_factor = (sum(depreciation_data['scale']) /
                  len(depreciation_data['scale']))
    return adj_factor


def annualCCRdeduction(investment_matrix, btax_params, other_params,
                       adj_factor, hc_undep=0., hc_undep_year=0,
                       corp=True):
    """
    Calculates the annual depreciation deduction for each year 1960-2034
    investment_matrix: the matrix of investment (by asset and year)
    btax_params: DataFrame of business tax policies for each year
    hc_undep: haircut on depreciation deductions taken
              after hc_undep_year on investments made before hc_undep_year
    """
    Dep_arr = buildDepreciationArray(investment_matrix, corp)
    for j in range(75):
        for k in range(75):
            if j + 1960 < hc_undep_year and k + 1960 >= hc_undep_year:
                Dep_arr[:, j, k] = Dep_arr[:, j, k] * (1 - hc_undep)
    totalAnnualDeduction = np.zeros(75)
    for k in range(75):
        totalAnnualDeduction[k] = (Dep_arr[:, :, k].sum().sum() *
                                   adj_factor)
    return totalAnnualDeduction


def capitalPath(investment_mat, depDeduction_vec,
                corp=True):
    """
    Computes the all information on the capital stock for 2014-2027
    Returns two DataFrames:
        cap_result: DataFrame of certain measures by year, including
            stock of assets
            stock of fixed assets (excluding land and inventories)
            amount of fixed assets
            amount of net investment
            amount of net fixed investment
            amount of tax depreciation deductions taken
            amount of true depreciation occurring
        Kstock: DataFrame of amount of each asset type in each year
    Note: MdepTotal does not require the adjustment factor, as that was applied
          when computing the depreciation deductions taken.
    """
    # Select scaling factors to use depending on corporate or noncorporate run
    if corp:
        adj_factor = adjfactor_dep_corp
        rescalar = rescale_corp
    else:
        adj_factor = adjfactor_dep_noncorp
        rescalar = rescale_noncorp
    Kstock = np.zeros((96, 15))
    trueDep = np.zeros((96, 14))
    pcelist = np.asarray(investmentGfactors_data['pce'])
    deltalist = np.asarray(base_data['delta'])
    for i in range(96):
        # Starting by assigning 2017 data from B-Tax
        if corp:
            Kstock[i, 3] = np.asarray(base_data['assets_c'])[i]
        else:
            Kstock[i, 3] = np.asarray(base_data['assets_nc'])[i]
        # Using 2017 asset totals, apply retroactively
        for j in [56, 55, 54]:
            Kstock[i, j - 54] = ((Kstock[i, j - 53] * pcelist[j] /
                                  pcelist[j + 1] - investment_mat[i, j]) /
                                 (1 - deltalist[i]))
            trueDep[i, j - 54] = Kstock[i, j - 54] * deltalist[i]
        # Using 2017 asset totals, apply to future
        for j in range(57, 68):
            trueDep[i, j - 54] = Kstock[i, j - 54] * deltalist[i]
            Kstock[i, j - 53] = ((Kstock[i, j - 54] + investment_mat[i, j] -
                                  trueDep[i, j - 54]) *
                                 pcelist[j + 1] / pcelist[j])
    # Sum across assets and put into new dataset
    Kstock_total = np.zeros(14)
    fixedK_total = np.zeros(14)
    trueDep_total = np.zeros(14)
    inv_total = np.zeros(14)
    fixedInv_total = np.zeros(14)
    Mdep_total = np.zeros(14)
    for j in range(14):
        Kstock_total[j] = sum(Kstock[:, j]) * adj_factor * rescalar[j]
        fixedK_total[j] = ((sum(Kstock[:, j]) - Kstock[31, j] -
                            Kstock[32, j]) * adj_factor * rescalar[j])
        trueDep_total[j] = sum(trueDep[:, j]) * adj_factor * rescalar[j]
        inv_total[j] = (sum(investment_mat[:, j + 54]) *
                        adj_factor * rescalar[j])
        fixedInv_total[j] = ((sum(investment_mat[:, j + 54]) -
                             investment_mat[31, j + 54]) *
                             adj_factor * rescalar[j])
        Mdep_total[j] = depDeduction_vec[j + 54] * rescalar[j]
    cap_result = pd.DataFrame({'year': range(2014, 2028),
                               'Kstock': Kstock_total,
                               'Investment': inv_total,
                               'FixedInv': fixedInv_total,
                               'TrueDep': trueDep_total,
                               'taxDep': Mdep_total,
                               'FixedK': fixedK_total})
    return (cap_result, Kstock)
