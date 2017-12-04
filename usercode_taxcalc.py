# Code to smoothly interface with taxcalc
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

def calc_MTRs_nc(param_dict, startyear):
    alpha_nc_ft = 0.763 # fully taxable share of noncorporate equity
    alpha_nc_td = 0.101 # share of noncorporate equity held in tax-deferred accounts
    alpha_nc_nt = 0.136 # nontaxable share of noncorporate equity
    calc_base = make_calculator({}, startyear)
    calc_ref = make_calculator(param_dict, startyear)
    mtr_soleprop_base = calc_base.mtr('e00900p')[2]
    mtr_soleprop_ref = calc_ref.mtr('e00900p')[2]
    mtr_partner_base = calc_base.mtr('e26270')[2]
    mtr_partner_ref = calc_ref.mtr('e26270')[2]
    mtr_otherSchE_base = calc_base.mtr('e02000')[2]
    mtr_otherSchE_ref = calc_ref.mtr('e02000')[2]
    mtr_taxdef_base = calc_base.mtr('e01700')[2]
    mtr_taxdef_ref = calc_ref.mtr('e01700')[2]
    posti_base = (calc_base.records.c04800 > 0.)
    posti_ref = (calc_ref.records.c04800 > 0.)
    tau_nc_taxable_base = ((((mtr_soleprop_base * np.abs(calc_base.records.e00900p)) +
                             (mtr_otherSchE_base * np.abs(calc_base.records.e02000 - calc_base.records.e26270)) +
                             (mtr_partner_base * np.abs(calc_base.records.e26270))) * calc_base.records.s006 * posti_base).sum() /
                           ((np.abs(calc_base.records.e00900p) + np.abs(calc_base.records.e02000-calc_base.records.e26270) +
                             np.abs(calc_base.records.e26270)) * calc_base.records.s006 * posti_base).sum())
    tau_nc_taxable_ref = ((((mtr_soleprop_base * np.abs(calc_base.records.e00900p)) +
                            (mtr_otherSchE_base * np.abs(calc_base.records.e02000 - calc_base.records.e26270)) +
                            (mtr_partner_base * np.abs(calc_base.records.e26270))) * calc_base.records.s006 * posti_ref).sum() /
                          ((np.abs(calc_base.records.e00900p) + np.abs(calc_base.records.e02000-calc_base.records.e26270) +
                            np.abs(calc_base.records.e26270)) * calc_base.records.s006 * posti_ref).sum())
    tau_td_base = ((mtr_taxdef_base * calc_base.records.e01700 * calc_base.records.s006).sum() /
                   (calc_base.records.e01700 * calc_base.records.s006).sum())
    tau_td_ref = ((mtr_taxdef_ref * calc_ref.records.e01700 * calc_ref.records.s006).sum() /
                  (calc_ref.records.e01700 * calc_ref.records.s006).sum())
    tau_base = tau_nc_taxable_base * alpha_nc_ft + tau_td_base * alpha_nc_td
    tau_ref = tau_nc_taxable_ref * alpha_nc_ft + tau_td_ref * alpha_nc_td
    return (tau_base, tau_ref)

def get_mtr_nc(calc):
    alpha_nc_ft = 0.763 # fully taxable share of noncorporate equity
    alpha_nc_td = 0.101 # share of noncorporate equity held in tax-deferred accounts
    mtr1 = calc.mtr('e00900p')[2]
    mtr2 = calc.mtr('e26270')[2]
    mtr3 = calc.mtr('e02000')[2]
    posti = (calc.records.c04800 > 0.)
    inc1 = np.abs(calc.records.e00900)
    inc2 = np.abs(calc.records.e26270)
    inc3 = np.abs(calc.records.e02000 - calc.records.e26270)
    wgt = calc.records.s006
    mtr_ft = (sum((mtr1 * inc1 + mtr2 * inc2 + mtr3 * inc3) * posti * wgt) /
              sum((inc1 + inc2 + inc3) * posti * wgt))
    mtr4 = calc.mtr('e01700')[2]
    inc4 = calc.records.e01700
    mtr_td = sum(mtr4 * inc4 * posti * wgt) / sum(inc4 * posti * wgt)
    mtr_nc = alpha_nc_ft * mtr_ft + alpha_nc_td * mtr_td
    return mtr_nc

def calc_mtr_nc_list(iit_refdict={}):
    calc1 = make_calculator(iit_refdict, 2013)
    mtrlist = []
    for year in range(2014, 2028):
        calc1.increment_year()
        calc1.calc_all()
        mtrlist.append(get_mtr_nc(calc1))
    return mtrlist

def distribute_results(reformdict):
    calc_base = make_calculator({}, 2014)
    calc_ref = make_calculator(reformdict, 2014)
    indiv_rev_impact = np.zeros(14)
    for i in range(2014,2028):
        calc_ref2 = copy.deepcopy(calc_ref)
        calc_ref2.records.e00900p = np.where(calc_ref2.records.e00900p >= 0, 
                                             calc_ref2.records.e00900p * indiv_gfactors['SchC_pos'][i-2014], 
                                             calc_ref2.records.e00900p * indiv_gfactors['SchC_neg'][i-2014])
        calc_ref2.records.e00900s = np.where(calc_ref2.records.e00900s >= 0, 
                                             calc_ref2.records.e00900s * indiv_gfactors['SchC_pos'][i-2014], 
                                             calc_ref2.records.e00900s * indiv_gfactors['SchC_neg'][i-2014])
        calc_ref2.records.e00900 = np.where(calc_ref2.records.e00900 >= 0, 
                                            calc_ref2.records.e00900 * indiv_gfactors['SchC_pos'][i-2014], 
                                            calc_ref2.records.e00900 * indiv_gfactors['SchC_neg'][i-2014])
        change_e26270 = np.where(calc_ref2.records.e26270 >= 0, 
                                 calc_ref2.records.e26270 * (indiv_gfactors['e26270_pos'][i-2014] - 1), 
                                 calc_ref2.records.e26270 * (indiv_gfactors['e26270_neg'][i-2014] - 1))
        calc_ref2.records.e26270 = calc_ref2.records.e26270 + change_e26270
        calc_ref2.records.e02000 = calc_ref2.records.e02000 + change_e26270
        # Change investment income
        calc_ref2.records.e00600 = calc_ref2.records.e00600 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.e00650 = calc_ref2.records.e00650 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.p22250 = calc_ref2.records.p22250 * indiv_gfactors['equity'][i-2014]
        calc_ref2.records.p23250 = calc_ref2.records.p23250 * indiv_gfactors['equity'][i-2014]
        calc_base.calc_all()
        calc_ref2.calc_all()
        indiv_rev_impact[i-2014] = sum((calc_ref2.records.combined -
                                        calc_base.records.combined) * calc_base.records.s006) / 10**9
        if i < 2027:
            calc_base.increment_year()
            calc_ref.increment_year()
    return(indiv_rev_impact)

def calc_tau_e(year, iitref):
    assert year in range(2014, 2028)
    m = 0.44 # retained earnings rate
    E = econ_defaults['r_e_c'][year-2017] + econ_defaults['pi'][year-2017]
    # shares of cg in short-term, long-term, and held until death
    omega_scg = 0.034
    omega_lcg = 0.496
    omega_xcg = 1 - omega_scg - omega_lcg
    # shares of corp equity in taxable, deferred and nontaxable form
    alpha_ft = 0.572
    alpha_td = 0.039
    alpha_nt = 0.389
    # holding period for gains
    h_scg = 0.5
    h_lcg = 8.0
    h_td = 8.0
    calc = make_calculator(iitref, year)
    mtr_d = calc.mtr('e00650')[2]
    mtr_scg = calc.mtr('p22250')[2]
    mtr_lcg = calc.mtr('p23250')[2]
    mtr_td = calc.mtr('e01700')[2]
    inc_d = calc.records.e00650
    inc_scg = np.where(calc.records.p22250 >= 0, calc.records.p22250, 0)
    inc_lcg = np.where(calc.records.p23250 >= 0, calc.records.p23250, 0)
    inc_td = calc.records.e01700
    posti = (calc.records.c04800 > 0.)
    wgt = calc.records.s006
    tau_d = sum(mtr_d * inc_d * posti * wgt) / sum(inc_d * posti * wgt)
    # accrual effective mtr on stcg
    tau_scg1 = sum(mtr_scg * inc_scg * posti * wgt) / sum(inc_scg * posti * wgt)
    tau_scg = 1 - np.log(np.exp(m * E * h_scg) * (1 - tau_scg1) + tau_scg1) / (m * E * h_scg)
    # accrual effective mtr on ltcg
    tau_lcg1 = sum(mtr_lcg * inc_lcg * posti * wgt) / sum(inc_lcg * posti * wgt)
    tau_lcg = 1 - np.log(np.exp(m * E * h_lcg) * (1 - tau_lcg1) + tau_lcg1) / (m * E * h_lcg)
    # mtr on capital gains held until death
    tau_xcg = 0.0
    tau_cg = omega_scg * tau_scg + omega_lcg * tau_lcg + omega_xcg * tau_xcg
    tau_ft = (1 - m) * tau_d + m * tau_cg
    tau_td1 = sum(mtr_td * inc_td * posti * wgt) / sum(inc_td * posti * wgt)
    tau_td = 1 - np.log(np.exp(E * h_td) * (1 - tau_td1) + tau_td1) / (E * h_td)
    tau_e = alpha_ft * tau_ft + alpha_td * tau_td + alpha_nt * 0.0
    return(tau_e)




