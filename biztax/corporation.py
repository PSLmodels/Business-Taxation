import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.asset import Asset
from biztax.debt import Debt
from biztax.corptaxreturn import CorpTaxReturn
from biztax.response import Response


class Corporation():
    """
    Constructor for the Corporation class.
    This contains both the real and tax information relevant to the
    corporate income tax.
    """

    def __init__(self, btax_params):
        # Store policy parameter objects
        if isinstance(btax_params, pd.DataFrame):
            self.btax_params = btax_params
        else:
            raise ValueError('btax_params must be DataFrame')
        # Create Data object
        self.data = Data()
        # Create Asset object and calculate
        self.asset = Asset(self.btax_params, corp=True, data=self.data)
        self.asset.calc_all()
        # Create earnings forecast
        self.create_earnings()

    def create_debt(self):
        """
        Creates the Debt object for the Corporation.
        Note: create_asset must have already been called
        """
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, corp=True)
        self.debt.calc_all()

    def create_earnings(self):
        """
        Creates the initial forecast for earnings. Static only.
        """
        # Grab forecasts of profit growth
        earnings_forecast = np.asarray(self.data.gfactors['profit'])
        # 2013 value for earnings (total)
        earnings13 = np.asarray(self.data.historical_taxdata['ebitda13'])[-1]
        # 2013 value for dividends received from foreign corporations
        foreign_divs13 = np.asarray(self.data.historical_taxdata['foreign_divs'])[-1]
        # 2013 value for foreign taxes gross-up
        foreign_tax13 = np.asarray(self.data.historical_taxdata['foreign_tax'])[-1]
        # 2013 value for other foreign income
        foreign_othinc13 = np.asarray(self.data.historical_taxdata['foreign_other'])[-1]
        # Compute domestic earnings for 2013
        domestic_inc13 = earnings13 - foreign_divs13 - foreign_tax13 - foreign_othinc13
        # Forecast new domestic earnings
        domestic_new = (earnings_forecast[1:] / earnings_forecast[0] * domestic_inc13)
        # Forecast new foreign earnings components
        foreign_div_new = (earnings_forecast[1:] / earnings_forecast[0] * foreign_divs13)
        foreign_tax_new = (earnings_forecast[1:] / earnings_forecast[0] * foreign_tax13)
        foreign_othinc_new = (earnings_forecast[1:] / earnings_forecast[0] * foreign_othinc13)
        # Compute earnings
        self.earnings = domestic_new + foreign_div_new + foreign_tax_new + foreign_othinc_new
        # Get foreign income exclusion parameters
        foreign_div_tinc = foreign_div_new * np.asarray(self.btax_params['foreign_dividend_inclusion'])
        foreign_tax_tinc = foreign_tax_new * np.asarray(self.btax_params['foreign_tax_grossrt'])
        foreign_othinc_tinc = foreign_othinc_new * np.asarray(self.btax_params['foreign_othinc_inclusion'])
        self.taxearnings = domestic_new + foreign_div_tinc + foreign_tax_tinc + foreign_othinc_tinc

    def file_taxes(self):
        """
        Creates the CorpTaxReturn object.
        """
        self.taxreturn = CorpTaxReturn(self.btax_params, self.taxearnings,
                                       data=self.data, assets=self.asset,
                                       debts=self.debt)
        self.taxreturn.calc_all()

    def real_activity(self):
        """
        Produces a DataFrame of the corporation's real activity.
        Real measures are:
            Capital stock
            Investment
            Depreciation (economic)
            Net debt
            Net interest paid
            Earnings
            Tax liability
            Net income
            Cash flow
        """
        real_results = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                     'Earnings': self.earnings})
        real_results['Kstock'] = self.asset.get_forecast()
        real_results['Inv'] = self.asset.get_investment()
        real_results['Depr'] = self.asset.get_truedep()
        real_results['Debt'] = self.debt.get_debt()
        real_results['NIP'] = self.debt.get_nip()
        real_results['Tax'] = self.taxreturn.get_tax()
        real_results['NetInc'] = (real_results['Earnings']
                                  - real_results['Depr']
                                  - real_results['NIP']
                                  - real_results['Tax'])
        real_results['CashFlow'] = (real_results['Earnings']
                                    - real_results['Inv']
                                    - real_results['Tax'])
        self.real_results = real_results

    def calc_static(self):
        """
        Runs the static calculations.
        """
        self.create_debt()
        self.file_taxes()
        self.real_activity()

    def update_legal(self, responses):
        """
        Updates the rescale_corp and rescale_noncorp associated with each
        Data associated with each object.
        """
        self.data.update_rescaling(responses.rescale_corp,
                                   responses.rescale_noncorp)
        self.asset.data.update_rescaling(responses.rescale_corp,
                                         responses.rescale_noncorp)

    def update_investment(self, responses):
        """
        Updates the Asset object to include investment response.
        """
        # First, save the capital stock by asset type and year (for earnings)
        self.old_capital_history = copy.deepcopy(self.asset.capital_history)
        self.asset.update_response(responses.investment_response)
        self.asset.calc_all()

    def update_earnings(self, responses):
        """
        Recalculates earnings using the old capital stock by asset type, the
        new capital stock by asset type (based on the investment response),
        and the marginal product of capital.
        """
        Kstock_base = copy.deepcopy(self.old_capital_history)
        Kstock_ref = copy.deepcopy(self.asset.capital_history)
        deltaK = Kstock_ref - Kstock_base
        changeEarnings = np.zeros((96, NUM_YEARS))
        for iyr in range(NUM_YEARS):  # for each year
            ystr = str(iyr + START_YEAR)
            mpk = np.array(responses.investment_response['MPKc' + ystr])
            for i in range(96):  # by asset
                changeEarnings[i, iyr] = (deltaK[i, iyr] * mpk[i]
                                          * self.data.adjfactor_dep_corp)
        deltaE = np.zeros(NUM_YEARS)
        for iyr in range(NUM_YEARS):
            deltaE[iyr] = changeEarnings[:, iyr].sum()
        self.earnings = (self.earnings + deltaE) * self.data.rescale_corp

    def update_debt(self, responses):
        """
        Replaces the Debt object to use the new asset forecast and Data
        """
        pctch_delta = np.array(responses.debt_response['pchDelta_corp'])
        self.debt = Debt(self.btax_params, self.asset.get_forecast(),
                         data=self.data, response=pctch_delta, corp=True)
        self.debt.calc_all()

    def apply_responses(self, responses):
        """
        Updates Data, Asset, earnings, Debt and CorpTaxReturn to include
        responses. Then calc_all() for each object.
        """
        assert isinstance(responses, Response)
        self.update_legal(responses)
        self.update_investment(responses)
        self.update_earnings(responses)
        self.update_debt(responses)
        self.file_taxes()
        self.real_activity()

    def get_netinc(self):
        """
        Returns an array of the corporation's net income (after-tax).
        """
        netinc = np.array(self.real_results['NetInc'])
        return netinc

    def get_taxrev(self):
        """
        Returns an array of the corporation's tax liability.
        """
        taxrev = np.array(self.real_results['Tax'])
        return taxrev
