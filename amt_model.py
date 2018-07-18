
def calcAMTparams2():
    """
    Calculates the adjustment factors for the AMT and PYMTC
    """
    # Grab historical data
    hist_data = copy.deepcopy(historical_combined)
    taxinc = np.array(hist_data['taxinc'])
    amt = np.array(hist_data['amt'])
    pymtc = np.array(hist_data['pymtc'])
    stock = np.zeros(len(amt))
    stock[15] = 26.0
    tau_a = 0.2
    tau_c = 0.347
    # Expand model backward based on defined value of stock[15]
    for i in range(15):
        stock[14-i] = stock[15-i] + pymtc[14-i] - amt[14-i]
    eta = sum([pymtc[i] / stock[i] for i in range(16)]) / 16.
    A_over_TI = sum([amt[i] / taxinc[i] for i in range(16)]) / 16.
    # Calculate solution to AMT parameter

    def amterr(lam):
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


def AMTmodel(taxinc, amt_rates=btax_defaults['tau_amt'],
             ctax_rates=btax_defaults['tau_c'],
             pymtc_status=np.zeros(14)):
    """
    Calculates the AMT revenue and PYMTC for 2014-2027
    pymtc_status: 0 for no change, 1 for repeal, 2 for refundable
    """
    assert len(amt_rates) == 14
    assert len(ctax_rates) == 14
    assert len(pymtc_status) == 14
    assert len(taxinc) == 14
    for x in pymtc_status:
        assert x in [0, 1, 2]
    A = np.zeros(14)
    P = np.zeros(14)
    stockA = np.zeros(15)
    stockN = np.zeros(15)
    stockA[0] = ((trans_amt1 * userate_pymtc + trans_amt2 *
                  (1 - userate_pymtc)) / (1 - trans_amt1) * stock2014)
    stockN[0] = stock2014 - stockN[0]
    stockN[0] = (1 - trans_amt1) / (1 - trans_amt1 + trans_amt1 *
                                    userate_pymtc + trans_amt2 *
                                    (1 - userate_pymtc)) * stock2014
    stockA[0] = stock2014 - stockN[0]
    for i in range(14):
        # Calculate AMT
        if amt_rates[i] == 0.:
            # If no AMT
            A[i] = 0.
            frac_amt = 0.
        elif ctax_rates[i] <= amt_rates[i]:
            # If AMT rate exceeds regular rate (all subject to AMT)
            A[i] = ((amt_rates[i] - ctax_rates[i] + amt_rates[i] / param_amt) *
                    taxinc[i])
            frac_amt = 1.
        else:
            A[i] = (amt_rates[i] / param_amt *
                    np.exp(-param_amt * (ctax_rates[i] / amt_rates[i] - 1)) *
                    taxinc[i])
            frac_amt = np.exp(-param_amt * (ctax_rates[i] / amt_rates[i] - 1))
        # Adjust transition params for change in AMT frequency
        alpha = trans_amt1 * frac_amt / amt_frac
        beta = trans_amt2 * frac_amt / amt_frac
        if pymtc_status[i] == 0:
            # No change from baseline
            userate = userate_pymtc
        elif pymtc_status[i] == 1:
            # PYMTC repealed
            userate = 0.0
        else:
            # PYMTC made fully refundable
            userate = 1.0
        P[i] = userate * stockN[i]
        stockA[i+1] = (trans_amt1 * (stockA[i] + A[i]) +
                       trans_amt2 * (stockN[i] - P[i]))
        stockN[i+1] = ((1 - trans_amt1) * (stockA[i] + A[i]) +
                       (1 - trans_amt2) * (stockN[i] - P[i]))
    # Rescale for any cross-sector shifting
    amt_final = A * rescale_corp
    pymtc_final = P * rescale_corp
    AMT_results = pd.DataFrame({'year': range(2014, 2028),
                                'amt': amt_final, 'pymtc': pymtc_final,
                                'stockA': stockA[:14], 'stockN': stockN[:14]})
    return AMT_results
