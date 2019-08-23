"""
Updating Business-Taxation for TCJA responses. 

This file runs the TCJA to compute the effect of
changes in the policies on changes in business
borrowing (debt-to-asset ratios) and repatriations.

Elasticities to use:
	Debt semi-elasticity: 0.17 (de Mooij and Everdeen, 2011)
	Repatriation semi-elasticity: -0.61 (Desai, Foley and Hines, 2001)
	First year response: 2018
We ignore investment elasticities, as these are update by BEA forecast.

"""
import taxcalc # capabilities of individual Tax-Calculator
from taxcalc.utils import json_to_dict
from biztax import Policy, BusinessModel, Response
import json

# 2017 law business tax rules
bdict1 = {
    "tau_c": {2018: 0.347},
    "tau_amt": {2018: 0.2},
    "pymtc_hc": {2018: 0.0},
    "pymtc_refund": {2018: 0.0},
    "depr_3yr_bonus": {2018: 0.4,
                       2019: 0.3,
                       2020: 0.0},
    "depr_5yr_bonus": {2018: 0.4,
                       2019: 0.3,
                       2020: 0.0},
    "depr_7yr_bonus": {2018: 0.4,
                       2019: 0.3,
                       2020: 0.0},
    "depr_10yr_bonus": {2018: 0.4,
                        2019: 0.3,
                        2020: 0.0},
    "depr_15yr_bonus": {2018: 0.4,
                        2019: 0.3,
                        2020: 0.0},
    "depr_20yr_bonus": {2018: 0.4,
                        2019: 0.3,
                        2020: 0.0},
    "sec199_rt": {2018: 0.09},
    "adjustedTaxInc_def": {2018: 1},
    "adjustedTaxInc_limit": {2018: 9e99},
    "domestic_dividend_inclusion": {2018: 0.3},
    "foreign_dividend_inclusion": {2018: 1.0},
    "foreign_tax_grossrt": {2018: 1.0},
    "foreign_repatriation_inclusion": {2018: 1.0},
    "GILTI_thd": {2018: 0.0},
    "GILTI_inclusion": {2018: 0.0},
    "fdii_rt": {2018: 0.0},
    "fdii_thd": {2018: 0.0}}
# TCJA law
bdict2 = {
    "tau_c": {2018: 0.21},
    "tau_amt": {2018: 0.0},
    "pymtc_hc": {2022: 1.0},
    "pymtc_refund": {2018: 0.5,
                     2021: 1.0,
                     2022: 0.0},
    "depr_3yr_bonus": {2018: 1.0,
                       2023: 0.8,
                       2024: 0.6,
                       2025: 0.4,
                       2026: 0.2,
                       2027: 0.0},
    "depr_5yr_bonus": {2018: 1.0,
                       2023: 0.8,
                       2024: 0.6,
                       2025: 0.4,
                       2026: 0.2,
                       2027: 0.0},
    "depr_7yr_bonus": {2018: 1.0,
                       2023: 0.8,
                       2024: 0.6,
                       2025: 0.4,
                       2026: 0.2,
                       2027: 0.0},
    "depr_10yr_bonus": {2018: 1.0,
                        2023: 0.8,
                        2024: 0.6,
                        2025: 0.4,
                        2026: 0.2,
                        2027: 0.0},
    "depr_15yr_bonus": {2018: 1.0,
                        2023: 0.8,
                        2024: 0.6,
                        2025: 0.4,
                        2026: 0.2,
                        2027: 0.0},
    "depr_20yr_bonus": {2018: 1.0,
                        2023: 0.8,
                        2024: 0.6,
                        2025: 0.4,
                        2026: 0.2,
                        2027: 0.0},
    "sec199_rt": {2018: 0.0},
    "adjustedTaxInc_def": {2022: 0},
    "adjustedTaxInc_limit": {2018: 0.3},
    "domestic_dividend_inclusion": {2018: 0.5},
    "foreign_dividend_inclusion": {2018: 0.0},
    "foreign_tax_grossrt": {2018: 0.0},
    "foreign_repatriation_inclusion": {2018: 0.31,
                                       2026: 0.0},
    "GILTI_thd": {2018: 0.1},
    "GILTI_inclusion": {2018: 0.5,
                        2025: 0.375},
    "fdii_rt": {2018: 0.375,
                2025: 0.21875},
    "fdii_thd": {2018: 0.1}}



JSON_PATH = 'biztax/reforms/'
with open(JSON_PATH + 'old_law_iitax.json') as file3:
	text3 = file3.read()
	idict1 = json_to_dict(text3)
with open(JSON_PATH + 'new_law_iitax.json') as file4:
	text4 = file4.read()
	idict2 = json_to_dict(text4)

# Policies for business tax rules
pol_pre = Policy()
pol_pre.implement_reform(bdict1)
pol_post = Policy()
pol_post.implement_reform(bdict2)
# Policies for individual income tax rules
ipol_pre = taxcalc.Policy()
#ipol_pre.implement_reform(taxcalc.Policy.read_json_reform('2017_law.json'))
ipol_post = taxcalc.Policy()
#ipol_post.implement_reform(taxcalc.Policy.read_json_reform('TCJA.json'))

# Create and run model
bm = BusinessModel(btax_policy_ref=pol_pre, itax_policy_ref=ipol_pre,
                   btax_policy_base=pol_post, itax_policy_base=ipol_post)
bm.calc_all(response=None)

# Update the MTRs from taxcalc
bm.update_mtrlists()

# Create Response object
resp = Response()
resp.update_elasticities({'debt_taxshield_c': 0.17,
	                      'reprate_inc': -0.61,
	                      'first_year_response': 2018})
resp.calc_all(bm.btax_params_base, bm.btax_params_ref)

# Extract debt items of interest
debteffect = pd.DataFrame({'year': range(2014, 2028)})
debteffect['fracded_base'] = bm.btax_params_base['fracded_c']
debteffect['txrt_base'] = bm.btax_params_base['tau_c']
debteffect['shield_base'] = debteffect['fracded_base'] * debteffect['txrt_base']
debteffect['fracded_ref'] = bm.btax_params_ref['fracded_c']
debteffect['txrt_ref'] = bm.btax_params_ref['tau_c']
debteffect['shield_ref'] = debteffect['fracded_ref'] * debteffect['txrt_ref']
debteffect['debtch'] = resp.debt_response['pchDelta_corp']

# Extract repatriation items of interest
repateffect = pd.DataFrame({'year': range(2014, 2028)})
ftax = Data().cfc_data.loc[0, 'taxrt']
repateffect['frachit_base'] = bm.btax_params_base['foreign_dividend_inclusion']
repateffect['txdiff_base'] = np.maximum(bm.btax_params_base['tau_c'] - ftax, 0.)
repateffect['penalty_base'] = repateffect['frachit_base'] * repateffect['txdiff_base']
repateffect['frachit_ref'] = bm.btax_params_ref['foreign_dividend_inclusion']
repateffect['txdiff_ref'] = np.maximum(bm.btax_params_ref['tau_c'] - ftax, 0.)
repateffect['penalty_ref'] = repateffect['frachit_ref'] * repateffect['txdiff_ref']
repateffect['repatch'] = resp.repatriation_response['reprate_e']

# Export results to check manually
debteffect.to_csv('debttest.csv')
repateffect.to_csv('repattest.csv')