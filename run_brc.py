# Background functions and calculations of adjustment factors
exec(open('import_packages.py').read())
exec(open('read_in_data.py').read())
exec(open('amt_model.py').read())
exec(open('ftc_model.py').read())
exec(open('sec199_model.py').read())
exec(open('ccr_model.py').read())
exec(open('usercode_taxcalc.py').read())
# Generate the baseline
exec(open('gen_baseline.py').read())
# Preliminary implementation of reform and behavioral responses
exec(open('reform_implementation.py').read())
exec(open('responses.py').read())
update_elast_dict(elast_params)
exec(open('mini_combined.py').read())
response_results = inv_response()
legal_response()
# Generate the reform path
exec(open('gen_reform.py').read())
exec(open('multipliers_for_taxcalc.py').read())
indiv_rev_impact = distribute_results(iit_params_ref)
ModelResults = pd.DataFrame({'year': range(2014, 2028),
                             'IndivTaxRev': indiv_rev_impact})
ModelResults['CorpTaxRev'] = combined_ref['taxrev'] - combined_base['taxrev']
ModelResults['RevenueChange'] = (ModelResults['IndivTaxRev'] +
                                 ModelResults['CorpTaxRev'])
