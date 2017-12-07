"""
This file provides the code to interface with taxcalc.
"""
# Set this path as needed.
records_url = 'puf.csv'
def make_calculator(reform_dict, start_year):
    """
    Build Calculator object with the given reform dictionary,
    advanced to start_year.
    """
    policy1 = Policy()
    behavior1 = Behavior()
    records1 = Records(records_url)
    if reform_dict != {}:
        policy1.implement_reform(reform_dict)
    calc1 = Calculator(records=records1, policy=policy1, behavior=behavior1)
    calc1.advance_to_year(start_year)
    calc1.calc_all()
    return(calc1)

def calc_tau_nc(calc):
    """
    Calculate the effective marginal tax rate on noncorporate business income.
    Noncorporate equity income can be in several forms:
        e00900: sole proprietorship income (Sch. C)
        e26270: partnership or S corporation active income
        e02000 - e26270: passive business income
    """
    # Shares of noncorporate equity in fully taxable and tax-deferred form.
    alpha_nc_ft = 0.763
    alpha_nc_td = 0.101
    mtr1 = calc.mtr('e00900p')[2]
    mtr2 = calc.mtr('e26270')[2]
    mtr3 = calc.mtr('e02000')[2]
    mtr4 = calc.mtr('e01700')[2]
    posti = (calc.records.c04800 > 0.)
    inc1 = np.abs(calc.records.e00900)
    inc2 = np.abs(calc.records.e26270)
    inc3 = np.abs(calc.records.e02000 - calc.records.e26270)
    inc4 = calc.records.e01700
    wgt = calc.records.s006
    mtr_ft = (sum((mtr1 * inc1 + mtr2 * inc2 + mtr3 * inc3) * posti * wgt) /
              sum((inc1 + inc2 + inc3) * posti * wgt))
    mtr_td = sum(mtr4 * inc4 * posti * wgt) / sum(inc4 * posti * wgt)
    mtr_nc = alpha_nc_ft * mtr_ft + alpha_nc_td * mtr_td
    return mtr_nc

def get_mtr_nc_list(iit_refdict={}):
    # Calculates the EMTR on noncorporate business income for 2014-2027
    calc1 = make_calculator(iit_refdict, 2013)
    mtrlist = []
    for year in range(2014, 2028):
        calc1.increment_year()
        calc1.calc_all()
        mtrlist.append(calc_tau_nc(calc1))
    return mtrlist

def distribute_results(reformdict):
    """
    Pass effects of business tax reform to taxcalc.
    Adjusts individual income based on growth factors.
    Adjusts noncorporate business credits based on rescaling factors from
    legal shifting response.
    """
    calc_base = make_calculator({}, 2014)
    calc_ref = make_calculator(reformdict, 2014)
    indiv_rev_impact = np.zeros(14)
    for i in range(2014, 2028):
        calc_ref2 = copy.deepcopy(calc_ref)
        # Change noncorporate business income
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
        # Change noncorporate business credits
        calc_ref2.records.e07300 = calc_ref2.records.e07300 * rescale_noncorp[i-2014]
        calc_ref2.records.e07400 = calc_ref2.records.e07400 * rescale_noncorp[i-2014]
        calc_ref2.records.e07600 = calc_ref2.records.e07600 * rescale_noncorp[i-2014]
        calc_base.calc_all()
        calc_ref2.calc_all()
        indiv_rev_impact[i-2014] = sum((calc_ref2.records.combined -
                                        calc_base.records.combined) *
                                       calc_base.records.s006) / 10**9
        if i < 2027:
            calc_base.increment_year()
            calc_ref.increment_year()
    return(indiv_rev_impact)

def calc_tau_e(calc):
    """
    Calculate the effective marginal tax rate on equity income in year.
    """
    # Retained earnings rate
    m = 0.44
    # Nominal expected return to equity
    year = calc.current_year
    E = econ_defaults['r_e_c'][year-2017] + econ_defaults['pi'][year-2017]
    # shares of cg in short-term, long-term, and held until death
    omega_scg = 0.034
    omega_lcg = 0.496
    omega_xcg = 1 - omega_scg - omega_lcg
    # shares of corp equity in taxable, deferred and nontaxable form
    alpha_ft = 0.572
    alpha_td = 0.039
    alpha_nt = 0.389
    # holding period for equity
    h_scg = 0.5
    h_lcg = 8.0
    h_td = 8.0
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
    tau_scg1 = (sum(mtr_scg * inc_scg * posti * wgt) /
                sum(inc_scg * posti * wgt))
    tau_scg = 1 - (np.log(np.exp(m * E * h_scg) * (1 - tau_scg1) + tau_scg1) /
                   (m * E * h_scg))
    # accrual effective mtr on ltcg
    tau_lcg1 = (sum(mtr_lcg * inc_lcg * posti * wgt) /
                sum(inc_lcg * posti * wgt))
    tau_lcg = 1 - (np.log(np.exp(m * E * h_lcg) * (1 - tau_lcg1) + tau_lcg1) /
                   (m * E * h_lcg))
    # mtr on capital gains held until death
    tau_xcg = 0.0
    tau_cg = omega_scg * tau_scg + omega_lcg * tau_lcg + omega_xcg * tau_xcg
    tau_ft = (1 - m) * tau_d + m * tau_cg
    tau_td1 = sum(mtr_td * inc_td * posti * wgt) / sum(inc_td * posti * wgt)
    tau_td = 1 - (np.log(np.exp(E * h_td) * (1 - tau_td1) + tau_td1) /
                  (E * h_td))
    tau_e = alpha_ft * tau_ft + alpha_td * tau_td + alpha_nt * 0.0
    return(tau_e)

def get_mtr_e_list(iit_refdict={}):
    # Calculates the EMTR on income from corporate equity for 2017-2027
    calc1 = make_calculator(iit_refdict, 2016)
    mtrlist = []
    for year in range(2017, 2028):
        calc1.increment_year()
        calc1.calc_all()
        mtrlist.append(calc_tau_e(calc1))
    return mtrlist
