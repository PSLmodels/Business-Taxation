# Calculate new EBITDA
earnings_results_noncorp = earningsResponse(response_results, False)
earnings_results_noncorp['ebitda_base'] = earnings_base['ebitda']
earnings_results_noncorp['ebitda_ref'] = (earnings_results_noncorp['ebitda_base'] +
                                          earnings_results_noncorp['deltaE']) * rescale_noncorp
earnings_results_noncorp['ebitda_chgfactor'] = (earnings_results_noncorp['ebitda_ref'] /
                                                earnings_results_noncorp['ebitda_base'])

SchC_results['ebitda_pos_ref'] = (SchC_results['ebitda_pos_base'] *
                                  earnings_results_noncorp['ebitda_chgfactor'])
SchC_results['ebitda_neg_ref'] = (SchC_results['ebitda_neg_base'] *
                                  earnings_results_noncorp['ebitda_chgfactor'])
partner_results['ebitda_pos_ref'] = (partner_results['ebitda_pos_base'] *
                                     earnings_results_noncorp['ebitda_chgfactor'])
partner_results['ebitda_neg_ref'] = (partner_results['ebitda_neg_base'] *
                                     earnings_results_noncorp['ebitda_chgfactor'])
Scorp_results['ebitda_pos_ref'] = (Scorp_results['ebitda_pos_base'] *
                                   earnings_results_noncorp['ebitda_chgfactor'])
Scorp_results['ebitda_neg_ref'] = (Scorp_results['ebitda_neg_base'] *
                                   earnings_results_noncorp['ebitda_chgfactor'])

# Recalculate sole proprietorship net income or loss
SchC_results['dep_pos_ref'] = (capPath_ref_noncorp['taxDep'] *
                               depshare_sp_posinc)
SchC_results['dep_neg_ref'] = (capPath_ref_noncorp['taxDep'] *
                               depshare_sp_neginc)
SchC_results['intpaid_pos_ref'] = (IntDed_ref_noncorp['intDed'] *
                                   intshare_sp_posinc)
SchC_results['intpaid_neg_ref'] = (IntDed_ref_noncorp['intDed'] *
                                   intshare_sp_neginc)
SchC_results['netinc_pos_ref'] = (SchC_results['ebitda_pos_ref'] -
                                  SchC_results['dep_pos_ref'] -
                                  SchC_results['intpaid_pos_ref'])
SchC_results['netinc_neg_ref'] = (SchC_results['ebitda_neg_ref'] -
                                  SchC_results['dep_neg_ref'] -
                                  SchC_results['intpaid_neg_ref'])

# Recalculate partnership net income or loss
partner_results['dep_pos_ref'] = (capPath_ref_noncorp['taxDep'] *
                                  depshare_partner_posinc)
partner_results['dep_neg_ref'] = (capPath_ref_noncorp['taxDep'] *
                                  depshare_partner_neginc)
partner_results['intpaid_pos_ref'] = (IntDed_ref_noncorp['intDed'] *
                                      intshare_partner_posinc)
partner_results['intpaid_neg_ref'] = (IntDed_ref_noncorp['intDed'] *
                                      intshare_partner_neginc)
partner_results['netinc_pos_ref'] = (partner_results['ebitda_pos_ref'] -
                                     partner_results['dep_pos_ref'] -
                                     partner_results['intpaid_pos_ref'])
partner_results['netinc_neg_ref'] = (partner_results['ebitda_neg_ref'] -
                                     partner_results['dep_neg_ref'] -
                                     partner_results['intpaid_neg_ref'])

# Recalculate S corporation net income or loss
Scorp_results['dep_pos_ref'] = (capPath_ref_noncorp['taxDep'] *
                                depshare_scorp_posinc)
Scorp_results['dep_neg_ref'] = (capPath_ref_noncorp['taxDep'] *
                                depshare_scorp_neginc)
Scorp_results['intpaid_pos_ref'] = (IntDed_ref_noncorp['intDed'] *
                                    intshare_scorp_posinc)
Scorp_results['intpaid_neg_ref'] = (IntDed_ref_noncorp['intDed'] *
                                    intshare_scorp_neginc)
Scorp_results['netinc_pos_ref'] = (Scorp_results['ebitda_pos_ref'] -
                                   Scorp_results['dep_pos_ref'] -
                                   Scorp_results['intpaid_pos_ref'])
Scorp_results['netinc_neg_ref'] = (Scorp_results['ebitda_neg_ref'] -
                                   Scorp_results['dep_neg_ref'] -
                                   Scorp_results['intpaid_neg_ref'])
