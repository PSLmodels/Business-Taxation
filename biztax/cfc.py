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
        self.cfc_data.set_index('Unnamed: 0', inplace=True)
        # Generate earnings
        self.create_earnings()

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
        earnings_2014 = self.cfc_data.loc['ALL', 'earnings']
        subpartF_2014 = self.cfc_data.loc['ALL', 'subpartF']
        assets_2014 = self.cfc_data.loc['ALL', 'assets']
        ppe_2014 = self.cfc_data.loc['ALL', 'ppe']
        # Produce forecast measures
        self.earnings = earnings_2014 * gfacts
        self.subpartF = subpartF_2014 * gfacts
        self.assets = assets_2014 * gfacts
        self.ppe = ppe_2014 * gfacts
        # Extract rates
        self.ftaxrate = self.cfc_data.loc['ALL', 'taxrt']
        # Fraction of current earnings to repatriate
        self.reprate_earnings = self.data.reprate_forecast['repatch_e'] + self.cfc_data.loc['ALL', 'reprate_e']
        # Fraction of previously accumulated earnings to repatriate
        self.reprate_accum = self.data.reprate_forecast['repatch_a'] + self.cfc_data.loc['ALL', 'reprate_a']

    def pay_foreign_taxes(self):
        """
        Determine taxes paid to foreign governments on earnings/profits
        Note: This is constant at the 2014 value.
        Also compute taxable income to be included for GILTI
        """
        # Compute foreign tax liability
        self.foreigntax = self.ftaxrate * self.earnings
        GILTI_inc = np.maximum(self.earnings - self.subpartF
                               - self.ppe
                               * np.asarray(self.btax_params['GILTI_thd']), 0.)
        GILTI_tinc = (GILTI_inc *
                      np.asarray(self.btax_params['GILTI_inclusion']))
        self.GILTI_tinc = GILTI_tinc

    def repatriate_accumulate(self):
        """
        Determine repatriations to US parent company based on current
        profits and accumulated profits.
        Accumulations are only for untaxed profits (i.e. net of
        subpart F and grossed-up dividends).
        """
        # Create arrays for dividends to parent and accumulated profits
        dividends = np.zeros(NUM_YEARS)
        repatriations = np.zeros(NUM_YEARS)
        accum = np.zeros(NUM_YEARS+1)
        accum[0] = self.cfc_data.loc['ALL', 'accum']
        # Compute dividend repatriations to parent company from earnings
        dividends = (self.earnings - self.foreigntax
                     - self.subpartF) * self.reprate_earnings
        for i in range(NUM_YEARS):
            # Compute new accumulated profits
            accum[i+1] = (accum[i] + self.earnings[i] - self.subpartF[i]
                          - repatriations[i]
                          - dividends[i] * (1 + self.ftaxrate))
        # Repatriations from accumulated untaxed profits
        repatriations = self.reprate_accum * accum[:NUM_YEARS]
        self.dividends = dividends
        self.repatriations = repatriations
        self.accumulated_profits = accum[1:]

    def calc_all(self):
        """
        Run all calculations
        """
        self.pay_foreign_taxes()
        self.repatriate_accumulate()
        # Add certain results to policy DataFrame
        self.btax_params['ftaxrate'] = self.ftaxrate
        self.btax_params['reprate_e'] = self.reprate_earnings

    def update_cfc(self, update_df, shift_response=None):
        """
        Updates the forecast for the repatriation rates.
        Then calls calc_all() using the new repatriation decisions.

        update_df should be a DataFrame object with columns
        [year, reprate_e, reprate_a]
        shift_response is array of income shifted between
        nondeferred foreign source and CFC
        """
        assert isinstance(update_df, pd.DataFrame)
        assert len(update_df) == NUM_YEARS
        if 'reprate_e' in update_df:
            # Update repatriation rate on current earnings
            reprate_e = np.minimum(np.maximum(self.reprate_earnings + update_df['reprate_e'],
                                              0.), 1.)
            self.reprate_earnings = reprate_e
        if 'reprate_a' in update_df:
            # Update repatriation rate on accumulated profits (if built)
            self.reprate_accum = self.reprate_accum + update_df['reprate_a']
        if shift_response is not None:
            # Update earnings
            self.earnings = self.earnings + shift_response
