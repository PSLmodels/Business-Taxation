# Code to smoothly interface with taxcalc
records_url = 'puf.csv'
def make_calculator(reform_dict, start_year):
    policy1 = Policy()
    behavior1 = Behavior()
    records1 = Records(records_url)
    if reform_dict != {}:
        policy1.implement_reform(reform_dict)
    calc1 = Calculator(records = records1, policy = policy1, behavior = behavior1)
    for i in range(start_year - 2013):
        calc1.increment_year()
    assert calc1.current_year == start_year
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
