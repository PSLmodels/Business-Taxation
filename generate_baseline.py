"""
The code in this file calculates and saves the various adjustment factors
and DataFrames necessary for the calculations in BRC. 

We need to produce the following objects:
    adjfactors.csv
    pass-through shares
"""
import numpy as np
import pandas as pd
import copy
import scipy.optimize
from data import Data
from asset import Asset
from debt import Debt

# Specify single Data object (for convenience)
data1 = Data()


"""
Section 1. Calculation of the adjustment parameters
"""

def calcAMTparams2():
    """
    Calculates the adjustment factors for the AMT and PYMTC
    """
    # Grab historical data
    hist_data = copy.deepcopy(data1.historical_combined)
    taxinc = np.array(hist_data['taxinc'])
    amt = np.array(hist_data['amt'])
    pymtc = np.array(hist_data['pymtc'])
    stock = np.zeros(len(amt))
    stock[15] = 26.0
    tau_a = 0.2
    tau_c = 0.347
    # Expand model backward based on defined value of stock in 2013 (26.0)
    for i in range(15):
        stock[14-i] = stock[15-i] + pymtc[14-i] - amt[14-i]
    eta = sum([pymtc[i] / stock[i] for i in range(16)]) / 16.
    A_over_TI = sum([amt[i] / taxinc[i] for i in range(16)]) / 16.
    # Calculate solution to AMT parameter
    def amterr(lam):
        # Squared difference between actual AMT/TaxInc ratio vs. predicted
        ATI_pred = tau_a / lam * np.exp(-lam * (tau_c / tau_a - 1))
        err = (ATI_pred - A_over_TI)**2
        return err
    lamf = scipy.optimize.minimize_scalar(amterr,
                                          bounds=(0.001, 100),
                                          method='bounded').x
    alpha = 0.494
    theta = np.exp(-lamf * (tau_c / tau_a - 1))
    beta = (1 - alpha) * theta / (1 - theta)
    gamma = eta * (1 - alpha + beta) / (1 - alpha - eta * alpha + eta * beta)
    stock2014 = stock[15] + amt[15] - pymtc[15]
    return (lamf, theta, eta, gamma, alpha, beta, stock2014)

def calcWAvgTaxRate(year):
    """
    Calculates the weighted average statutory corporate tax rate
    in all OECD countries in a given year.
    """
    assert year in range(1995, 2028)
    year = min(year, 2016)
    gdp_list = np.asarray(data1.ftc_gdp_data[str(year)])
    taxrate_list = np.asarray(data1.ftc_taxrates_data[str(year)])
    # remove observations with missing data
    taxrate_list2 = np.where(np.isnan(taxrate_list), 0, taxrate_list)
    gdp_list2 = np.where(np.isnan(taxrate_list), 0, gdp_list)
    avgrate = sum(taxrate_list2 * gdp_list2) / sum(gdp_list2)
    return avgrate

def calcFTCAdjustment():
    """
    Calculates the adjustment factor for the FTC.
    """
    ftc_actual = np.asarray(data1.ftc_other_data['F'][:19])
    profits = np.asarray(data1.ftc_other_data['C_total'][:19])
    profits_d = np.asarray(data1.ftc_other_data['C_domestic'][:19])
    profits_f = profits - profits_d
    tax_f = []
    for i in range(1995, 2014):
        tax_f.append(calcWAvgTaxRate(i))
    ftc_gross = profits_f * tax_f / 100.
    adjfactor = sum(ftc_actual / ftc_gross) / 19.
    return adjfactor

def calcDepAdjustment(corp):
    """
    Calculates the adjustment factor for assets, depreciation and investment
    corp: indicator for whether corporate or noncorporate data
    """
    # Create Asset object
    asset1 = Asset(data1.btax_defaults, corp)
    asset1.calc_all()
    # Get unscaled depreciation for all years
    totalAnnualDepreciation = asset1.calcDep_allyears()
    #####
    depreciation_data = copy.deepcopy(data1.depreciationIRS_data)
    depreciation_data['dep_model'] = totalAnnualDepreciation[40:54]
    if corp:
        depreciation_data['scale'] = (depreciation_data['dep_Ccorp'] /
                                      depreciation_data['dep_model'])
    else:
        depreciation_data['scale'] = ((depreciation_data['dep_Scorp'] +
                                       depreciation_data['dep_sp'] +
                                       depreciation_data['dep_partner']) /
                                      depreciation_data['dep_model'])
    adj_factor = (sum(depreciation_data['scale']) /
                  len(depreciation_data['scale']))
    return adj_factor

def calcIDAdjustment(Corp, eta=0.4):
    """
    Calculates the adjustment factors for the corporate and noncorporate debt
    and interest. 
    eta: retirement rate of existing debt
    """
    # Create Asset object
    asset1 = Asset(data1.btax_defaults, Corp)
    asset1.calc_all()
    # Get asset forecast
    forecast = asset1.get_forecast()
    # Create Debt object
    debt1 = Debt(data1.btax_defaults, forecast, corp=Corp)
    debt1.calc_all()
    # Get unscaled net interest deduction
    NID_gross = debt1.NID[38:54]
    # Get net interest deduction from historical IRS data
    if Corp:
        NID_irs = np.array(data1.debt_data_corp['NID_IRS'])[38:54]
    else:
        NID_irs = np.array(data1.debt_data_noncorp['ID_Scorp'][38:54] +
                           data1.debt_data_noncorp['ID_sp'][38:54] +
                           data1.debt_data_noncorp['ID_partner'][38:54])
    NID_scale = sum(NID_irs / NID_gross) / 16.
    return NID_scale

# Calculate the adjustment and dynamic parameters for AMT & PYMTC
all_amt_params = calcAMTparams2()
# Calculate the FTC adjustment parameters
adjfactor_ftc_corp = calcFTCAdjustment()
# Calculate the depreciation adjustment parameters
adjfactor_dep_corp = calcDepAdjustment(True)
adjfactor_dep_noncorp = calcDepAdjustment(False)
# Calculate the interest adjustment parameters
adjfactor_int_corp = calcIDAdjustment(True)
adjfactor_int_noncorp = calcIDAdjustment(False)



"""
Section 2. Calculation of pass-through shares
Note: All shares are estimated for 2013.
"""
# Total depreciation
totaldep = (data1.partner_data['dep_total'][19] +
            data1.Scorp_data['dep_total'][18] +
            data1.sp_data['dep_total'][16])
# Depreciation shares for S corporations (by income status)
depshare_scorp_posinc = data1.Scorp_data['dep_posinc'][18] / totaldep
depshare_scorp_neginc = (data1.Scorp_data['dep_total'][18] / totaldep -
                         depshare_scorp_posinc)
# Depreciation shares for sole proprietorships (by income status)
depshare_sp_posinc = data1.sp_data['dep_posinc'][16] / totaldep
depshare_sp_neginc = data1.sp_data['dep_total'][16] / totaldep - depshare_sp_posinc
# Depreciation shares for partnerships (by income status)
depshare_partner_posinc = data1.partner_data['dep_posinc'][19] / totaldep
depshare_partner_neginc = (data1.partner_data['dep_total'][19] / totaldep -
                           depshare_partner_posinc)
# Total net interest deduction, excluding finance sector and holding companies
totalint_exfin = (data1.partner_data['intpaid_total'][19] +
                  data1.Scorp_data['intpaid_total'][18] +
                  data1.sp_data['mortintpaid'][16] +
                  data1.sp_data['otherintpaid'][16] -
                  data1.partner_data['intpaid_fin_total'][19] -
                  data1.Scorp_data['intpaid_fin'][18] -
                  data1.sp_data['mortintpaid_fin'][16] -
                  data1.sp_data['otherintpaid_fin'][16])
# Net interest share for S corporations (by income status)
intshare_scorp_posinc = (data1.Scorp_data['intpaid_posinc'][18] -
                         data1.Scorp_data['intpaid_fin_posinc'][18]) / totalint_exfin
intshare_scorp_neginc = ((data1.Scorp_data['intpaid_total'][18] -
                          data1.Scorp_data['intpaid_fin'][18]) /
                         totalint_exfin - intshare_scorp_posinc)
# Net interest share for sole proprietorships (by income status)
intshare_sp_posinc = (data1.sp_data['mortintpaid_posinc'][16] +
                      data1.sp_data['otherintpaid_posinc'][16] -
                      data1.sp_data['mortintpaid_fin_posinc'][16] -
                      data1.sp_data['otherintpaid_fin_posinc'][16]) / totalint_exfin
intshare_sp_neginc = ((data1.sp_data['mortintpaid'][16] +
                       data1.sp_data['otherintpaid'][16] -
                       data1.sp_data['mortintpaid_fin'][16] -
                       data1.sp_data['otherintpaid_fin'][16]) /
                      totalint_exfin - intshare_sp_posinc)
intshare_partner_posinc = ((data1.partner_data['intpaid_posinc'][19] -
                            data1.partner_data['intpaid_fin_posinc'][19]) /
                           totalint_exfin)
intshare_partner_neginc = ((data1.partner_data['intpaid_total'][19] -
                            data1.partner_data['intpaid_fin_total'][19]) /
                           totalint_exfin - intshare_partner_posinc)

# Save the adjustment factors and pass-through shares
adj_factors = {'param_amt': all_amt_params[0],
               'amt_frac': all_amt_params[1],
               'totaluserate_pymtc': all_amt_params[2],
               'userate_pymtc': all_amt_params[3],
               'trans_amt1': all_amt_params[4],
               'trans_amt2': all_amt_params[5],
               'stock2014': all_amt_params[6],
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
df_adjf.to_csv('adjfactors.csv', index=False)
df_pts = pd.DataFrame({k: [passthru_factors[k]] for k in passthru_factors})
df_pts.to_csv('passthru_shares.csv', index=False)
