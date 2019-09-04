import copy
import numpy as np
import pandas as pd
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS
from biztax.data import Data
from biztax.asset import Asset
from biztax.debt import Debt
from biztax.corptaxreturn import CorpTaxReturn
from biztax.response import Response
from biztax.domesticmne import DomesticMNE


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
        # Create DomesticMNE object
        self.dmne = DomesticMNE(self.btax_params)
        self.dmne.calc_all()
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
        gfacts = earnings_forecast[1:] / earnings_forecast[0]
        # 2013 values for non-modeled revenues
        taxitems = np.array(self.data.corp_tax2013['ALL'])
        receipts = taxitems[4] * gfacts
        rent_inc = taxitems[7] * gfacts
        royalties = taxitems[8] * gfacts
        capgains = (taxitems[9] + taxitems[10] + taxitems[11] - taxitems[32]) * gfacts
        domestic_divs = taxitems[12] * gfacts
        other_recs = taxitems[14] * gfacts
        # 2013 values for non-modeled deductions and credits
        cogs = taxitems[16] * gfacts
        execcomp = taxitems[17] * gfacts
        wages = taxitems[18] * gfacts
        repairs = taxitems[19] * gfacts
        baddebt = taxitems[20] * gfacts
        rent_paid = taxitems[21] * gfacts
        statelocaltax = taxitems[22] * gfacts
        charity = taxitems[24] * gfacts
        amortization = taxitems[25] * gfacts
        depletion = taxitems[27] * gfacts
        advertising = taxitems[28] * gfacts
        pensions = taxitems[29] * gfacts
        benefits = taxitems[30] * gfacts
        sec199_base = taxitems[31] * gfacts
        other_ded = taxitems[33] * gfacts
        gbc = taxitems[42] * gfacts
        # Save unodeled tax items
        self.revenues = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                      'receipts': receipts,
                                      'rent': rent_inc,
                                      'royalties': royalties,
                                      'capgains': capgains,
                                      'domestic_divs': domestic_divs,
                                      'other': other_recs})
        self.deductions = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                        'cogs': cogs,
                                        'execcomp': execcomp,
                                        'wages': wages,
                                        'repairs': repairs,
                                        'baddebt': baddebt,
                                        'rent': rent_paid,
                                        'statelocaltax': statelocaltax,
                                        'charity': charity,
                                        'amortization': amortization,
                                        'depletion': depletion,
                                        'advertising': advertising,
                                        'pensions': pensions,
                                        'benefits': benefits,
                                        'sec199share': sec199_base,
                                        'other': other_ded})
        self.credits = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1),
                                     'gbc': gbc})

    def file_taxes(self):
        """
        Creates the CorpTaxReturn object.
        """
        self.taxreturn = CorpTaxReturn(self.btax_params, self.revenues,
                                       self.deductions, self.credits,
                                       dmne=self.dmne, data=self.data,
                                       assets=self.asset, debts=self.debt)
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

        real_results = pd.DataFrame({'year': range(START_YEAR, END_YEAR + 1)})
        real_results['Earnings'] = (self.revenues['receipts']
                                    + self.revenues['rent']
                                    + self.revenues['royalties']
                                    + self.revenues['capgains']
                                    + self.revenues['domestic_divs']
                                    + self.revenues['other']
                                    - self.deductions['cogs']
                                    - self.deductions['execcomp']
                                    - self.deductions['wages']
                                    - self.deductions['repairs']
                                    - self.deductions['baddebt']
                                    - self.deductions['rent']
                                    - self.deductions['charity']
                                    - self.deductions['depletion']
                                    - self.deductions['advertising']
                                    - self.deductions['pensions']
                                    - self.deductions['benefits']
                                    - self.deductions['other']
                                    + self.dmne.dmne_results['foreign_directinc']
                                    + self.dmne.dmne_results['foreign_indirectinc'])
        real_results['Kstock'] = self.asset.get_forecast()
        real_results['Inv'] = self.asset.get_investment()
        real_results['Depr'] = self.asset.get_truedep()
        real_results['Debt'] = self.debt.get_debt()
        real_results['NIP'] = self.debt.get_nip()
        real_results['Tax'] = self.taxreturn.get_tax()
        real_results['NetInc'] = (real_results['Earnings']
                                  - real_results['Depr']
                                  - real_results['NIP']
                                  - real_results['Tax']
                                  - self.dmne.dmne_results['foreign_tax']
                                  - self.deductions['statelocaltax'])
        real_results['CashFlow'] = (real_results['Earnings']
                                    - real_results['Inv']
                                    - real_results['Tax']
                                    - self.dmne.dmne_results['foreign_tax']
                                    - self.deductions['statelocaltax'])
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

    def update_repatriation(self, responses):
        """
        Updates the DomesticMNE object to include the repatriation response.
        Also updates profits to reflect this response.
        """
        # First, save current foreign earnings
        self.dmne.update_profits(responses.repatriation_response,
                                 responses.shifting_response)
        self.dmne.calc_all()

    def update_earnings(self, responses):
        """
        Recalculates earnings using the old capital stock by asset type, the
        new capital stock by asset type (based on the investment response),
        and the marginal product of capital.
        """
        Kstock_base = copy.deepcopy(self.old_capital_history)
        Kstock_ref = copy.deepcopy(self.asset.capital_history)
        changeEarnings = np.zeros((95, NUM_YEARS))
        for iyr in range(NUM_YEARS):  # for each year
            ystr = str(iyr + START_YEAR)
            mpk = np.array(responses.investment_response['MPKc' + ystr])
            for i in range(95):  # by asset
                changeEarnings[i, iyr] = (Kstock_ref[ystr][i] -
                                          Kstock_base[ystr][i]) * mpk[i]
        deltaE = np.zeros(NUM_YEARS)
        for iyr in range(NUM_YEARS):
            deltaE[iyr] = changeEarnings[:, iyr].sum()
        # Update new earnings
        self.revenues['receipts'] = self.revenues['receipts'] + deltaE

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
        self.update_repatriation(responses)
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
