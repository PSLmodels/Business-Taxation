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
        Forecast growth of foreign earnings/profits.
        Also forecasts growth of total assets and net PPE using
        the same growth factors.
        """
        # Get growth factors for foreign activity
        earnings_forecast = np.asarray(self.data.gfactors['profit_f'])
        gfacts = earnings_forecast[1:] / earnings_forecast[1]
        # Get real activity information for 2014
        earnings_2014 = np.asarray(self.cfc_data['earnings'])[0]
        subpartF_2014 = np.asarray(self.cfc_data['subpartF'])[0]
        assets_2014 = np.asarray(self.cfc_data['assets'])[0]
        ppe_2014 = np.asarray(self.cfc_data['ppe'])[0]
        # Produce forecast measures
        self.earnings = earnings_2014 * gfacts
        self.subpartF = subpartF_2014 * gfacts
        self.assets = assets_2014 * gfacts
        self.ppe = ppe_2014 * gfacts

    def pay_foreign_taxes(self):
        """
        Determine taxes paid to foreign governments on earnings/profits
        Note: This is constant at the 2014 value.
        Also compute taxable income to be included for GILTI
        """
        # Compute foreign tax liability
        self.ftaxrate = np.asarray(self.cfc_data['taxrt'])
        self.foreigntax = self.ftaxrate * self.earnings
        GILTI_inc = (self.earnings - self.subpartF
                     - self.ppe * np.asarray(self.btax_params['GILTI_thd']))
        GILTI_tinc = GILTI_inc * np.asarray(self.btax_params['cfcinc_inclusion'])
        self.GILTI_tinc = GILTI_tinc

    def repatriate_accumulate(self):
        """
        Determine repatriations to US parent company based on current
        profits and accumulated profits.
        Accumulations are only for untaxed profits (i.e. net of
        subpart F and grossed-up dividends).
        """
        # Fraction of current earnings to repatriate
        reprate_earnings = np.asarray(self.cfc_data['reprate_e'])
        # Fraction of previously accumulated earnings to repatriate
        reprate_accum = np.asarray(self.cfc_data['reprate_a'])
        # Create arrays for dividends to parent and accumulated profits
        dividends = np.zeros(14)
        repatriations = np.zeros(14)
        accum = np.zeros(15)
        accum[0] = np.asarray(self.cfc_data['accum'])[0]
        for i in range(14):
            # Compute dividend repatriations to parent company from earnings
            dividends[i] = (self.earnings[i] - self.foreigntax[i]
                            - self.subpartF[i]) * reprate_earnings[i]
            # Repatriations from accumulated untaxed profits
            repatriations[i] = reprate_accum[i] * accum[i]
            # Compute new accumulated profits
            accum[i+1] = (accum[i] + self.earnings[i] - self.subpartF[i]
                          - repatriations[i] - dividends[i] * (1 + self.ftaxrate[i]))
        self.dividends = dividends
        self.repatriations = repatriations
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




