# Background functions and calculations of adjustment factors
execfile('import_packages.py')
execfile('read_in_data.py')
execfile('amt_model.py')
execfile('ftc_model.py')
execfile('sec199_model.py')
execfile('ccr_model.py')
execfile('usercode_taxcalc.py')
# Generate the baseline
execfile('gen_baseline.py')
# Preliminary implementation of reform and behavioral responses
execfile('reform_implementation.py')
execfile('responses.py')
update_elast_dict(elast_params)
execfile('mini_combined.py')
response_results = inv_response()
legal_response()
# Generate the reform path
execfile('gen_reform.py')
execfile('multipliers_for_taxcalc.py')
indiv_rev_impact = distribute_results(iit_params_ref)
ModelResults = pd.DataFrame({'year': range(2014, 2028),
                             'IndivTaxRev': indiv_rev_impact})
ModelResults['CorpTaxRev'] = combined_ref['taxrev'] - combined_base['taxrev']
ModelResults['RevenueChange'] = (ModelResults['IndivTaxRev'] +
                                 ModelResults['CorpTaxRev'])
