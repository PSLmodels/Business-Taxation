def sec199(s199_hc=0.0, s199_hc_year=9e99):
    """
    Calculates the Section 199 deduction for each year 2014-2027.
    Parameters:
        s199_hc, s199_hc_year: haircut on Sec. 199 deductions taken beginning
                               in s199_hc_year
    """
    profit = np.asarray(gfactors['profit_d'])
    sec199_res = np.zeros(14)
    sec199_2013 = np.asarray(historical_taxdata['sec199'])[-1]
    for i in range(14):
        sec199_res[i] = profit[i+1] / profit[0] * sec199_2013
        if i + 2014 >= s199_hc_year:
            sec199_res[i] = sec199_res[i] * (1 - s199_hc)
    return sec199_res
