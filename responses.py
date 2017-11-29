# behavioral_responses
######################################################################

def test_elast_dict():
    # check that all necessary terms included or defined
    try:
        elast_dict
    except NameError:
        print "Elasticity dictionary undefined"
    else:
        for key in ['inv_usercost_c', 'inv_usercost_nc', 'inv_eatr',
                    'debt_taxshield_c', 'debt_taxshield_nc', 'legalform_ratediff']:
            assert key in elast_dict
    # test that values are correct
    assert elast_dict['inv_usercost_c'] <= 0.0
    assert elast_dict['inv_usercost_nc'] <= 0.0
    assert elast_dict['inv_eatr'] <= 0.0
    assert elast_dict['debt_taxshield_c'] >= 0.0
    assert elast_dict['debt_taxshield_nc'] >= 0.0
    assert elast_dict['legalform_ratediff'] <= 0.0
test_elast_dict()

def investmentResponse(startyear):
    # Calculates investment response by asset type by year
    # Returns dataset of:
    #        percent change in investment by asset type, year and legal status
    #        change in earnings from a change in the capital stock, by asset, year and legal status
    assert startyear >= 2017
    elast_usercost_c = elast_dict['inv_usercost_c']
    elast_usercost_nc = elast_dict['inv_usercost_nc']
    elast_eatr = elast_dict['inv_eatr']
    combined_response = copy.deepcopy(base_data)
    combined_response.drop(['assets_c', 'assets_nc', 'delta'],
                           axis=1, inplace=True)
    for year in range(2014, 2028):
    	print "***** RUN " + str(year) + " *****"
        if year < startyear:
            combined_response['deltaIc' + str(year)] = 0
            combined_response['deltaEc' + str(year)] = 0
            combined_response['deltaInc' + str(year)] = 0
            combined_response['deltaEnc' + str(year)] = 0
        elif (elast_usercost_c == 0) and (elast_usercost_nc == 0) and (elast_eatr == 0):
            combined_response['deltaIc' + str(year)] = 0
            combined_response['deltaEc' + str(year)] = 0
            combined_response['deltaInc' + str(year)] = 0
            combined_response['deltaEnc' + str(year)] = 0
        else:
            ## Get results for the year
            BtaxBase = run_btax(False, False, min(year,2020), {}, btax_betr_corp=tau_base, btax_betr_entity_Switch=False, btax_betr_pass=0,
                                btax_depr_3yr_exp=bonus_data['bonus3'][year-1960] * 100.,
                                btax_depr_5yr_exp=bonus_data['bonus5'][year-1960] * 100.,
                                btax_depr_7yr_exp=bonus_data['bonus7'][year-1960] * 100.,
                                btax_depr_10yr_exp=bonus_data['bonus10'][year-1960] * 100.,
                                btax_depr_15yr_exp=bonus_data['bonus15'][year-1960] * 100.,
                                btax_depr_20yr_exp=bonus_data['bonus20'][year-1960] * 100.,
                                btax_depr_25yr_exp=bonus_data['bonus25'][year-1960] * 100.,
                                btax_depr_27_5yr_exp=bonus_data['bonus27'][year-1960] * 100.,
                                btax_depr_39yr_exp=bonus_data['bonus39'][year-1960] * 100.,
                                inventory_method=inventory_accounting, btax_depr_land_exp=bonusrate_land,
                                btax_other_hair=0, btax_other_corpeq=0, btax_other_invest=0, btax_other_proptx=0,
                                btax_depr_allyr_ads_Switch=False, btax_depr_allyr_exp=0, btax_depr_allyr_gds_Switch=True, btax_depr_allyr_tax_Switch=False,
                                btax_depr_hover_ads_Switch=False, btax_depr_hover_exp=0, btax_depr_hover_gds_Switch=True, btax_depr_hover_tax_Switch=False,
                                btax_depr_3yr_ads_Switch=False, btax_depr_3yr_gds_Switch=True, btax_depr_3yr_tax_Switch=False,
                                btax_depr_5yr_ads_Switch=False, btax_depr_5yr_gds_Switch=True, btax_depr_5yr_tax_Switch=False,
                                btax_depr_7yr_ads_Switch=False, btax_depr_7yr_gds_Switch=True, btax_depr_7yr_tax_Switch=False,
                                btax_depr_10yr_ads_Switch=False, btax_depr_10yr_gds_Switch=True, btax_depr_10yr_tax_Switch=False,
                                btax_depr_15yr_ads_Switch=False, btax_depr_15yr_gds_Switch=True, btax_depr_15yr_tax_Switch=False,
                                btax_depr_20yr_ads_Switch=False, btax_depr_20yr_gds_Switch=True, btax_depr_20yr_tax_Switch=False,
                                btax_depr_25yr_ads_Switch=False, btax_depr_25yr_gds_Switch=True, btax_depr_25yr_tax_Switch=False,
                                btax_depr_27_5yr_ads_Switch=False, btax_depr_27_5yr_gds_Switch=True, btax_depr_27_5yr_tax_Switch=False,
                                btax_depr_39yr_ads_Switch=False, btax_depr_39yr_gds_Switch=True, btax_depr_39yr_tax_Switch=False)
            BtaxRefm = run_btax(False, False, min(year,2020), {}, btax_betr_corp=tau_ref, btax_betr_entity_Switch=False, btax_betr_pass=0,
                                btax_depr_3yr_exp=bonus_data_ref['bonus3'][year-1960] * 100.,
                                btax_depr_5yr_exp=bonus_data_ref['bonus5'][year-1960] * 100.,
                                btax_depr_7yr_exp=bonus_data_ref['bonus7'][year-1960] * 100.,
                                btax_depr_10yr_exp=bonus_data_ref['bonus10'][year-1960] * 100.,
                                btax_depr_15yr_exp=bonus_data_ref['bonus15'][year-1960] * 100.,
                                btax_depr_20yr_exp=bonus_data_ref['bonus20'][year-1960] * 100.,
                                btax_depr_25yr_exp=bonus_data_ref['bonus25'][year-1960] * 100.,
                                btax_depr_27_5yr_exp=bonus_data_ref['bonus27'][year-1960] * 100.,
                                btax_depr_39yr_exp=bonus_data_ref['bonus39'][year-1960] * 100.,
                                inventory_method=inventory_accounting, btax_depr_land_exp=bonusrate_land,
                                btax_other_hair=int_hc, btax_other_corpeq=0, btax_other_invest=0, btax_other_proptx=0,
                                btax_depr_allyr_ads_Switch=False, btax_depr_allyr_exp=0, btax_depr_allyr_gds_Switch=True, btax_depr_allyr_tax_Switch=False,
                                btax_depr_hover_ads_Switch=False, btax_depr_hover_exp=0, btax_depr_hover_gds_Switch=True, btax_depr_hover_tax_Switch=False,
                                btax_depr_3yr_ads_Switch=False, btax_depr_3yr_gds_Switch=True, btax_depr_3yr_tax_Switch=False,
                                btax_depr_5yr_ads_Switch=False, btax_depr_5yr_gds_Switch=True, btax_depr_5yr_tax_Switch=False,
                                btax_depr_7yr_ads_Switch=False, btax_depr_7yr_gds_Switch=True, btax_depr_7yr_tax_Switch=False,
                                btax_depr_10yr_ads_Switch=False, btax_depr_10yr_gds_Switch=True, btax_depr_10yr_tax_Switch=False,
                                btax_depr_15yr_ads_Switch=False, btax_depr_15yr_gds_Switch=True, btax_depr_15yr_tax_Switch=False,
                                btax_depr_20yr_ads_Switch=False, btax_depr_20yr_gds_Switch=True, btax_depr_20yr_tax_Switch=False,
                                btax_depr_25yr_ads_Switch=False, btax_depr_25yr_gds_Switch=True, btax_depr_25yr_tax_Switch=False,
                                btax_depr_27_5yr_ads_Switch=False, btax_depr_27_5yr_gds_Switch=True, btax_depr_27_5yr_tax_Switch=False,
                                btax_depr_39yr_ads_Switch=False, btax_depr_39yr_gds_Switch=True, btax_depr_39yr_tax_Switch=False)
            df_base = BtaxBase[0]
            df_ref = BtaxRefm[0]
            ## Build main dataset
            df_base.drop(['ADS Life', 'Asset Type', 'GDS Class Life', 'GDS Life', 'Method', 'System', 'asset_category',
                          'b', 'bea_asset_code', 'bonus', 'major_asset_group', 'metr_c', 'metr_c_d', 'metr_c_e',
                          'metr_nc', 'metr_nc_d', 'metr_nc_e', 'mettr_c', 'mettr_c_d', 'mettr_c_e', 'mettr_nc', 'mettr_nc_d',
                          'mettr_nc_e', 'rho_c_d', 'rho_c_e', 'rho_nc_d', 'rho_nc_e', 'z_c_d', 'z_c_e',
                          'z_nc_d', 'z_nc_e'], axis=1, inplace=True)
            df_ref.drop(['ADS Life', 'Asset Type', 'GDS Class Life', 'GDS Life', 'Method', 'System', 'asset_category', 
                         'b', 'bea_asset_code', 'bonus', 'major_asset_group', 'metr_c', 'metr_c_d', 'metr_c_e',
                         'metr_nc', 'metr_nc_d', 'metr_nc_e', 'mettr_c', 'mettr_c_d', 'mettr_c_e', 'mettr_nc', 'mettr_nc_d',
                         'mettr_nc_e', 'rho_c_d', 'rho_c_e', 'rho_nc_d', 'rho_nc_e', 'z_c_d', 'z_c_e', 
                         'z_nc_d', 'z_nc_e', 'assets_c', 'assets_nc'], axis=1, inplace=True)
            df_base.rename(columns={'assets_c': 'K_c_base', 'rho_c': 'rho_c_base', 'z_c': 'z_c_base', 
                                    'assets_nc': 'K_nc_base', 'rho_nc': 'rho_nc_base', 'z_nc': 'z_nc_base'}, inplace=True)
            df_ref.rename(columns={'rho_c': 'rho_c_ref', 'z_c': 'z_c_ref', 'rho_nc': 'rho_nc_ref', 'z_nc': 'z_nc_ref'}, inplace=True)
            df_comb = df_base.merge(right=df_ref, how='outer', on='Asset')
            df_total = df_comb.merge(right=df_econdepr, how='outer', on='Asset')
            df_nocat = df_total.drop([3, 21, 32, 91, 100, 101, 102], axis=0)
            
            ## Apply marginal response using user cost of capital, to corporate and noncorporate
            df_nocat['usercost_c_base'] = df_nocat['rho_c_base'] + df_nocat['delta']
            df_nocat['usercost_c_ref'] = df_nocat['rho_c_ref'] + df_nocat['delta']
            df_nocat['deltaInv_c_m'] = ((df_nocat['usercost_c_ref'] / df_nocat['usercost_c_base']) - 1) * elast_usercost_c
            df_nocat['deltaE_c'] = (df_nocat['usercost_c_base'] + df_nocat['usercost_c_ref']) / 2.0
            df_nocat['usercost_nc_base'] = df_nocat['rho_nc_base'] + df_nocat['delta']
            df_nocat['usercost_nc_ref'] = df_nocat['rho_nc_ref'] + df_nocat['delta']
            df_nocat['deltaInv_nc'] = ((df_nocat['usercost_nc_ref'] / df_nocat['usercost_nc_base']) - 1) * elast_usercost_nc
            df_nocat['deltaE_nc'] = (df_nocat['usercost_nc_base'] + df_nocat['usercost_nc_ref']) / 2.0
            
            ## Apply nonmarginal response using EATR, to corporate only
            r = (1 - f) * E + f * (i_d - pi)
            F_base = f * tau_base
            F_ref = f * tau_ref * (1 - int_hc)

            df_nocat['Rstar'] = (p - r) / (r + df_nocat['delta'])
            df_nocat['P'] = p / (r + df_nocat['delta'])
            df_nocat['R_base'] = (-(1 - df_nocat['z_c_base'] * tau_base - F_base) +
                                  (p + df_nocat['delta']) * (1 - tau_base) / (r + df_nocat['delta']))
            df_nocat['R_ref'] = (-(1 - df_nocat['z_c_ref'] * tau_ref - F_ref) +
                                 (p + df_nocat['delta']) * (1 - tau_ref) / (r + df_nocat['delta']))
            df_nocat['EATR_base'] = (df_nocat['Rstar'] - df_nocat['R_base']) / df_nocat['P']
            df_nocat['EATR_ref'] = (df_nocat['Rstar'] - df_nocat['R_ref']) / df_nocat['P']
            df_nocat['deltaInv_c_nm'] = (df_nocat['EATR_ref'] - df_nocat['EATR_base']) * elast_eatr
            df_nocat['deltaInv_c'] = df_nocat['deltaInv_c_m'] + df_nocat['deltaInv_c_nm']
            df_deltaI = df_nocat.drop(['K_c_base', 'rho_c_base', 'z_c_base', 'rho_c_ref', 'z_c_ref', 
                                       'K_nc_base', 'rho_nc_base', 'z_nc_base', 'rho_nc_ref', 'z_nc_ref',
                                       'delta', 'usercost_c_base', 'usercost_c_ref', 'usercost_nc_base', 'usercost_nc_ref',
                                       'deltaInv_c_m', 'Rstar', 'P', 'R_base', 'R_ref', 'EATR_base', 'EATR_ref', 'deltaInv_c_nm'],
                                      axis=1)
            df_deltaI.rename(columns={'deltaInv_c': 'deltaIc' + str(year), 'deltaE_c': 'deltaEc' + str(year),
                                      'deltaInv_nc': 'deltaInc' + str(year), 'deltaE_nc': 'deltaEnc' + str(year)}, inplace=True)
            combined_response = combined_response.merge(right=df_deltaI, how='outer', on='Asset')
    for year in range(2021,2028):
        combined_response['deltaIc' + str(year)] = combined_response['deltaIc2020']
        combined_response['deltaEc' + str(year)] = combined_response['deltaEc2020']
        combined_response['deltaInc' + str(year)] = combined_response['deltaInc2020']
        combined_response['deltaEnc' + str(year)] = combined_response['deltaEnc2020']
    return combined_response

def buildNewInvMatrix(response_data, response_type='usercost'):
    ## Create new investment matrices for corporate and noncorporate
    assert response_type in ['usercost', 'eatr']
    if response_type == 'usercost':
        invbase = 'gross'
    else:
        invbase = 'net'
    inv_mat_base_corp = build_inv_matrix()
    inv_mat_base_noncorp = build_inv_matrix(False)
    inv_mat_ref_corp = build_inv_matrix()
    inv_mat_ref_noncorp = build_inv_matrix(False)
    data_main = copy.deepcopy(base_data)
    data_main.rename(columns={'assets_c': 'K_c_2017', 'assets_nc': 'K_nc_2017'}, inplace=True)
    for i in range(57,68):
        data_main['K_c_' + str(1961+i)] = ((data_main['K_c_' + str(1960+i)] * (1 - data_main['delta']) + 
                                            inv_mat_base_corp[:,i]) * investmentGfactors_data['pce'][i+1] / 
                                           investmentGfactors_data['pce'][i])
        data_main['Inv_c_' + str(1960+i)] = inv_mat_base_corp[:,i]
        data_main['NetInv_c_' + str(1960+i)] = data_main['Inv_c_' + str(1960+i)] - data_main['K_c_' + str(1960+i)] * data_main['delta']
        data_main['K_nc_' + str(1961+i)] = ((data_main['K_nc_' + str(1960+i)] * (1 - data_main['delta']) + 
                                             inv_mat_base_noncorp[:,i]) * investmentGfactors_data['pce'][i+1] / 
                                            investmentGfactors_data['pce'][i])
        data_main['Inv_nc_' + str(1960+i)] = inv_mat_base_noncorp[:,i]
        data_main['NetInv_nc_' + str(1960+i)] = data_main['Inv_nc_' + str(1960+i)] - data_main['K_nc_' + str(1960+i)] * data_main['delta']
        if invbase == 'gross':
            inv_mat_ref_corp[:,i] = inv_mat_base_corp[:,i] + data_main['Inv_c_' + str(1960+i)] * response_data['deltaIc' + str(1960+i)]
            inv_mat_ref_noncorp[:,i] = inv_mat_base_noncorp[:,i] + data_main['Inv_nc_' + str(1960+i)] * response_data['deltaInc' + str(1960+i)]
        else:
            inv_mat_ref_corp[:,i] = inv_mat_base_corp[:,i] + data_main['NetInv_c_' + str(1960+i)] * response_data['deltaIc' + str(1960+i)]
            inv_mat_ref_noncorp[:,i] = inv_mat_base_noncorp[:,i] + data_main['NetInv_nc_' + str(1960+i)] * response_data['deltaInc' + str(1960+i)]
    return (inv_mat_ref_corp, inv_mat_ref_noncorp)

def earningsResponse(response_data, corp_noncorp=True):
    # Create new investment matrix
    inv_base = build_inv_matrix(corp_noncorp)
    inv_ref = build_inv_matrix(corp_noncorp)
    for i in range(96):
        for j in range(57,68):
            if corp_noncorp:
                inv_ref[i,j] = inv_ref[i,j] * (1 + response_results['deltaIc' + str(j + 1960)].tolist()[i])
            else:
                inv_ref[i,j] = inv_ref[i,j] * (1 + response_results['deltaInc' + str(j + 1960)].tolist()[i])
    
    Kstock_base = np.zeros((96,15))
    Kstock_ref = np.zeros((96,15))
    for i in range(96):
        if corp_noncorp:
            Kstock_base[i,3] = np.asarray(base_data['assets_c'])[i]
            Kstock_ref[i,3] = np.asarray(base_data['assets_c'])[i]
        else:
            Kstock_base[i,3] = np.asarray(base_data['assets_nc'])[i]
            Kstock_ref[i,3] = np.asarray(base_data['assets_nc'])[i]
        for j in [56,55,54]:
            Kstock_base[i,j-54] = (Kstock_base[i,j-53] * investmentGfactors_data['pce'][j] / 
                                   investmentGfactors_data['pce'][j+1] - inv_base[i,j]) / (1 - np.asarray(base_data['delta'])[i])
            Kstock_ref[i,j-54] = (Kstock_ref[i,j-53] * investmentGfactors_data['pce'][j] / 
                                  investmentGfactors_data['pce'][j+1] - inv_ref[i,j]) / (1 - np.asarray(base_data['delta'])[i])
        for j in range(57,68):
            Kstock_base[i,j-53] = ((Kstock_base[i,j-54] * (1 - np.asarray(base_data['delta'])[i]) + inv_base[i,j]) * 
                                   investmentGfactors_data['pce'][j+1] / investmentGfactors_data['pce'][j])
            Kstock_ref[i,j-53] = ((Kstock_ref[i,j-54] * (1 - np.asarray(base_data['delta'])[i]) + inv_ref[i,j]) * 
                                  investmentGfactors_data['pce'][j+1] / investmentGfactors_data['pce'][j])
    changeEarnings = np.zeros((96,14))
    for i in range(96):
        for j in range(14):
            if corp_noncorp:
                changeEarnings[i,j] = (Kstock_ref[i,j] - Kstock_base[i,j]) * adjfactor_dep_corp * response_data['deltaEc' + str(j + 2014)][i]
            else:
                changeEarnings[i,j] = (Kstock_ref[i,j] - Kstock_base[i,j]) * adjfactor_dep_noncorp * response_data['deltaEnc' + str(j + 2014)][i]
    newEarnings_total = np.zeros(14)
    for j in range(14):
        newEarnings_total[j] = changeEarnings[:,j].sum()
    earnings_results = pd.DataFrame({'year': range(2014, 2028), 'deltaE': newEarnings_total})
    return earnings_results

def NID_response(capital_path, eta=0.4, id_hc_year=9e99, nid_hc_year=9e99, id_hc_old=0, id_hc_new=0, nid_hc_old=0, nid_hc=0):
    # capital_path: growth path of the capital stock
    # eta: retirement rate of existing debt
    # nid_hc: haircut on the net interest deduction, beginning in nid_hc_year
    # id_hc_old, id_hc_new: haircuts on the deduction of interest paid on debt originated before id_hc_year and on debt originated beginning in id_hc_year
    elast_debt = elast_dict['debt_taxshield_c']
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_corp['Kfa'][:57].tolist()
    A = debt_data_corp['A'][:57].tolist()
    L = debt_data_corp['L'][:57].tolist()
    D = [L[i] - A[i] for i in range(len(L))]
    i_t = debt_data_corp['i_t'].tolist()
    i_pr = debt_data_corp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        A.append(A[56] * K_fa[i] / K_fa[56])
        D.append(D[56] * K_fa[i] / K_fa[56])
        L.append(D[i] + A[i])
    ## Apply debt response
    taxshield_base = tau_base
    taxshield_ref = tau_ref * (1 - max(id_hc_new, nid_hc))
    pctchg_delta = elast_debt * (taxshield_ref / taxshield_base - 1)
    D_opt = copy.deepcopy(D)
    L_opt = copy.deepcopy(L)
    for i in range(len(D)):
        if i + 1960 >= nid_hc_year or i + 1960 >= id_hc_year:
            D_opt[i] = D[i] * (1 + pctchg_delta)
            L_opt[i] = D_opt[i] + A[i]
    R = np.zeros(68)
    O = np.zeros(68)
    L2 = copy.deepcopy(L)
    for i in range(1,68):
        R[i] = L2[i-1] * eta
        O[i] = max(L_opt[i] - L2[i-1] * (1 - eta), 0)
        L2[i] = L2[i-1] - R[i] + O[i]
        
    i_a = [x / 100. for x in i_t]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_income = [A[i] * i_a[i] for i in range(len(A))]
    int_expense = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            if j + 1960 < id_hc_year and i + 1960 >= id_hc_year:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_old)
            elif j + 1960 >= id_hc_year:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_new)
            else:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    NID_gross = int_expense - int_income
    NID = np.zeros(len(NID_gross))
    NIP = NID_gross * adjfactor_nid_corp
    for i in range(len(NID)):
        if i + 1960 < nid_hc_year:
            NID[i] = NID_gross[i] * adjfactor_nid_corp
        else:
            NID[i] = NID_gross[i] * adjfactor_nid_corp * (1 - nid_hc)
    NID_results = pd.DataFrame({'year': range(2014,2028), 'nid': NID[54:68]})
    NIP_results = pd.DataFrame({'year': range(2014,2028), 'nip': NIP[54:68]})
    return (NID_results, NIP_results)

def noncorpIntDeduction_response(capital_path, eta=0.4, id_hc_year=9e99, id_hc_old=0, id_hc_new=0):
    elast_debt = elast_dict['debt_taxshield_nc']
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_noncorp['Kfa'][:57].tolist()
    L = debt_data_noncorp['L'][:57].tolist()
    i_t = debt_data_noncorp['i_t'].tolist()
    i_pr = debt_data_noncorp['i_pr'].tolist()
    for i in range(57,68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        L.append(L[56] * K_fa[i] / K_fa[56])
    ##Apply debt response
    (tau_nc_base, tau_nc_ref) = calc_MTRs_nc(iit_params_ref, reform_start_year)
    taxshield_base = tau_nc_base
    taxshield_ref = tau_nc_ref * (1 - id_hc_new)
    pctchg_delta = (taxshield_ref / taxshield_base - 1) * elast_debt
    L_opt = copy.deepcopy(L)
    for i in range(len(L)):
        if i + 1960 >= id_hc_year:
            L_opt[i] = L[i] * (1 + pctchg_delta)
    R = np.zeros(68)
    O = np.zeros(68)
    L2 = copy.deepcopy(L)
    for i in range(1,68):
        R[i] = L2[i-1] * eta
        O[i] = max(L_opt[i] - L2[i-1] * (1 - eta), 0)
        L2[i] = L2[i-1] - R[i] + O[i]

    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_paid = np.zeros(68)
    int_deducted = np.zeros(68)
    for i in range(1,68):
        for j in range(i+1):
            int_paid[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * adjfactor_id_noncorp
            if j + 1960 < id_hc_year and i + 1960 >= id_hc_year:
                int_deducted[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_old) * adjfactor_id_noncorp
            elif j + 1960 >= id_hc_year:
                int_deducted[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * (1 - id_hc_new) * adjfactor_id_noncorp
            else:
                int_deducted[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j] * adjfactor_id_noncorp
    ID_results = pd.DataFrame({'year': range(2014,2028), 'intDed': int_deducted[54:68]})
    IP_results = pd.DataFrame({'year': range(2014,2028), 'intpaid': int_paid[54:68]})
    return (ID_results, IP_results)

