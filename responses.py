# behavioral_responses
######################################################################

def test_elast_dict():
    # check that all necessary terms included or defined
    try:
        elast_dict
    except NameError:
        print "Elasticity dictionary undefined"
    else:
        for key in ['inv_usercost_c', 'inv_usercost_nc', 'inv_eatr_c',
                    'inv_eatr_nc', 'mne_share_c', 'mne_share_nc',
                    'debt_taxshield_c', 'debt_taxshield_nc', 'legalform_ratediff']:
            assert key in elast_dict
    # test that values are correct
    assert elast_dict['inv_usercost_c'] <= 0.0
    assert elast_dict['inv_usercost_nc'] <= 0.0
    assert elast_dict['inv_eatr_c'] <= 0.0
    assert elast_dict['inv_eatr_nc'] <= 0.0
    assert elast_dict['mne_share_c'] >= 0.0
    assert elast_dict['mne_share_c'] <= 1.0
    assert elast_dict['mne_share_nc'] >= 0.0
    assert elast_dict['mne_share_nc'] <= 1.0
    assert elast_dict['debt_taxshield_c'] >= 0.0
    assert elast_dict['debt_taxshield_nc'] >= 0.0
    assert elast_dict['legalform_ratediff'] <= 0.0
test_elast_dict()

def buildNewInvMatrix(response_data):
    # Create new investment matrices for corporate and noncorporate
    inv_mat_base_corp = build_inv_matrix()
    inv_mat_base_noncorp = build_inv_matrix(False)
    inv_mat_ref_corp = build_inv_matrix()
    inv_mat_ref_noncorp = build_inv_matrix(False)
    for i in range(96):
        for j in range(57, 68):
            inv_mat_ref_corp[i, j] = inv_mat_base_corp[i, j] * (1 + response_results['deltaIc' + str(j + 1960)].tolist()[i])
            inv_mat_ref_noncorp[i, j] = inv_mat_base_noncorp[i, j] * (1 + response_results['deltaInc' + str(j + 1960)].tolist()[i])
    return (inv_mat_ref_corp, inv_mat_ref_noncorp)

def earningsResponse(response_data, corp_noncorp=True):
    if corp_noncorp:
        Kstock_base = copy.deepcopy(Kstock_base_corp)
        Kstock_ref = copy.deepcopy(Kstock_ref_corp)
    else:
        Kstock_base = copy.deepcopy(Kstock_base_noncorp)
        Kstock_ref = copy.deepcopy(Kstock_ref_noncorp)
    changeEarnings = np.zeros((96, 14))
    for i in range(96):
        for j in range(14):
            if corp_noncorp:
                changeEarnings[i, j] = (Kstock_ref[i, j] - Kstock_base[i, j]) * np.asarray(response_data['MPKc' + str(j + 2014)])[i] * adjfactor_dep_corp
            else:
                changeEarnings[i, j] = (Kstock_ref[i, j] - Kstock_base[i, j]) * np.asarray(response_data['MPKnc' + str(j + 2014)])[i] * adjfactor_dep_noncorp
    newEarnings_total = np.zeros(14)
    for j in range(14):
        newEarnings_total[j] = changeEarnings[:, j].sum()
    earnings_results = pd.DataFrame({'year': range(2014, 2028),
                                     'deltaE': newEarnings_total})
    return earnings_results

def NID_response(capital_path, eta=0.4, id_hc_year=9e99, nid_hc_year=9e99,
                 id_hc_old=0, id_hc_new=0, nid_hc=0):
    """
    Calculates the debt, net interest deduction and interest paid
    for corporations under the reform.
    Includes the change in debt due to a change in the capital stock.
    If nonzero corporate debt elasticity, also includes a behavioral response.
    Parameters:
        capital_path: growth path of the corporate capital stock
        eta: retirement rate of existing debt
        nid_hc: haircut on the net interest deduction, beginning in nid_hc_year
        id_hc_old, id_hc_new: haircuts on the deduction of interest paid
                              on debt originated before id_hc_year (old) and
                              on debt originated beginning in id_hc_year (new)
    """
    elast_debt = elast_dict['debt_taxshield_c']
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_corp['Kfa'][:57].tolist()
    A = debt_data_corp['A'][:57].tolist()
    L = debt_data_corp['L'][:57].tolist()
    D = [L[i] - A[i] for i in range(len(L))]
    i_t = debt_data_corp['i_t'].tolist()
    i_pr = debt_data_corp['i_pr'].tolist()
    for i in range(57, 68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        A.append(A[56] * K_fa[i] / K_fa[56])
        D.append(D[56] * K_fa[i] / K_fa[56])
        L.append(D[i] + A[i])
    # Apply debt response
    hclist = np.zeros(14)
    for i in range(14):
        if i + 2014 >= nid_hc_year:
            hc1 = nid_hc
        if i + 2014 >= id_hc_year:
            hc2 = id_hc_new
        hclist[i] = max(hc1, hc2)
    taxshield_base = btax_defaults['tau_c']
    taxshield_ref = np.asarray(btax_params_reform['tau_c']) * (1 - hclist)
    pctchg_delta = elast_debt * (taxshield_ref / taxshield_base - 1)
    D_opt = copy.deepcopy(D)
    L_opt = copy.deepcopy(L)
    for i in range(len(D)):
        if i + 1960 >= nid_hc_year or i + 1960 >= id_hc_year:
            if i < 54:
                D_opt[i] = D[i]
            else:
                D_opt[i] = D[i] * (1 + pctchg_delta[i-54])
            L_opt[i] = D_opt[i] + A[i]
    R = np.zeros(68)
    O = np.zeros(68)
    L2 = copy.deepcopy(L)
    for i in range(1, 68):
        R[i] = L2[i-1] * eta
        O[i] = max(L_opt[i] - L2[i-1] * (1 - eta), 0)
        L2[i] = L2[i-1] - R[i] + O[i]
    i_a = [x / 100. for x in i_t]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_income = [A[i] * i_a[i] for i in range(len(A))]
    int_expense = np.zeros(68)
    for i in range(1, 68):
        for j in range(i+1):
            if j + 1960 < id_hc_year and i + 1960 >= id_hc_year:
                int_expense[i] += (O[j] * (1 - eta)**(i - j - 1) *
                                   i_l[j] * (1 - id_hc_old))
            elif j + 1960 >= id_hc_year:
                int_expense[i] += (O[j] * (1 - eta)**(i - j - 1) *
                                   i_l[j] * (1 - id_hc_new))
            else:
                int_expense[i] += O[j] * (1 - eta)**(i - j - 1) * i_l[j]
    NID_gross = int_expense - int_income
    NID = np.zeros(len(NID_gross))
    NIP = NID_gross * adjfactor_int_corp
    for i in range(len(NID)):
        if i + 1960 < nid_hc_year:
            NID[i] = NID_gross[i] * adjfactor_int_corp
        else:
            NID[i] = NID_gross[i] * adjfactor_int_corp * (1 - nid_hc)
    debt = np.asarray(L2) * adjfactor_int_corp
    NID_results = pd.DataFrame({'year': range(2014, 2028), 'nid': NID[54:68],
                                'nip': NIP[54:68], 'debt': debt[54:68]})
    return NID_results

def noncorpIntDeduction_response(capital_path, eta=0.4,
                                 id_hc_year=9e99, id_hc_old=0, id_hc_new=0):
    """
    Calculates the debt, interest deduction and interest paid
    for noncorporate businesses under the reform.
    Includes the change in debt due to a change in the capital stock.
    If nonzero noncorporate debt elasticity, also includes behavioral response.
    Parameters:
        capital_path: growth path of the noncorporate capital stock
        eta: retirement rate of existing debt
        id_hc_old, id_hc_new: haircuts on the deduction of interest paid
                              on debt originated before id_hc_year (old) and
                              on debt originated beginning in id_hc_year (new)
    """
    elast_debt = elast_dict['debt_taxshield_nc']
    Kstock2016 = capital_path['Kstock'][2]
    K_fa = debt_data_noncorp['Kfa'][:57].tolist()
    L = debt_data_noncorp['L'][:57].tolist()
    i_t = debt_data_noncorp['i_t'].tolist()
    i_pr = debt_data_noncorp['i_pr'].tolist()
    for i in range(57, 68):
        K_fa.append(K_fa[56] * capital_path['Kstock'][i-54] / Kstock2016)
        L.append(L[56] * K_fa[i] / K_fa[56])
    # Apply debt response
    hclist = np.zeros(14)
    for i in range(14):
        if i + 2014 >= id_hc_year:
            hclist[i] = id_hc_year
    taxshield_base = btax_defaults['tau_nc']
    taxshield_ref = btax_params_reform['tau_nc'] * (1 - hclist)
    pctchg_delta = (taxshield_ref / taxshield_base - 1) * elast_debt
    L_opt = copy.deepcopy(L)
    for i in range(len(L)):
        if i + 1960 >= id_hc_year:
            if i < 54:
                L_opt[i] = L[i]
            else:
                L_opt[i] = L[i] * (1 - pctchg_delta[i-54])
    R = np.zeros(68)
    O = np.zeros(68)
    L2 = copy.deepcopy(L)
    for i in range(1, 68):
        R[i] = L2[i-1] * eta
        O[i] = max(L_opt[i] - L2[i-1] * (1 - eta), 0)
        L2[i] = L2[i-1] - R[i] + O[i]
    i_l = [(i_t[i] + i_pr[i]) / 100. for i in range(len(i_t))]
    int_paid = np.zeros(68)
    int_deducted = np.zeros(68)
    for i in range(1, 68):
        for j in range(i+1):
            int_paid[i] += (O[j] * (1 - eta)**(i - j - 1) *
                            i_l[j] * adjfactor_int_noncorp)
            if j + 1960 < id_hc_year and i + 1960 >= id_hc_year:
                int_deducted[i] += (O[j] * (1 - eta)**(i - j - 1) * i_l[j] *
                                    (1 - id_hc_old) * adjfactor_int_noncorp)
            elif j + 1960 >= id_hc_year:
                int_deducted[i] += (O[j] * (1 - eta)**(i - j - 1) * i_l[j] *
                                    (1 - id_hc_new) * adjfactor_int_noncorp)
            else:
                int_deducted[i] += (O[j] * (1 - eta)**(i - j - 1) *
                                    i_l[j] * adjfactor_int_noncorp)
    debt = np.asarray(L2) * adjfactor_int_noncorp
    ID_results = pd.DataFrame({'year': range(2014, 2028),
                               'intDed': int_deducted[54:68],
                               'intpaid': int_paid[54:68],
                               'debt': debt[54:68]})
    return ID_results

def legal_response(firstyear):
    """
    Reallocation of business activity between corporate and noncorporate
    sections, achieved by modifying the rescaling factors. For now,
    assuming identical tax bases.
    firstyear: first year when this takes effect
    """
    assert firstyear in range(2017, 2028)
    elast = elast_dict['legalform_ratediff']
    tau_nc_base = btax_defaults['tau_nc'][firstyear-2014:]
    tau_c_base = btax_defaults['tau_c'][firstyear-2014:]
    tau_nc_ref = btax_params_reform['tau_nc'][firstyear-2014:]
    tau_c_ref = btax_params_reform['tau_c'][firstyear-2014:]
    tau_e_base = get_mtr_e_list({})[firstyear-2017:]
    tau_e_ref = get_mtr_e_list(iit_params_ref)[firstyear-2017:]
    taxterm_base = (tau_c_base + tau_e_base - tau_c_base * tau_e_base -
                    tau_nc_base)
    taxterm_ref = tau_c_ref + tau_e_ref - tau_c_ref * tau_e_ref - tau_nc_ref
    legalshift = elast * (taxterm_ref - taxterm_base)
    # business activity shares
    earnings_c = combined_base['ebitda'][firstyear-2014:]
    earnings_nc = earnings_base['ebitda'][firstyear-2014:]
    assets_c = capPath_base_corp['Kstock'][firstyear-2014:]
    assets_nc = capPath_base_noncorp['Kstock'][firstyear-2014:]
    debt_c = NID_base['debt'][firstyear-2014:]
    debt_nc = IntPaid_base_noncorp['debt'][firstyear-2014:]
    cshare_earnings = earnings_c / (earnings_c + earnings_nc)
    cshare_assets = assets_c / (assets_c + assets_nc)
    cshare_debt = debt_c / (debt_c + debt_nc)
    cshare_base = (cshare_earnings + cshare_assets + cshare_debt) / 3.0
    cshare_ref = cshare_base + legalshift
    scale_c = cshare_ref / cshare_base
    scale_nc = (1 - cshare_ref) / (1 - cshare_base)
    rescale_corp[firstyear-2014:] = scale_c
    rescale_noncorp[firstyear-2014:] = scale_nc
