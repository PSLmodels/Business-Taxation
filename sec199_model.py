def sec199(s199_hc=0.0, s199_hc_year=9e99):
    # s199_hc, s199_hc_year: haircut on Sec. 199 deductions taken beginning
    #                        in s199_hc_year
    profit = sec199_data['profit'].tolist()
    sec199 = sec199_data['sec199'][:9].tolist()
    for i in range(9,23):
        sec199.append(sec199[i-1] * profit[i] / profit[i-1])
        if i + 2005 >= s199_hc_year:
            sec199[i] = sec199[i] * (1 - s199_hc)
    sec199_final = np.asarray(sec199[9:]) * rescale_corp
    sec199_results = pd.DataFrame({'year': range(2014,2028),
                                   'sec199': sec199_final})
    return sec199_results
