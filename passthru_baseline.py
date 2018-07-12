# Calculate shares for 2013 to distribute changes in depreciation and interest
totaldep = (partner_data['dep_total'][19] + Scorp_data['dep_total'][18] +
            sp_data['dep_total'][16])
depshare_scorp_posinc = Scorp_data['dep_posinc'][18] / totaldep
depshare_scorp_neginc = (Scorp_data['dep_total'][18] / totaldep -
                         depshare_scorp_posinc)
depshare_sp_posinc = sp_data['dep_posinc'][16] / totaldep
depshare_sp_neginc = sp_data['dep_total'][16] / totaldep - depshare_sp_posinc
depshare_partner_posinc = partner_data['dep_posinc'][19] / totaldep
depshare_partner_neginc = (partner_data['dep_total'][19] / totaldep -
                           depshare_partner_posinc)

totalint_exfin = (partner_data['intpaid_total'][19] +
                  Scorp_data['intpaid_total'][18] +
                  sp_data['mortintpaid'][16] + sp_data['otherintpaid'][16] -
                  partner_data['intpaid_fin_total'][16] -
                  Scorp_data['intpaid_fin'][16] -
                  sp_data['mortintpaid_fin'][16] -
                  sp_data['otherintpaid_fin'][16])
intshare_scorp_posinc = (Scorp_data['intpaid_posinc'][18] -
                         Scorp_data['intpaid_fin_posinc'][18]) / totalint_exfin
intshare_scorp_neginc = ((Scorp_data['intpaid_total'][18] -
                          Scorp_data['intpaid_total'][18]) /
                         totalint_exfin - intshare_scorp_posinc)
intshare_sp_posinc = (sp_data['mortintpaid_posinc'][16] +
                      sp_data['otherintpaid_posinc'][16] -
                      sp_data['mortintpaid_fin_posinc'][16] -
                      sp_data['otherintpaid_fin_posinc'][16]) / totalint_exfin
intshare_sp_neginc = ((sp_data['mortintpaid'][16] +
                       sp_data['otherintpaid'][16] -
                       sp_data['mortintpaid_fin'][16] -
                       sp_data['otherintpaid_fin'][16]) /
                      totalint_exfin - intshare_sp_posinc)
intshare_partner_posinc = ((partner_data['intpaid_posinc'][19] -
                            partner_data['intpaid_fin_posinc'][19]) /
                           totalint_exfin)
intshare_partner_neginc = ((partner_data['intpaid_total'][19] -
                            partner_data['intpaid_fin_total'][19]) /
                           totalint_exfin - intshare_partner_posinc)

# Construct Sch C income
sp_posinc = [sp_data['netinc'][17]]
sp_neginc = [sp_data['netloss'][17]]
for i in range(55, 68):
    sp_posinc.append(sp_posinc[0] * investmentGfactors_data['prop_inc'][i] /
                     investmentGfactors_data['prop_inc'][54])
    sp_neginc.append(sp_neginc[0] * investmentGfactors_data['prop_inc'][i] /
                     investmentGfactors_data['prop_inc'][54])
SchC_results = pd.DataFrame({'year': range(2014, 2028),
                             'netinc_pos_base': sp_posinc,
                             'netinc_neg_base': sp_neginc})
SchC_results['intpaid_pos_base'] = (IntPaid_base_noncorp['intpaid'] *
                                    intshare_sp_posinc)
SchC_results['intpaid_neg_base'] = (IntPaid_base_noncorp['intpaid'] *
                                    intshare_sp_neginc)
SchC_results['dep_pos_base'] = (capPath_base_noncorp['taxDep'] *
                                depshare_sp_posinc)
SchC_results['dep_neg_base'] = (capPath_base_noncorp['taxDep'] *
                                depshare_sp_neginc)
SchC_results['ebitda_pos_base'] = (SchC_results['netinc_pos_base'] +
                                   SchC_results['intpaid_pos_base'] +
                                   SchC_results['dep_pos_base'])
SchC_results['ebitda_neg_base'] = (-SchC_results['netinc_neg_base'] +
                                   SchC_results['intpaid_neg_base'] +
                                   SchC_results['dep_neg_base'])

# Construct partnership income
partner_posinc = [partner_data['netinc_total'][20]]
partner_neginc = [partner_data['netloss_total'][20]]
for i in range(55, 68):
    partner_posinc.append(partner_posinc[0] *
                          investmentGfactors_data['prop_inc'][i] /
                          investmentGfactors_data['prop_inc'][54])
    partner_neginc.append(partner_neginc[0] *
                          investmentGfactors_data['prop_inc'][i] /
                          investmentGfactors_data['prop_inc'][54])
partner_results = pd.DataFrame({'year': range(2014, 2028),
                                'netinc_pos_base': partner_posinc,
                                'netinc_neg_base': partner_neginc})
partner_results['intpaid_pos_base'] = (IntPaid_base_noncorp['intpaid'] *
                                       intshare_partner_posinc)
partner_results['intpaid_neg_base'] = (IntPaid_base_noncorp['intpaid'] *
                                       intshare_partner_neginc)
partner_results['dep_pos_base'] = (capPath_base_noncorp['taxDep'] *
                                   depshare_partner_posinc)
partner_results['dep_neg_base'] = (capPath_base_noncorp['taxDep'] *
                                   depshare_partner_neginc)
partner_results['ebitda_pos_base'] = (partner_results['netinc_pos_base'] +
                                      partner_results['intpaid_pos_base'] +
                                      partner_results['dep_pos_base'])
partner_results['ebitda_neg_base'] = (-partner_results['netinc_neg_base'] +
                                      partner_results['intpaid_neg_base'] +
                                      partner_results['dep_neg_base'])

# Construct S corporation income
scorp_posinc = ([Scorp_data['netinc_total'][18] *
                 investmentGfactors_data['prop_inc'][54] /
                 investmentGfactors_data['prop_inc'][53]])
scorp_neginc = ([Scorp_data['netloss_total'][18] *
                 investmentGfactors_data['prop_inc'][54] /
                 investmentGfactors_data['prop_inc'][53]])
for i in range(55, 68):
    scorp_posinc.append(scorp_posinc[0] *
                        investmentGfactors_data['prop_inc'][i] /
                        investmentGfactors_data['prop_inc'][54])
    scorp_neginc.append(scorp_neginc[0] *
                        investmentGfactors_data['prop_inc'][i] /
                        investmentGfactors_data['prop_inc'][54])
Scorp_results = pd.DataFrame({'year': range(2014, 2028),
                              'netinc_pos_base': scorp_posinc,
                              'netinc_neg_base': scorp_neginc})
Scorp_results['intpaid_pos_base'] = (IntPaid_base_noncorp['intpaid'] *
                                     intshare_scorp_posinc)
Scorp_results['intpaid_neg_base'] = (IntPaid_base_noncorp['intpaid'] *
                                     intshare_scorp_neginc)
Scorp_results['dep_pos_base'] = (capPath_base_noncorp['taxDep'] *
                                 depshare_scorp_posinc)
Scorp_results['dep_neg_base'] = (capPath_base_noncorp['taxDep'] *
                                 depshare_scorp_neginc)
Scorp_results['ebitda_pos_base'] = (Scorp_results['netinc_pos_base'] +
                                    Scorp_results['intpaid_pos_base'] +
                                    Scorp_results['dep_pos_base'])
Scorp_results['ebitda_neg_base'] = (-Scorp_results['netinc_neg_base'] +
                                    Scorp_results['intpaid_neg_base'] +
                                    Scorp_results['dep_neg_base'])
earnings1 = (SchC_results['ebitda_pos_base'] +
             SchC_results['ebitda_neg_base'] +
             partner_results['ebitda_pos_base'] +
             partner_results['ebitda_neg_base'] +
             Scorp_results['ebitda_pos_base'] +
             Scorp_results['ebitda_neg_base'])
earnings_base = pd.DataFrame({'ebitda': earnings1, 'year': range(2014, 2028)})
