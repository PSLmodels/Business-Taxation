def gbc():
    profit = np.asarray(gfactors['profit_d'])
    gbc_2013 = np.asarray(historical_taxdata['gbc'])[-1]
    gbc_res = profit[1:] / profit[0] * gbc_2013
    return gbc_res
