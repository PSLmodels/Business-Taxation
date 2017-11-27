# construct base dataset
def ccr_data_v1():
    ModelDiffs = run_btax(False, True, 2017)
    btax_data = ModelDiffs[0]
    btax_data.drop(['ADS Life', 'Asset Type', 'GDS Life', 'System', 'asset_category',
                    'b', 'bea_asset_code', 'bonus', 'major_asset_group', 'metr_c',
                    'metr_c_d', 'metr_c_e', 'metr_nc', 'metr_nc_d', 'metr_nc_e',
                    'mettr_c', 'mettr_c_d', 'mettr_c_e', 'mettr_nc', 'mettr_nc_d',
                    'mettr_nc_e', 'rho_c', 'rho_c_d', 'rho_c_e', 
                    'rho_nc', 'rho_nc_d', 'rho_nc_e',
                    'z_c_d', 'z_c_e', 'z_nc_d', 'z_nc_e'], axis=1, inplace=True)
    btax_data.rename(columns={'GDS Class Life': 'L'}, inplace=True)
    btax_data.drop([3, 21, 32, 91], axis=0, inplace=True)
    ccrdata = btax_data.merge(right=df_econdepr, how='outer', on='Asset')
    ccrdata.drop([96,97,98], axis=0, inplace=True)
    return ccrdata
base_data = ccr_data_v1()

def ccr_data_v2(paramdict={}):
    execfile('mini_combined.py')
    btaxparams = update_btax_params(paramdict)
    
    

    
# longer functions to use
def depreciationDeduction(year_investment, year_deduction, method, L,
                          delta, bonusdata):
    # year_investment: year the investment is made
    # year_deduction: year the CCR deduction is taken
    # Method: Method of CCR (DB 200%, DB 150%, SL, Expensing)
    # L: class life for DB or SL depreciation (MACRS)
    # bonusdata: dataset of bonus depreciation rates by L and year_investment
    assert method in ['DB 200%', 'DB 150%', 'SL', 'Expensing', 'Economic']
    ##Extract bonus depreciation amount
    if L < 100:
        b = bonusdata['bonus' + str(int(L))][year_investment]
    else:
        b = 0
    # Expensing
    if method == 'Expensing':
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
            annual_change = ((pi_temp * np.exp(delta) - 1) /
                             (np.log(pi_temp) - delta))
        if year_deduction < year_investment:
            deduction = 0
        elif year_deduction == year_investment:
            deduction = b + (1 - b) * delta * annual_change
        else:
            deduction = (investmentGfactors_data['pce'][year_deduction] /
                         investmentGfactors_data['pce'][year_investment] *
                         np.exp(-delta * (year_deduction - year_investment)) *
                         delta * annual_change) * (1 - b)
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
            deduction = b + (1 - b) * (1 - np.exp(-N / L * 0.5))
        elif s2 <= t1:
            deduction = ((1 - b) * (np.exp(-N / L * (s1 - t0)) -
                                    np.exp(-N / L * (s2 - t0))))
        elif s1 >= t1 and s1 <= t0 + L and s2 > t0 + L:
            deduction = (1 - b) * (N / L * np.exp(1 - N) * (s2 - s1) * 0.5)
        elif s1 >= t1 and s2 <= t0 + L:
            deduction = (1 - b) * (N / L * np.exp(1 - N) * (s2 - s1))
        elif s1 < t1 and s2 > t1:
            deduction = ((1 - b) * (np.exp(-N / L * (s1 - t0)) -
                                    np.exp(-N / L * (t1 - t0)) +
                                    N / L * np.exp(1 - N) * (s2 - t1)))
        if L == 100:
            deduction = 0
    return(deduction)

def build_inv_matrix(corp_noncorp=True):
    # Function builds a matrix of investment by asset type by year
    # corp_noncorp: indicator for corporate or noncorporate investment
    # Returns 96x75 invesment matrix (96 assets, years 1960-2034)
    inv_mat1 = np.zeros((96,75))
    # build historical portion
    for j in range(57):
        if corp_noncorp:
            inv_mat1[:,j] = (investmentrate_data['i' + str(j + 1960)] *
                             investmentshare_data['c_share'][j])
        else:
            inv_mat1[:,j] = (investmentrate_data['i' + str(j + 1960)] *
                             (1 - investmentshare_data['c_share'][j]))
    # Extend investment using NGDP (growth factors from CBO forecast)
    for j in range(57,75):
        inv_mat1[:,j] = (inv_mat1[:,56] * investmentGfactors_data['ngdp'][j] /
                         investmentGfactors_data['ngdp'][56])
    # Rescale investment to match investment based on B-Tax for 2017
    if corp_noncorp:
        inv2017 = np.asarray(base_data['assets_c'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    else:
        inv2017 = np.asarray(base_data['assets_nc'] *
                             (investmentGfactors_data['ngdp'][57] /
                              investmentGfactors_data['ngdp'][56] - 1 +
                              base_data['delta']))
    inv_mat2 = np.zeros((96,75))
    l1 = range(96)
    l1.remove(32) # exclude land
    for j in range(75):
        for i in l1:
            inv_mat2[i,j] = inv_mat1[i,j] * inv2017[i] / inv_mat1[i, 57]
    return(inv_mat2)

def calcDepAdjustment(corp_noncorp=True):
    # corp_noncorp: indicator for whether corporate or noncorporate data
    investment_matrix = build_inv_matrix(corp_noncorp)
    Dep_arr = np.zeros((96,75,75))
    methodlist = np.asarray(base_data['Method'])
    Llist = np.asarray(base_data['L'])
    deltalist = np.asarray(base_data['delta'])
    for i in range(96): #asset
        for j in range(75): #year investment made
            for k in range(75): #year deduction taken
                Dep_arr[i,j,k] = (depreciationDeduction(j, k, methodlist[i],
                                                        Llist[i], deltalist[i],
                                                        bonus_data) *
                                  investment_matrix[i,j])
    totalAnnualDepreciation = np.zeros(75)
    for k in range(75):
        totalAnnualDepreciation[k] = Dep_arr[:,:,k].sum().sum()
    depreciation_data = copy.deepcopy(depreciationIRS_data)
    depreciation_data['dep_model'] = totalAnnualDepreciation[40:54]
    if corp_noncorp:
        depreciation_data['scale'] = (depreciation_data['dep_Ccorp'] /
                                      depreciation_data['dep_model'])
    else:
        depreciation_data['scale'] = ((depreciation_data['dep_Scorp'] +
                                       depreciation_data['dep_sp'] +
                                       depreciation_data['dep_partner']) /
                                      depreciation_data['dep_model'])
    adj_factor = (sum(depreciation_data['scale']) /
                  len(depreciation_data['scale']))
    return(adj_factor)
adjfactor_dep_corp = calcDepAdjustment()
adjfactor_dep_noncorp = calcDepAdjustment(False)


def annualCCRdeduction(investment_matrix, bonusdata, adj_factor,
                       hc_undep=0., hc_undep_year=0):
    # investment_matrix: the matrix of investment (by asset and year)
    # bonusdata: bonus depreciation data (by asset and year)
    # hc_undep: haircut on depreciation deductions taken
    #           after hc_under_year on investments made before hc_undep_year
    Dep_arr = np.zeros((96,75,75))
    methodlist =np.asarray(base_data['Method'])
    Llist = np.asarray(base_data['L'])
    deltalist = np.asarray(base_data['delta'])
    for i in range(96):
        for j in range(75):
            for k in range(75):
                Dep_arr[i,j,k] = (depreciationDeduction(j, k, methodlist[i],
                                                        Llist[i], deltalist[i],
                                                        bonusdata) *
                                  investment_matrix[i,j])
    for j in range(75):
        for k in range(75):
            if j + 1960 < hc_undep_year and k + 1960 >= hc_undep_year:
                Dep_arr[:,j,k] = Dep_arr[:,j,k] * (1 - hc_undep)
    totalAnnualDeduction = np.zeros(75)
    for k in range(75):
        totalAnnualDeduction[k] = (Dep_arr[:,:,k].sum().sum() *
                                   adjfactor_dep_corp)
    return totalAnnualDeduction

def capitalPath(investment_mat, depDeduction_vec, 
                corp_noncorp=True, economic=False):
    if corp_noncorp:
        adj_factor = adjfactor_dep_corp
    else:
        adj_factor = adjfactor_dep_noncorp
    Kstock = np.zeros((96,15))
    trueDep = np.zeros((96,14))
    pcelist = np.asarray(investmentGfactors_data['pce'])
    deltalist = np.asarray(base_data['delta'])
    for i in range(96):
        if corp_noncorp:
            Kstock[i,3] = np.asarray(base_data['assets_c'])[i]
        else:
            Kstock[i,3] = np.asarray(base_data['assets_nc'])[i]
        for j in [56,55,54]:
            Kstock[i,j-54] = ((Kstock[i,j-53] * pcelist[j] / pcelist[j+1] -
                               investment_mat[i,j]) / (1 - deltalist[i]))
            trueDep[i,j-54] = Kstock[i,j-54] * deltalist[i]
        for j in range(57,68):
            trueDep[i,j-54] = Kstock[i,j-54] * deltalist[i]
            Kstock[i,j-53] = ((Kstock[i,j-54] + investment_mat[i,j] -
                               trueDep[i,j-54]) *
                              pcelist[j+1] / pcelist[j])
    # Sum across assets and put into new dataset
    Kstock_total = np.zeros(14)
    fixedK_total = np.zeros(14)
    trueDep_total = np.zeros(14)
    inv_total = np.zeros(14)
    fixedInv_total = np.zeros(14)
    Mdep_total = np.zeros(14)
    for j in range(14):
        Kstock_total[j] = sum(Kstock[:,j]) * adj_factor
        fixedK_total[j] = ((sum(Kstock[:,j]) - Kstock[31,j] - Kstock[32,j]) *
                           adj_factor)
        trueDep_total[j] = sum(trueDep[:,j]) * adj_factor
        inv_total[j] = sum(investment_mat[:,j+54]) * adj_factor
        fixedInv_total[j] = (sum(investment_mat[:,j+54]) -
                             investment_mat[31,j+54]) * adj_factor
        Mdep_total[j] = depDeduction_vec[j+54]
    cap_result = pd.DataFrame({'year': range(2014,2028),
                               'Kstock': Kstock_total,
                               'Investment': inv_total,
                               'FixedInv': fixedInv_total,
                               'TrueDep': trueDep_total,
                               'taxDep': Mdep_total,
                               'FixedK': fixedK_total})
    if economic:
        taxDep_results = cap_result.drop(['Kstock', 'FixedK', 'Investment',
                                          'FixedInv', 'taxDep'], axis=1)
        taxDep_results.rename(columns={'TrueDep': 'taxDep'}, inplace=True)
    else:
        taxDep_results = cap_result.drop(['Kstock', 'FixedK', 'Investment',
                                          'FixedInv', 'TrueDep'], axis=1)
    return (cap_result, taxDep_results)

