import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.response import Response


class CFC():
    """
    Constructor for the CFC class (controlled foreign corporations).
    This contains both the real and tax information relevant to the
    corporate income tax.
    """

    def __init__(self, btax_params, data=None):
        # Store policy parameter objects
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        # Create Data object
        if isinstance(data, Data):
            self.data = data
        else:
            self.data = Data()
        # Extract baseline forecast for earnings and action
        self.cfc_data = copy.deepcopy(self.data.cfc_data)

    def create_earnings(self):
        """
        Forecast growth of foreign earnings/profits
        Note: 2013 value is set to produce actual 2014 value after growth factor.
        """
        earnings_forecast = np.asarray(self.data.gfactors['profit_f'])
        earnings2014 = np.asarray(self.cfc_data['earnings'])[0]
        earnings_new = (earnings_forecast[1:] / earnings_forecast[1]
                        * earnings2014)
        self.earnings = earnings_new

    def pay_foreign_taxes(self):
        """
        Determine taxes paid to foreign governments on earnings/profits
        Note: This is constant at the 2014 value.
        """
        ftaxrate = np.asarray(self.cfc_data['taxrt'])
        self.foreigntax = ftaxrate * self.earnings

    def repatriate_accumulate(self):
        """
        Determine repatriations to US parent company based on current
        profits and accumulated profits.
        Note: 
        """
        # Fraction of current earnings to repatriate
        reprate_earnings = np.asarray(self.cfc_data['reprate_e'])
        # Fraction of previously accumulated earnings to repatriate
        reprate_accum = np.asarray(self.cfc_data['reprate_a'])
        # Create arrays for dividends to parent and accumulated profits
        dividends = np.zeros(14)
        accum = np.zeros(15)
        accum[0] = np.asarray(self.cfc_data['accum'])[0]
        for i in range(14):
            # Compute dividend repatriations to parent company
            dividends[i] = (reprate_earnings[i] * (self.earnings[i] - self.foreigntax[i])
                            + reprate_accum[i] * accum[i])
            # Compute new accumulated profits
            accum[i+1] = accum[i] + self.earnings[i] - self.foreigntax[i] - dividends[i]
        self.dividends = dividends
        self.accumulated_profits = accum[1:]

    def calc_all(self):
        """
        Run all calculations
        """
        self.create_earnings()
        self.pay_foreign_taxes()
        self.repatriate_accumulate()

    def update_cfc(self, update_df):
        """
        Updates the forecast for the repatriation rates.
        Then calls calc_all() using the new repatriation decisions.

        update_df should be a DataFrame object with columns
        [year, reprate_e, reprate_a]
        and years 2014:2028
        """
        assert isinstance(update_df, pd.DataFrame)
        assert len(update_df) == 14
        reprate_e = np.asarray(self.cfc_data['reprate_e'])
        if 'reprate_e' in update_df:
            # Update repatriation rate on current earnings
            reprate_e = np.minimum(np.maximum(reprate_e + update_df['reprate_e'], 0), 1.)
            self.cfc_data['reprate_e'] = reprate_e
        if 'reprate_a' in update_df:
            # Update repatriation rate on accumulated profits (if built)
            self.cfc_data['reprate_e'] = self.cfc_data['reprate_e']




