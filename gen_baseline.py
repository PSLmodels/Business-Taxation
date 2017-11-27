# AMT and PYMTC
amt_base = AMTmodel()
# FTC
ftc_base = FTC_model()
# Combine and calculte taxable income
combined_base = taxrev_data.merge(right=amt_base, how='outer', on='year')
combined_base = combined_base.merge(right=ftc_base, how='outer', on='year')
combined_base['taxbc'] = (combined_base['taxrev'] + combined_base['pymtc'] +
                     	  combined_base['ftc'] - combined_base['amt'])
combined_base['gbc_adj'] = 0.025739617
combined_base['tau'] = 0.347
combined_base['taxinc'] = (combined_base['taxbc'] /
						   (combined_base['tau'] - combined_base['gbc_adj']))
# Sec. 199
sec199_results = sec199()
combined_base = combined_base.merge(right=sec199_results, how='outer', on='year')
# CCR
inv_mat_base_corp = build_inv_matrix()
inv_mat_base_noncorp = build_inv_matrix(False)
annualDepreciation_base_corp = annualCCRdeduction(inv_mat_base_corp,
                                                  btax_defaults, adjfactor_dep_corp)
print 'Depreciation step corp'
annualDepreciation_base_noncorp = annualCCRdeduction(inv_mat_base_noncorp,
                                                     btax_defaults,
                                                     adjfactor_dep_noncorp)
print 'Depreciation step noncorp'
(capPath_base_corp, taxDep_base_corp) = capitalPath(inv_mat_base_corp,
                                                    annualDepreciation_base_corp)
(capPath_base_noncorp, taxDep_base_noncorp) = capitalPath(inv_mat_base_noncorp,
                                                          annualDepreciation_base_noncorp,
                                                          corp_noncorp=False)
combined_base = combined_base.merge(right=taxDep_base_corp, how='outer', on='year')
# Interest model
execfile('interest_model.py')
(NID_base, NIP_base) = netInterestDeduction(capPath_base_corp)
IntPaid_base_noncorp = noncorpIntDeduction(capPath_base_noncorp)
combined_base = combined_base.merge(right=NID_base, how='outer', on='year')
# Complete the combining of baseline results
combined_base['ebitda'] = (combined_base['taxinc'] + combined_base['sec199'] +
                           combined_base['taxDep'] + combined_base['nid'])
