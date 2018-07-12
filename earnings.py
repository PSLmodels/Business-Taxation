# This file reads earnings from 2013 and advances it to future years
def extend_earnings():
    earnings_forecast = np.asarray(gfactors['profit'])
    earnings2013 = np.asarray(historical_taxdata['ebitda13'])[-1]
    earnings_new = earnings_forecast[1:] / earnings_forecast[0] * earnings2013
    return earnings_new
