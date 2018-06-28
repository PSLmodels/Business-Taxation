"""
The code in this file generates the baseline.
"""

# AMT and PYMTC
amt_base = AMTmodel()
# FTC
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
annualDepreciation_base_corp = annualCCRdeduction(inv_mat_base_corp,
                                                  btax_defaults,
                                                  brc_defaults_other,
                                                  adjfactor_dep_corp)
if track_progress:
    print("Corporate depreciation calculated")
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
