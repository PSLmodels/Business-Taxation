def calcWAvgTaxRate(year):
    assert year in range(1995,2028)
    year = min(year, 2016)
    gdp_list = np.asarray(ftc_gdp_data[str(year)])
    taxrate_list = np.asarray(ftc_taxrates_data[str(year)])
    # remove observations with missing data
    taxrate_list2 = np.where(np.isnan(taxrate_list), 0, taxrate_list)
    gdp_list2 = np.where(np.isnan(taxrate_list), 0, gdp_list)
    avgrate = sum(taxrate_list2 * gdp_list2) / sum(gdp_list2)
    return avgrate

def calcFTCAdjustment():
    ftc_actual = np.asarray(ftc_other_data['F'][:19])
    profits = np.asarray(ftc_other_data['C_total'][:19])
    profits_d = np.asarray(ftc_other_data['C_domestic'][:19])
    profits_f = profits - profits_d
    tax_f = []
    for i in range(1995,2014):
        tax_f.append(calcWAvgTaxRate(i))
    ftc_gross = profits_f * tax_f / 100.
    adjfactor = sum(ftc_actual / ftc_gross) / 19.
    return adjfactor
adjfactor_ftc_corp = calcFTCAdjustment()

def FTC_model(haircut=0.0, haircut_year = 9e99):
    profits = np.asarray(ftc_other_data['C_total'][19:])
    profits_d = np.asarray(ftc_other_data['C_domestic'][19:])
    tax_f = np.zeros(14)
    hc_applied = np.zeros(14)
    for i in range(14):
        tax_f[i] = calcWAvgTaxRate(i + 2014)
        if i + 2014 >= haircut_year:
            hc_applied = haircut
    ftc_semif = ((profits - profits_d) * tax_f / 100. * adjfactor_ftc_corp *
                 (1 - hc_applied))
    ftc_final = ftc_semif * rescale_corp
    ftc_results = pd.DataFrame({'year': range(2014,2028), 'ftc': ftc_final})
    return ftc_results
