"""
This file runs and implements the reform.
It should be run after the reform parameters have been specified
and the investment responses calculated.
"""
# Investment, depreciation and capital
(inv_mat_ref_corp, inv_mat_ref_noncorp) = buildNewInvMatrix(response_results)
if track_progress:
    print("New investment matrices constructed")
(hc_dep_year_c, hc_dep_c) = extract_other_param('undepBasis_corp_hc',
                                                other_params_reform)
(hc_dep_year_nc, hc_dep_nc) = extract_other_param('undepBasis_noncorp_hc',
                                                  other_params_reform)
annualDepreciation_ref_corp = annualCCRdeduction(inv_mat_ref_corp,
                                                 btax_params_reform,
                                                 other_params_reform,
                                                 adjfactor_dep_corp,
                                                 hc_dep_c, hc_dep_year_c, True)
if track_progress:
    print("New corporate depreciation calculated")
annualDepreciation_ref_noncorp = annualCCRdeduction(inv_mat_ref_noncorp,
                                                    btax_params_reform,
                                                    other_params_reform,
                                                    adjfactor_dep_noncorp,
                                                    hc_dep_nc, hc_dep_year_nc, False)
if track_progress:
    print("New noncorporate depreciation calculated")
(capPath_ref_corp, Kstock_ref_corp) = capitalPath(inv_mat_ref_corp,
                                                  annualDepreciation_ref_corp)
(capPath_ref_noncorp, Kstock_ref_noncorp) = capitalPath(inv_mat_ref_noncorp,
                                                        annualDepreciation_ref_noncorp,
                                                        corp_noncorp=False)
if track_progress:
    print("New capital paths calculated")

# Change in earnings
earnings_ref_data = earningsResponse(response_results)
earnings_ref_data['earnings_base'] = combined_base['ebitda'].tolist()
earnings_ref_data['ebitda'] = (earnings_ref_data['earnings_base'] +
                               earnings_ref_data['deltaE'])
combined_ref = earnings_ref_data.drop(['deltaE', 'earnings_base'], axis=1,
                                      inplace=False)
combined_ref['ebitda'] = np.asarray(combined_ref['ebitda']) * rescale_corp
combined_ref['taxDep'] = capPath_ref_corp['taxDep']
if track_progress:
    print("New earnings calculated")

# Net interest deduction and interest paid deduction
(hc_nid_year_c, hc_nid_c) = extract_other_param('netIntPaid_corp_hc',
                                                other_params_reform)
(hc_id_old_year_c, hc_id_old_c) = extract_other_param('oldIntPaid_corp_hc',
                                                      other_params_reform)
(hc_id_new_year_c, hc_id_new_c) = extract_other_param('newIntPaid_corp_hc',
                                                      other_params_reform)
assert hc_id_old_year_c == hc_id_new_year_c
(hc_id_old_year_nc, hc_id_old_nc) = extract_other_param('oldIntPaid_noncorp_hc',
                                                        other_params_reform)
(hc_id_new_year_nc, hc_id_new_nc) = extract_other_param('newIntPaid_noncorp_hc',
                                                        other_params_reform)
assert hc_id_old_year_nc == hc_id_new_year_nc
NID_ref = NID_response(capPath_ref_corp, id_hc_year=hc_id_old_year_c,
                       nid_hc_year=hc_nid_year_c,
                       id_hc_old=hc_id_old_c, id_hc_new=hc_id_new_c,
                       nid_hc=hc_nid_c)
if track_progress:
    print("New corporate net interest deduction calculated")
IntDed_ref_noncorp = noncorpIntDeduction_response(capPath_ref_noncorp,
                                                  id_hc_year=hc_id_old_year_nc,
                                                  id_hc_old=hc_id_old_nc,
                                                  id_hc_new=hc_id_new_nc)
if track_progress:
    print("New noncorporate interest deduction calculated")
combined_ref['nid'] = NID_ref['nid']

# Sec 199
(s199hc_yr, s199hc) = extract_other_param('sec199_hc', other_params_reform)
sec199_reform = sec199(s199_hc=s199hc, s199_hc_year=s199hc_yr)
combined_ref['sec199'] = sec199_reform

# Compute taxinc and taxbc
combined_ref['taxinc'] = (combined_ref['ebitda'] - combined_ref['taxDep'] -
                          combined_ref['nid'] - combined_ref['sec199'])
combined_ref['tau'] = btax_params_reform['tau_c']
combined_ref['taxbc'] = combined_ref['taxinc'] * combined_ref['tau']
if track_progress:
    print("New taxable income calculated")
# FTC
(ftchc_year, ftchc) = extract_other_param('ftc_hc', other_params_reform)
ftc_ref = FTC_model(haircut=ftchc, haircut_year=ftchc_year)
combined_ref['ftc'] = ftc_ref['ftc']

# AMT and PYMTC
(amtrepeal_yr, amtrepeal_truth) = extract_other_param('amt_repeal',
                                                      other_params_reform)
if amtrepeal_truth:
    amtrepealyear = amtrepeal_yr
else:
    amtrepealyear = 9e99
(pymtcrepeal_yr, pymtcrepeal_truth) = extract_other_param('pymtc_repeal',
                                                          other_params_reform)
if pymtcrepeal_truth:
    pymtcrepealyear = pymtcrepeal_yr
else:
    pymtcrepealyear = 9e99
amt_ref = AMTmodel(amt_repeal_year=amtrepealyear,
                   pymtc_repeal_year=pymtcrepealyear,
                   amt_rates=np.asarray(btax_params_reform['tau_amt']),
                   ctax_rates=np.asarray(btax_params_reform['tau_c']))

combined_ref['gbc'] = gbc()
# Complete combined_ref
combined_ref = combined_ref.merge(right=amt_ref, how='outer', on='year')
combined_ref['taxrev'] = (combined_ref['taxbc'] + combined_ref['amt'] -
                          combined_ref['ftc'] - combined_ref['pymtc'] -
                          combined_ref['gbc'])
# Pass-through model
exec(open('passthru_reform.py').read())
print("Reform corporate tax revenue complete")
