# Baseline earnings and cash flow
corpInc_base = capPath_base_corp.drop(['FixedInv', 'FixedK',
                                       'Kstock', 'taxDep'],
                                      axis=1, inplace=False)
corpInc_base = corpInc_base.merge(right=NIP_base, how='outer', on='year')
corpInc_base['earnings'] = combined_base['ebitda']
corpInc_base['tax'] = combined_base['taxrev']
corpInc_base['inc_aftertax'] = (corpInc_base['earnings'] -
                                corpInc_base['TrueDep'] -
                                corpInc_base['nip'] - corpInc_base['tax'])
corpInc_base['cashflow'] = (corpInc_base['earnings'] -
                            corpInc_base['Investment'] -
                            corpInc_base['nip'] - corpInc_base['tax'])

# Reform earnings and cash flow
corpInc_ref = capPath_ref_corp.drop(['FixedInv', 'FixedK',
                                     'Kstock', 'taxDep'],
                                    axis=1, inplace=False)
corpInc_ref = corpInc_ref.merge(right=NIP_ref, how='outer', on='year')
corpInc_ref['earnings'] = combined_ref['ebitda']
corpInc_ref['tax'] = combined_ref['taxrev']
corpInc_ref['inc_aftertax'] = (corpInc_ref['earnings'] -
                               corpInc_ref['TrueDep'] -
                               corpInc_ref['nip'] - corpInc_ref['tax'])
corpInc_ref['cashflow'] = (corpInc_ref['earnings'] -
                           corpInc_ref['Investment'] -
                           corpInc_ref['nip'] - corpInc_ref['tax'])

# Multipliers for debt and equity income
indiv_gfactors = corpInc_base.drop(['earnings', 'tax', 'TrueDep',
                                    'cashflow', 'nip'], axis=1, inplace=False)
indiv_gfactors.rename(columns={'inc_aftertax': 'inc_aftertax_base'},
                      inplace=True)
indiv_gfactors['inc_aftertax_ref'] = corpInc_ref['inc_aftertax']
indiv_gfactors['equity'] = (indiv_gfactors['inc_aftertax_ref'] /
                            indiv_gfactors['inc_aftertax_base'])
corpshare_totalint = 1.0  ##Corporate interest share of all interest
# Note: interest income not distributed to debtholders (yet)
indiv_gfactors['debt'] = (1 + (corpInc_ref['nip'] / corpInc_base['nip'] - 1) *
                          corpshare_totalint)

# Multipliers for pass-through net income or loss, for e00900 and e26270
execfile('passthru_model.py')
indiv_gfactors['SchC_pos'] = (SchC_results['netinc_pos_ref'] /
                              SchC_results['netinc_pos_base'])
indiv_gfactors['SchC_neg'] = (SchC_results['netinc_neg_ref'] /
                              SchC_results['netinc_neg_base'] * -1)
indiv_gfactors['e26270_pos'] = ((partner_results['netinc_pos_ref'] +
                                 Scorp_results['netinc_pos_ref']) /
                                (partner_results['netinc_pos_base'] +
                                 Scorp_results['netinc_pos_base']))
indiv_gfactors['e26270_neg'] = ((partner_results['netinc_neg_ref'] +
                                 Scorp_results['netinc_neg_ref']) / 
                                (partner_results['netinc_neg_base'] +
                                 Scorp_results['netinc_neg_base']) * -1)
