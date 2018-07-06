"""
The code in this file generates the baseline.
"""


# AMT and PYMTC
(adjfactor_pymtc_corp, adjfactor_amt_corp) = calcAMTparams()
amt_base = AMTmodel()
# FTC
adjfactor_ftc_corp = calcFTCAdjustment()
ftc_base = FTC_model()
# Combine and calculte taxable income
combined_base = taxrev_data.merge(right=amt_base, how='outer', on='year')
combined_base['ftc'] = ftc_base['ftc']
combined_base['taxbc'] = (combined_base['taxrev'] + combined_base['pymtc'] +
                          combined_base['ftc'] - combined_base['amt'])
combined_base['gbc_adj'] = 0.021642614
combined_base['tau'] = btax_defaults['tau_c']
combined_base['taxinc'] = (combined_base['taxbc'] /
                           (combined_base['tau'] - combined_base['gbc_adj']))
if track_progress:
    print("Taxable income calculated")
# Sec. 199
sec199_base = sec199()
combined_base['sec199'] = sec199_base['sec199']
# CCR
inv_mat_base_corp = build_inv_matrix()
inv_mat_base_noncorp = build_inv_matrix(False)
if track_progress:
    print("Investment matrices constructed")
if track_progress:
    print("Corporate depreciation calculated")
adjfactor_dep_corp = calcDepAdjustment()
if track_progress:
    print("Corporate depreciation adjustment calculated")
adjfactor_dep_noncorp = calcDepAdjustment(False)
if track_progress:
    print("Noncorporate depreciation adjustment calculated")
annualDepreciation_base_corp = annualCCRdeduction(inv_mat_base_corp,
                                                  btax_defaults,
                                                  brc_defaults_other,
                                                  adjfactor_dep_corp)
annualDepreciation_base_noncorp = annualCCRdeduction(inv_mat_base_noncorp,
                                                     btax_defaults,
                                                     brc_defaults_other,
                                                     adjfactor_dep_noncorp)
if track_progress:
    print("Noncorporate depreciation calculated")
(capPath_base_corp, Kstock_base_corp) = capitalPath(inv_mat_base_corp,
                                                    annualDepreciation_base_corp)
(capPath_base_noncorp, Kstock_base_noncorp) = capitalPath(inv_mat_base_noncorp,
                                                          annualDepreciation_base_noncorp,
                                                          corp_noncorp=False)
if track_progress:
    print("Capital paths calculated")
combined_base['taxDep'] = capPath_base_corp['taxDep']
# Interest model
exec(open('interest_model.py').read())
NID_base = netInterestDeduction(capPath_base_corp)
if track_progress:
    print("Corporate net interest deduction calculated")
IntPaid_base_noncorp = noncorpIntDeduction(capPath_base_noncorp)
if track_progress:
    print("Noncorporate interest deduction calculated")
combined_base['nid'] = NID_base['nid']
# Complete the combining of baseline results
combined_base['ebitda'] = (combined_base['taxinc'] + combined_base['sec199'] +
                           combined_base['taxDep'] + combined_base['nid'])
(mtr_nclist_base, mtr_elist_base) = gen_mtr_lists({})
btax_defaults['tau_nc'] = mtr_nclist_base
btax_defaults['tau_e'] = mtr_elist_base
if track_progress:
    print("Marginal tax rates calculated")
# Build pass-through model
exec(open('passthru_baseline.py').read())
if track_progress:
    print("Baseline complete")
# Save baseline components to CSVs
capPath_base_corp.to_csv('capPath_base_corp.csv')
capPath_base_noncorp.to_csv('capPath_base_noncorp.csv')
combined_base.to_csv('corptax_results_base.csv')
btax_defaults.to_csv('mini_params_btax.csv')
SchC_results.to_csv('SchC_base.csv')
partner_results.to_csv('partnership_base.csv')
Scorp_results.to_csv('Scorp_base.csv')
earnings_base.to_csv('passthru_earnings.csv')
adj_factors = {'amt': adjfactor_amt_corp,
               'pymtc': adjfactor_pymtc_corp,
               'ftc': adjfactor_ftc_corp,
               'dep_corp': adjfactor_dep_corp,
               'dep_noncorp': adjfactor_dep_noncorp,
               'int_corp': adjfactor_int_corp,
               'int_noncorp': adjfactor_int_noncorp}
passthru_factors = {'dep_scorp_pos': depshare_scorp_posinc,
                    'dep_scorp_neg': depshare_scorp_neginc,
                    'dep_sp_pos': depshare_sp_posinc,
                    'dep_sp_neg': depshare_sp_neginc,
                    'dep_part_pos': depshare_partner_posinc,
                    'dep_part_neg': depshare_partner_neginc,
                    'int_scorp_pos': intshare_scorp_posinc,
                    'int_scorp_neg': intshare_scorp_neginc,
                    'int_sp_pos': intshare_sp_posinc,
                    'int_sp_neg': intshare_sp_neginc,
                    'int_part_pos': intshare_partner_posinc,
                    'int_part_neg': intshare_partner_neginc}
df_adjf = pd.DataFrame({k: [adj_factors[k]] for k in adj_factors})
df_adjf.to_csv('adjfactors.csv')
df_pts = pd.DataFrame({k: [passthru_factors[k]] for k in passthru_factors})
df_pts.to_csv('passthru_shares.csv')
if track_progress:
    print("BRC baseline results saved")
